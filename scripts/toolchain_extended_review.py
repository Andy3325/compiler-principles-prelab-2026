#!/usr/bin/env python3
"""Verify protected inputs and the rebuilt optimization-exploration report.

Run on Windows after scripts/build_report.ps1; --render also makes page PNGs
and contact sheets. This does not rerun or alter any baseline experiment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/toolchain/extended_exploration"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    review = OUT / "report_review"
    review.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((OUT / "preservation/protected_before.json").read_text(encoding="utf-8-sig"))
    meta = json.loads((OUT / "preservation/baseline_verification.json").read_text(encoding="utf-8-sig"))
    allowed = {"report/toolchain.tex"} | {"report/main." + ext for ext in
        ("aux", "fdb_latexmk", "fls", "log", "out", "pdf", "toc", "xdv", "synctex.gz")}
    changed, unexpected = [], []
    for entry in manifest:
        rel = entry["path"].replace("\\", "/")
        p = ROOT / rel
        if not p.is_file() or sha(p) != entry["sha256"].upper():
            changed.append(rel)
            if rel not in allowed:
                unexpected.append(rel)
    old = (Path(meta["backup"]) / "report/toolchain.tex").read_text(encoding="utf-8")
    new = (ROOT / "report/toolchain.tex").read_text(encoding="utf-8")
    markers = ["\\subsubsection{从循环依赖到整数归约}",
               "\\subsubsection{向量通道、尾部与展开}",
               "\\subsubsection{代码大小与编译器差异}"]
    sections = [old[old.index(markers[i]):old.index(markers[i+1])].strip() for i in (0, 1)]
    old_six = old[old.index(markers[2]):].strip()
    adjusted_six = old_six.replace("\\subsubsection{代码大小与编译器差异}",
        "\\subsubsection{代码大小、调试信息与编译器差异}").replace(
        "本文未进一步比较 O3。", "上述基线未包含 O3；本轮新增比较见\\ref{sec:toolchain-gcc-controlled}节。")
    preserved = {"original_reduction_subsection": sections[0] in new,
                 "original_vector_tail_subsection": sections[1] in new,
                 "original_size_analysis_except_heading_and_obsolete_O3_sentence": adjusted_six in new}
    helper = (ROOT / "report/toolchain_extended.tex").read_text(encoding="utf-8")
    expanded = new.replace("\\input{toolchain_extended}", helper)
    old_labels = set(re.findall(r"\\label\{([^}]+)\}", old))
    new_labels = set(re.findall(r"\\label\{([^}]+)\}", expanded))
    preserved["all_original_toolchain_labels"] = old_labels <= new_labels
    measured = {row["configuration"]: row for row in json.loads((OUT / "metrics.json").read_text(encoding="utf-8"))}
    table_checks = {}
    for label, names, indices in (
        ("tab:clang-controlled", ["clang_A_O2", "clang_B_no_vector", "clang_C_no_unroll", "clang_D_no_vector_no_unroll"], (5, 6, 7)),
        ("tab:gcc-controlled", ["gcc_A_O2", "gcc_B_O2_vector", "gcc_C_O3", "gcc_D_O3_no_vector"], (6, 5, 7)),
        ("tab:noinline-controlled", ["clang_A_O2", "clang_noinline_O2"], (4, 5, 6))):
        body = helper.split("\\label{" + label + "}", 1)[1].split("\\end{table}", 1)[0]
        rows = [line.rsplit("\\\\", 1)[0].split(" & ") for line in body.splitlines()
                if re.match(r"^(?:[ABCD]|原始|noinline) & ", line)]
        checks = []
        for cells, name in zip(rows, names):
            row = measured[name]
            checks.append(cells[indices[0]].strip() == str(row["text_bytes"]) and
                          cells[indices[1]].strip() == str(row["main_object_instruction_count"]) and
                          cells[indices[2]].strip() == f'{row["passed"]}/{row["test_count"]}')
            if label == "tab:clang-controlled":
                checks.append(cells[4].strip() == f'{row["final_ir_functions"]["alternating_sum"]["basic_blocks"]}/{row["final_ir_functions"]["main"]["basic_blocks"]}')
        table_checks[label] = len(rows) == len(names) and all(checks)
    pdf = ROOT / "report/main.pdf"
    commands = []
    with tempfile.TemporaryDirectory(prefix="compiler-report-review-") as tmp:
        text_path = Path(tmp) / "main.txt"
        bbox_path = Path(tmp) / "main.html"
        for command in (["pdftotext", "-layout", str(pdf), str(text_path)],
                        ["pdftotext", "-bbox-layout", str(pdf), str(bbox_path)]):
            p = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
            commands.append({"command": command, "exit": p.returncode, "stderr": p.stderr})
            p.check_returncode()
        txt = text_path.read_text(encoding="utf-8")
        (review / "main.txt").write_text(txt, encoding="utf-8")
        bbox = bbox_path.read_text(encoding="utf-8")
        (review / "main.bbox.html").write_text(bbox, encoding="utf-8")
    pages = txt.split("\f")
    if not pages[-1].strip():
        pages.pop()
    headings = ["Clang 向量化与循环展开的受控实验", "GCC 优化级别与向量化配置比较",
                "函数内联对后续循环优化的影响", "代码大小、调试信息与编译器差异"]
    locations = {}
    for h in headings:
        locations[h] = [{"physical_page": i+1,
            "printed_page_footer": p.strip().splitlines()[-1].strip()}
            for i, p in enumerate(pages) if re.sub(r"\s", "", h) in re.sub(r"\s", "", p)]
    outside = []
    tree = ET.fromstring(bbox)
    for i, page in enumerate(tree.iter("{http://www.w3.org/1999/xhtml}page")):
        w, h = float(page.attrib["width"]), float(page.attrib["height"])
        for word in page.iter("{http://www.w3.org/1999/xhtml}word"):
            a = {k: float(v) for k, v in word.attrib.items()}
            if a["xMin"] < 0 or a["yMin"] < 0 or a["xMax"] > w or a["yMax"] > h:
                outside.append({"page": i+1, "text": word.text, "box": a})
    log = (ROOT / "report/main.log").read_text(encoding="utf-8", errors="replace")
    bad = [line for line in log.splitlines() if re.search(
        r"^!|Undefined control sequence|LaTeX Warning:.*undefined|There were undefined references|Missing character:|Overfull \\[hv]box", line)]
    result = {"pdf": str(pdf), "pdf_sha256": sha(pdf), "pdf_bytes": pdf.stat().st_size,
              "pages": len(pages), "protected_existing_file_count": len(manifest),
              "changed_existing_files": changed, "unexpected_protected_changes": unexpected,
              "preservation": preserved, "table_values_match_metrics": table_checks, "section_locations": locations,
              "outside_page_words": outside, "bad_latex_log_lines": bad,
              "extraction_commands": commands, "visual_review": "PENDING"}
    if args.render:
        command = ["pdftoppm", "-png", "-r", "120", str(pdf), str(review / "page")]
        p = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        result["render_command"] = {"command": command, "exit": p.returncode, "stderr": p.stderr}
        p.check_returncode()
        from PIL import Image, ImageOps, ImageDraw
        images = sorted(review.glob("page-*.png"))
        for start in range(0, len(images), 9):
            sheet = Image.new("RGB", (960, 1350), "#e0e0e0")
            draw = ImageDraw.Draw(sheet)
            for j, image_path in enumerate(images[start:start+9]):
                with Image.open(image_path) as image:
                    tile = ImageOps.contain(image.convert("RGB"), (310, 422))
                x, y = (j % 3)*320, (j//3)*450
                sheet.paste(tile, (x+(320-tile.width)//2, y+22))
                draw.text((x+8, y+5), image_path.stem, fill="black")
            sheet.save(review / f"contact-{start//9+1}.png")
        result["rendered_pages"] = len(images)
    (review / "verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if unexpected or not all(preserved.values()) or not all(table_checks.values()) or outside or bad or not all(locations.values()):
        raise SystemExit("Report verification failed; inspect retained evidence")


if __name__ == "__main__":
    main()
