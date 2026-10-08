#!/usr/bin/env python3
"""Independent mathematical oracle, deterministic cases, real RISC-V execution.

Integer expectation uses a weighted prefix sum, not either implementation's loop.
Float expectation rounds EVERY elementary operation to IEEE binary32 using struct.
All cases and per-implementation stdout/stderr/exit codes are persisted.
"""
import csv
import json
import math
import random
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/sysy'
SEED = 24115602412565
BASE = [1, 2, 0, -3, 4, 5]


def f32(x):
    return struct.unpack('<f', struct.pack('<f', x))[0]


def integer_expected(n, stop, gate, divisor, delta):
    assert 0 <= n <= 6 and divisor != 0
    a = [x + d for x, d in zip(BASE, delta)]
    # stop=0 never breaks: continue is tested before break in the specification.
    cutoff = next((k for k in range(n) if a[k] != 0 and a[k] == stop), n)
    total = 10 + sum((k + 1) * a[k] for k in range(cutoff))
    calls = 0 if gate == 0 else 1 + int(a[5] < 0)
    tag = (6 if gate == 0 else int(a[0] > 0) + 2 * int(a[5] < 0))
    # Python // is floor division. Explicit magnitude/sign gives C/SysY truncation.
    q = abs(a[1]) // abs(divisor)
    if (a[1] < 0) != (divisor < 0):
        q = -q
    r = a[1] - q * divisor
    return [total, calls, tag, q, r]


def float_expected(n, scale, values):
    transformed = [f32(f32(f32(v) * f32(scale)) + f32(i))
                   for i, v in enumerate(values[:n])]
    positives = [v for v in transformed if v > 0.0]
    total = f32(0.0)
    for v in positives:
        total = f32(total + v)
    result = f32(total + f32(0.25))
    return [result, math.trunc(result), f32(result / f32(n + 1))]


def make_cases():
    rng = random.Random(SEED)
    cases = []
    fixed = [
        ('empty_gate_zero', 0, 40, 0, 3, [0]*6),
        ('initial_full', 6, 40, 1, 3, [0]*6),
        ('break_first', 6, 1, 1, -3, [0]*6),
        ('break_middle', 6, -3, -1, 3, [0]*6),
        ('break_last', 6, 5, 2, -3, [0]*6),
        ('zero_continue_before_break', 6, 0, 0, 1, [-1,-2,0,3,-4,-5]),
        ('short_circuit_two_calls', 6, 40, 1, 3, [0,0,0,0,0,-6]),
        ('short_circuit_first_false', 6, 40, 1, 3, [-2,0,0,0,0,-6]),
        ('short_circuit_zero_first', 1, 40, 1, 3, [-1,0,0,0,0,0]),
        ('negative_dividend', 6, 40, 0, 3, [0,-7,0,0,0,0]),
        ('both_negative_division', 6, 40, -2, -3, [0,-7,0,0,0,0]),
        ('exact_division', 2, 40, 1, -7, [0,12,0,0,0,0]),
        ('zero_dividend', 6, 40, 1, -7, [0,-2,0,0,0,0]),
        ('upper_delta_bound', 6, 40, 2, 7, [30]*6),
        ('lower_delta_bound', 6, 40, -2, -7, [-30]*6),
        ('one_element', 1, 40, 0, 1, [3,0,0,0,0,-5]),
        ('two_elements', 2, 40, 1, 2, [3,-7,0,0,0,0]),
        ('three_elements', 3, 40, 1, 4, [0,0,6,0,0,0]),
        ('four_elements', 4, 40, 1, -2, [0,0,0,0,0,0]),
        ('five_elements', 5, 40, 1, 5, [0,0,0,0,0,0]),
    ]
    for j in range(80):
        delta = [rng.randint(-30,30) for _ in range(6)]
        stop = rng.choice([40, 0, BASE[j % 6] + delta[j % 6]])
        fixed.append((f'generated_{j:02}', rng.randint(0,6), stop,
                      rng.randint(-2,2), rng.choice([i for i in range(-7,8) if i]), delta))
    for name, n, stop, gate, divisor, delta in fixed:
        cases.append({'program':'control_matrix', 'case':name,
                      'input':' '.join(map(str, [n,stop,gate,divisor]+delta))+'\n',
                      'expected':integer_expected(n,stop,gate,divisor,delta)})
    ff = [
        ('empty', 0, 1.0, []),
        ('zero_scale', 4, 0.0, [1,-2,3,-4]),
        ('positive_and_negative',4,1.0,[1,-2,0.5,-4]),
        ('negative_scale',4,-2.0,[1,-2,3,-4]),
        ('fractional',3,0.1,[0.1,0.2,0.3]),
        ('all_filtered',4,2.0,[-10,-10,-10,-10]),
        ('truncation_not_rounding',1,1.0,[0.5]),
        ('small_positive',1,0.0001,[0.0001]),
        ('upper_bound',4,8.0,[32]*4),
        ('negative_bounds',4,-8.0,[-32]*4),
    ]
    for j in range(50):
        n = rng.randint(0,4)
        ff.append((f'generated_{j:02}',n,rng.uniform(-8,8),[rng.uniform(-32,32) for _ in range(n)]))
    for name,n,scale,values in ff:
        scale,values = f32(scale),list(map(f32, values))
        # SysY runtime scanf("%a") accepts hex floats, avoiding decimal ambiguity.
        inp = f'{n} {scale.hex()} ' + ' '.join(v.hex() for v in values) + '\n'
        cases.append({'program':'float_stats','case':name,'input':inp,
                      'expected':float_expected(n,scale,values)})
    return cases


def equal(case, output):
    parts = output.split()
    if case['program'] == 'control_matrix':
        return list(map(int,parts)) == case['expected']
    if len(parts) != 3:
        return False
    actual = [float.fromhex(parts[0]), int(parts[1]), float.fromhex(parts[2])]
    e = case['expected']
    return actual[1] == e[1] and all(
        abs(actual[k]-e[k]) <= 1e-6 + 2e-6 * abs(e[k]) for k in [0,2])


def main():
    # Five manually derived anchors independently check the oracle itself.
    assert integer_expected(0,40,0,3,[0]*6) == [10,0,6,0,2]
    assert integer_expected(6,40,1,3,[0]*6) == [53,1,1,0,2]
    assert integer_expected(6,1,1,-3,[0]*6) == [10,1,1,0,2]
    assert integer_expected(6,40,0,3,[0,-7,0,0,0,0]) == [39,0,6,-1,-2]
    assert float_expected(1,1.0,[0.5]) == [0.75,0,0.375]
    cases = make_cases()
    (ROOT/'tests/sysy_cases.json').write_text(json.dumps({'seed':SEED,'cases':cases},indent=2)+'\n')
    input_dir = ROOT/'tests/inputs'
    input_dir.mkdir(exist_ok=True)
    log_dir = OUT/'logs'
    log_dir.mkdir(exist_ok=True)
    rows, failures = [], []
    exact_float = 0
    for case in cases:
        identifier = f"{case['program']}.{case['case']}"
        (input_dir/f'{identifier}.in').write_text(case['input'])
        (input_dir/f'{identifier}.expected.json').write_text(json.dumps(case['expected'])+'\n')
        for kind in ['source','llvm','asm']:
            cmd = ['qemu-riscv64',str(OUT/'bin'/f"{case['program']}.{kind}")]
            p = subprocess.run(cmd,input=case['input'],text=True,capture_output=True,timeout=5)
            try:
                passed = p.returncode == 0 and equal(case,p.stdout)
            except (ValueError,OverflowError):
                passed = False
            evidence = dict(case, implementation=kind,command=cmd,stdout=p.stdout,
                            stderr=p.stderr,exit_code=p.returncode,passed=passed)
            (log_dir/f'{identifier}.{kind}.json').write_text(json.dumps(evidence,indent=2)+'\n')
            rows.append({'program':case['program'],'case':case['case'],'implementation':kind,
                         'exit_code':p.returncode,'passed':passed,'stdout':p.stdout.strip()})
            if case['program']=='float_stats' and passed:
                t=p.stdout.split()
                if [float.fromhex(t[0]),int(t[1]),float.fromhex(t[2])] == case['expected']:
                    exact_float += 1
            if not passed:
                failures.append(evidence)
    with (OUT/'results.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    summary={'seed':SEED,'logical_cases':len(cases),'executions':len(rows),
             'passed':len(rows)-len(failures),'failed':len(failures),
             'integer_cases':sum(c['program']=='control_matrix' for c in cases),
             'float_cases':sum(c['program']=='float_stats' for c in cases),
             'float_exact_numeric_matches':exact_float,
             'float_tolerance':'abs(actual-expected) <= 1e-6 + 2e-6*abs(expected)',
             'runtime_stderr':'upstream destructor prints TOTAL: 0H-0M-0S-0us; not performance data',
             'failures':failures}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    if failures:
        raise SystemExit(1)


if __name__=='__main__':
    main()
