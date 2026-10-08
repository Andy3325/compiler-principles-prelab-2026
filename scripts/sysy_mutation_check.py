#!/usr/bin/env python3
"""Deliberately inject three wrong assembly semantics; oracle must reject each.

These are controlled mutations, NOT bugs observed in the final implementations.
"""
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('oracle', ROOT/'tests/sysy_oracle.py')
oracle=importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)
OUT=ROOT/'artifacts/sysy/mutations'
OUT.mkdir(exist_ok=True)
mutations=[
    ('eager_and','control_matrix','empty_gate_zero',
     'beqz s2, .Lsc_or', 'nop # deliberately eager &&'),
    ('wrong_remainder','control_matrix','negative_dividend',
     'remw s7, t0, s3', 'divw s7, t0, s3'),
    ('round_to_nearest','float_stats','truncation_not_rounding',
     'fcvt.w.s s2, fs1, rtz', 'fcvt.w.s s2, fs1, rne'),
]
records=[]
cases=oracle.make_cases()
for name,program,case_name,before,after in mutations:
    original=(ROOT/'src/riscv'/f'{program}.S').read_text()
    assert original.count(before)==1
    source=OUT/f'{name}.S'
    source.write_text(original.replace(before,after))
    binary=OUT/name
    cmd=['riscv64-linux-gnu-gcc','-static','-no-pie','-march=rv64gc','-mabi=lp64d',
         str(source),str(ROOT/'artifacts/sysy/objects/libsylib.a'),'-o',str(binary)]
    built=subprocess.run(cmd,capture_output=True,text=True)
    assert built.returncode==0,built.stderr
    case=next(c for c in cases if c['program']==program and c['case']==case_name)
    run=subprocess.run(['qemu-riscv64',str(binary)],input=case['input'],capture_output=True,text=True,timeout=5)
    detected=run.returncode==0 and not oracle.equal(case,run.stdout)
    records.append(dict(name=name,case=case,build_command=cmd,build_stderr=built.stderr,
                        stdout=run.stdout,stderr=run.stderr,exit_code=run.returncode,
                        detected=detected,mutation=dict(before=before,after=after)))
summary={'purpose':'deliberate fault injection, separate from final 480 successful executions',
         'mutants':len(records),'detected':sum(r['detected'] for r in records),'records':records}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
assert summary['detected']==summary['mutants']
