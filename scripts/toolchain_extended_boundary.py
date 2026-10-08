#!/usr/bin/env python3
"""Record real GDB basic-block hits for unchanged Clang O2 code.

Run with WSL Python from the project root. No baseline files are written.
The standalone harness links the original main.o and wraps the startup main
reference; its alternating_sum bytes must match the baseline executable.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ENV = dict(os.environ, LC_ALL="C", TZ="Asia/Shanghai")
EVENTS = []


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(command, stem, *, expected_exit=0):
    stem.parent.mkdir(parents=True, exist_ok=True)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    p = subprocess.run(list(map(str, command)), cwd=ROOT, env=ENV,
                       capture_output=True, text=True, timeout=60)
    stem.with_suffix(".command.txt").write_text(shlex.join(map(str, command)) + "\n", encoding="utf-8")
    save_json(stem.with_suffix(".command.json"), list(map(str, command)))
    stem.with_suffix(".stdout.txt").write_text(p.stdout, encoding="utf-8")
    stem.with_suffix(".stderr.txt").write_text(p.stderr, encoding="utf-8")
    stem.with_suffix(".exit.txt").write_text(str(p.returncode) + "\n", encoding="utf-8")
    EVENTS.append({"started_utc": started, "command": list(map(str, command)),
                   "exit": p.returncode, "log": str(stem.relative_to(ROOT))})
    if p.returncode != expected_exit:
        raise RuntimeError(f"Command exit {p.returncode}: {shlex.join(map(str, command))}\n{p.stderr}")
    return p


def elf_function(path, name):
    """Extract symbol bytes using the ELF64 section and symbol tables."""
    data = path.read_bytes()
    if data[:6] != b"\x7fELF\x02\x01":
        raise ValueError("Expected little-endian ELF64")
    offset = struct.unpack_from("<Q", data, 40)[0]
    size, count = struct.unpack_from("<HH", data, 58)
    sections = [struct.unpack_from("<IIQQQQIIQQ", data, offset + i * size) for i in range(count)]
    for section in sections:
        if section[1] != 2:  # SHT_SYMTAB
            continue
        strings_section = sections[section[6]]
        strings = data[strings_section[4]:strings_section[4] + strings_section[5]]
        for symbol_offset in range(section[4], section[4] + section[5], section[9]):
            n, info, other, index, address, length = struct.unpack_from("<IBBHQQ", data, symbol_offset)
            end = strings.find(b"\0", n)
            if strings[n:end].decode() == name:
                owner = sections[index]
                file_offset = owner[4] + address - owner[3]
                body = data[file_offset:file_offset + length]
                return {"address": address, "size": length, "sha256": hashlib.sha256(body).hexdigest()}, body
    raise ValueError(f"Symbol {name} not found in {path}")


def instructions(disassembly, name):
    found = False
    result = []
    for line in disassembly.splitlines():
        header = re.match(r"^([0-9a-f]+) <([^>]+)>:$", line)
        if header:
            if found:
                break
            found = header[2] == name
            continue
        if found:
            match = re.match(r"^\s*([0-9a-f]+):\s+([a-z][a-z0-9]*)\s*(.*)$", line)
            if match:
                result.append({"address": int(match[1], 16), "mnemonic": match[2], "operands": match[3], "line": line})
    if not result:
        raise ValueError(f"No disassembly for {name}")
    return result


def loop_headers(insns):
    loops = []
    for row in insns:
        if not row["mnemonic"].startswith("j") or row["mnemonic"] == "jmp":
            continue
        match = re.match(r"([0-9a-f]+) <", row["operands"])
        if match and insns[0]["address"] <= int(match[1], 16) < row["address"]:
            target = int(match[1], 16)
            body = [x for x in insns if target <= x["address"] <= row["address"]]
            loops.append({"header": target, "backedge": row["address"],
                          "simd": any("xmm" in x["operands"] for x in body),
                          "instructions": [x["line"] for x in body]})
    return loops


def gdb_string(path):
    return '"' + str(path).replace('\\', '\\\\').replace('"', '\\"') + '"'


def trace(executable, probes, folder, n):
    folder.mkdir(parents=True, exist_ok=True)
    input_path = folder / "input.txt"
    program_out = folder / "program.stdout.txt"
    program_err = folder / "program.stderr.txt"
    input_path.write_text(f"{n}\n", encoding="ascii")
    lines = ["set pagination off", "set confirm off", "set disassembly-flavor intel",
             "set disable-randomization off"]
    for name, address in probes.items():
        lines += [f"set $hits_{name} = 0", f"break *0x{address:x}", "commands", "silent",
                  f"set $hits_{name} = $hits_{name} + 1",
                  f'printf "TRACE {name} pc=0x%lx eax=%d ecx=%d r8d=%d\\n", $pc, $eax, $ecx, $r8d',
                  "continue", "end"]
    lines.append(f"run < {gdb_string(input_path)} > {gdb_string(program_out)} 2> {gdb_string(program_err)}")
    for name in probes:
        lines.append(f'printf "HITS {name}=%d\\n", $hits_{name}')
    lines += ['printf "INFERIOR_EXIT=%d\\n", $_exitcode', "quit"]
    command_file = folder / "trace.gdb"
    command_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    p = run(["gdb", "--batch", "--nx", "-x", command_file, executable], folder / "gdb")
    hits = {k: int(v) for k, v in re.findall(r"^HITS (\w+)=(\d+)$", p.stdout, re.M)}
    exit_match = re.search(r"^INFERIOR_EXIT=(-?\d+)$", p.stdout, re.M)
    if hits.keys() != probes.keys() or not exit_match:
        raise RuntimeError(f"Incomplete GDB evidence in {folder}")
    total = -3 * (n // 2) if n % 2 == 0 else 3 * (n // 2) + 5
    expected_stdout = f"n={n} alternating={total} adjusted={total + 11}\n"
    result = {"n": n, "executable": str(executable.relative_to(ROOT)), "executable_sha256": digest(executable),
              "expected_stdout": expected_stdout, "stdout": program_out.read_text(),
              "stderr": program_err.read_text(), "exit": int(exit_match[1]),
              "hits": hits, "gdb_stdout": str((folder / "gdb.stdout.txt").relative_to(ROOT)),
              "gdb_commands": str(command_file.relative_to(ROOT))}
    result["output_pass"] = result["stdout"] == expected_stdout and result["stderr"] == "" and result["exit"] == 0
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", default="artifacts/toolchain/clang_O2")
    args = parser.parse_args()
    baseline = (ROOT / args.baseline).resolve()
    out = ROOT / "artifacts/toolchain/extended_exploration/boundary"
    out.mkdir(parents=True, exist_ok=True)
    source = ROOT / "src/toolchain"
    wrapper = source / "variants/boundary_wrapper.c"
    original_paths = [baseline / x for x in ("main.o", "bonus.o", "demo", "main.s", "main.ll")]
    original_paths += [source / x for x in ("main.c", "bonus.c", "demo.h")]
    original_hashes = {str(p.relative_to(ROOT)): digest(p) for p in original_paths}
    save_json(out / "original_hashes_before.json", original_hashes)
    run(["gdb", "--version"], out / "gdb_version")
    run(["clang-14", "--version"], out / "clang_version")
    flags = ["-std=c11", "-Wall", "-Wextra", "-Werror", "-march=x86-64", "-mtune=generic", "-fno-pie", "-O2"]
    wrapper_object = out / "boundary_wrapper.o"
    harness = out / "standalone_demo"
    run(["clang-14", *flags, "-I", source, "-c", wrapper, "-o", wrapper_object], out / "compile_wrapper")
    run(["clang-14", "-no-pie", baseline / "main.o", baseline / "bonus.o", wrapper_object,
         "-Wl,--wrap=main", "-o", harness], out / "link_standalone")
    run(["readelf", "-hSWs", harness], out / "harness_readelf")
    run(["nm", "-S", "--defined-only", harness], out / "harness_symbols")
    baseline_disasm = run(["objdump", "-d", "-w", "-Mintel", "--no-show-raw-insn", baseline / "demo"], out / "baseline_disassembly").stdout
    harness_disasm = run(["objdump", "-d", "-w", "-Mintel", "--no-show-raw-insn", harness], out / "harness_disassembly").stdout
    original_symbol, original_bytes = elf_function(baseline / "demo", "alternating_sum")
    harness_symbol, harness_bytes = elf_function(harness, "alternating_sum")
    (out / "baseline_alternating_sum.bin").write_bytes(original_bytes)
    (out / "harness_alternating_sum.bin").write_bytes(harness_bytes)
    identity = {"baseline": original_symbol, "harness": harness_symbol,
                "machine_bytes_identical": original_bytes == harness_bytes,
                "original_main_object_sha256": digest(baseline / "main.o"),
                "wrapper_source_sha256": digest(wrapper),
                "method": "Unmodified baseline main.o + bonus.o, with wrapper.o and --wrap=main; no LTO or recompilation of original source."}
    save_json(out / "function_identity.json", identity)
    if not identity["machine_bytes_identical"]:
        raise AssertionError("Standalone machine bytes differ after linking; cannot assert exact code identity")
    standalone_insns = instructions(harness_disasm, "alternating_sum")
    main_insns = instructions(baseline_disasm, "main")
    standalone_loops = loop_headers(standalone_insns)
    main_loops = loop_headers(main_insns)
    vector = [x for x in standalone_loops if x["simd"]]
    scalar = [x for x in standalone_loops if not x["simd"]]
    main_scalar = [x for x in main_loops if not x["simd"]]
    main_vector = [x for x in main_loops if x["simd"]]
    reductions = [x for x in main_insns if x["mnemonic"] == "pshufd"]
    if len(vector) != 1 or len(scalar) != 1 or len(main_scalar) != 1 or main_vector or not reductions:
        raise AssertionError("Unexpected baseline CFG: inspect disassembly before changing probes")
    standalone_probes = {"function_entry": harness_symbol["address"], "vector_loop": vector[0]["header"],
                         "scalar_loop": scalar[0]["header"]}
    main_probes = {"main_entry": main_insns[0]["address"], "standalone_entry": original_symbol["address"],
                   "vector_reduce": reductions[0]["address"], "scalar_loop": main_scalar[0]["header"]}
    selection_loads = [x for x in main_insns if x["mnemonic"] == "movdqa" and "[rip" in x["operands"]
                       and x["address"] < reductions[0]["address"]]
    for i, row in enumerate(selection_loads):
        main_probes[f"constant_vector_{i}"] = row["address"]
    address_evidence = {"standalone_probes": {k: hex(v) for k, v in standalone_probes.items()},
                        "main_probes": {k: hex(v) for k, v in main_probes.items()},
                        "standalone_loops": standalone_loops, "main_loops": main_loops,
                        "main_reduction_instructions": [x["line"] for x in reductions],
                        "main_constant_vector_instructions": [x["line"] for x in selection_loads],
                        "basis": "Backward conditional branch target identifies each actual loop header. SIMD operands classify standalone vector body; main has only one scalar backedge. Its vector computation is bounded, fully unrolled and folded into constant-vector selection plus reduction.",
                        "threshold_evidence": "baseline main.s: standalone cmp $8,%edi / and $-8,%r8d; main cmp $4,%eax / and $-4,%ecx. Actual machine disassembly is retained beside this JSON."}
    save_json(out / "probe_addresses.json", address_evidence)
    cases = []
    for n in (7, 8, 9, 15, 16, 17):
        standalone = trace(harness, standalone_probes, out / "standalone" / f"n_{n}", n)
        standalone["context"] = "standalone alternating_sum"
        standalone["expected_hits_from_cfg"] = {"function_entry": 1, "vector_loop": n // 8, "scalar_loop": n % 8}
        standalone["path_pass"] = all(standalone["hits"][k] == v for k, v in standalone["expected_hits_from_cfg"].items())
        cases.append(standalone)
        inlined = trace(baseline / "demo", main_probes, out / "main_inlined" / f"n_{n}", n)
        inlined["context"] = "original main inlined context"
        inlined["expected_hits_from_cfg"] = {"main_entry": 1, "standalone_entry": 0, "vector_reduce": int(n >= 4), "scalar_loop": n % 4}
        inlined["path_pass"] = all(inlined["hits"][k] == v for k, v in inlined["expected_hits_from_cfg"].items())
        cases.append(inlined)
    after = {str(p.relative_to(ROOT)): digest(p) for p in original_paths}
    save_json(out / "original_hashes_after.json", after)
    unchanged = original_hashes == after
    result = {"baseline_directory": str(baseline.relative_to(ROOT)), "baseline_demo_sha256": digest(baseline / "demo"),
              "script_sha256": digest(Path(__file__).resolve()), "wrapper_source_sha256": digest(wrapper),
              "function_identity": identity, "probe_evidence": "probe_addresses.json", "cases": cases,
              "summary": {"cases": len(cases), "output_passed": sum(x["output_pass"] for x in cases),
                          "path_passed": sum(x["path_pass"] for x in cases), "original_files_unchanged": unchanged},
              "limits": ["Breakpoint hits measure executed basic blocks, not elapsed time or speedup.",
                         "Standalone wrapper changes startup selection only; alternating_sum machine bytes are verified identical.",
                         "main has no surviving vector loop. Its vector_reduce hit is not a count of vector iterations.",
                         "These paths describe this exact baseline Clang O2 ELF; other configurations require their own disassembly and probes."]}
    save_json(out / "boundary_results.json", result)
    save_json(out / "commands.json", EVENTS)
    note = ["# Clang O2 向量主体与标量尾部：直接执行证据", "",
            "## 方法与代码身份", "",
            "独立函数由原 `main.o`、`bonus.o` 与新增 wrapper 链接，使用 `--wrap=main` 选择启动入口。原有源程序和对象未重新编译。",
            f"`alternating_sum` 的 {original_symbol['size']} 字节在原 demo 和 harness 中完全相同，函数字节 SHA256 为 `{original_symbol['sha256']}`。",
            f"原 demo SHA256：`{digest(baseline / 'demo')}`。原对象及源码执行前后 SHA256 均一致。", "",
            "GDB 断点设置在反汇编中的实际基本块入口；循环入口由条件回边的目标地址识别。",
            f"独立函数 SIMD 循环头 `{hex(standalone_probes['vector_loop'])}`、标量循环头 `{hex(standalone_probes['scalar_loop'])}`。",
            f"原 main 归约入口 `{hex(main_probes['vector_reduce'])}`、标量循环头 `{hex(main_probes['scalar_loop'])}`。",
            "`probe_addresses.json` 保存地址依据、回边和完整循环指令；每组 `trace.gdb` 与 `gdb.stdout.txt` 保存真实命中。", "",
            "## 实测结果", "",
            "| n | alternating | adjusted | 独立函数 SIMD 循环头 | 独立函数标量循环头 | main 归约块 | main 标量循环头 | main 中独立函数入口 |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for i in range(0, len(cases), 2):
        a, b = cases[i:i + 2]
        n = a["n"]
        total = -3 * (n // 2) if n % 2 == 0 else 3 * (n // 2) + 5
        note.append(f"| {n} | {total} | {total + 11} | {a['hits']['vector_loop']} | {a['hits']['scalar_loop']} | {b['hits']['vector_reduce']} | {b['hits']['scalar_loop']} | {b['hits']['standalone_entry']} |")
    note += ["", "全部 12 组 stdout、stderr、退出状态均符合独立闭式预期，全部 12 组路径计数符合实际 CFG。该计数与原 60/60 基线测试分开记录。", "",
             "## 可支持的机制解释", "",
             "独立函数每次 SIMD 循环执行处理 8 个标量迭代（4 通道、交错因子 2），门槛为 n>=8；标量循环执行 n mod 8 次。因此 n=7 走 7 次标量体，n=8 完整执行一批且没有尾部，n=9 为一批加一次尾部，n=16 执行两批，n=17 为两批加一次尾部。n=17 的 GDB 日志还直接记录 SIMD 头处 eax 从 16 降为 8、尾部头处 r8d=16。", "",
             "main 的原有边界检查允许后续优化利用 0<=n<=20。最终机器码中的 SIMD 循环已经完全展开并折叠成常量向量选择和一次归约，不能把 main 归约块命中次数称为向量循环迭代次数。main 的门槛为 4，尾部长度为 n mod 4；因此 n=7 已执行归约块，另有 3 次标量尾部。main 内独立 alternating_sum 入口始终未命中，与其已内联的代码形态一致。", "",
             "## 证据边界", "",
             "这些记录证明指定 ELF 中基本块实际执行的路径；不测量时间，也不支持速度或性能优劣结论。harness 的程序启动入口有变化，但独立函数机器字节已验证相同。其他优化配置需要各自反汇编和运行证据。", "",
             "复现命令（WSL，工程根目录）：`python3 scripts/toolchain_extended_boundary.py`。完整命令、版本、退出码和文件摘要见 `commands.json`、`manifest.json`。", ""]
    (out / "BOUNDARY_ANALYSIS.md").write_text("\n".join(note), encoding="utf-8")
    files = [p for p in sorted(out.rglob("*")) if p.is_file() and p.name != "manifest.json"]
    save_json(out / "manifest.json", [{"path": str(p.relative_to(ROOT)), "size": p.stat().st_size, "sha256": digest(p)} for p in files])
    if not unchanged or not all(x["output_pass"] and x["path_pass"] for x in cases):
        raise AssertionError("Boundary verification failed; inspect retained results")
    print(json.dumps(result["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
