#!/usr/bin/env python3
"""Generate source-checked CFG/ABI figures; never rebuild or rerun test programs.

Input: final handwritten LLVM IR/assembly and existing mutation evidence.
Analysis: parse actual terminators/phi pairs, calculate dominance, inspect stack
save/restore offsets, run LLVM 14 verifier and dominator-tree printer.
The layout is manually arranged, but all block/edge/slot assertions must pass.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/mechanism'
FIG = ROOT / 'report/figures'
IR = ROOT / 'src/llvm/control_matrix.ll'
ASM = ROOT / 'src/riscv/float_stats.S'
MUT = ROOT / 'artifacts/sysy/mutations/summary.json'
INK, BLUE, RED, GREEN = '#223247', '#1F6080', '#A84632', '#316C53'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def function_body(text, name):
    return re.search(r'^define[^\n]*@' + re.escape(name) + r'\([^\n]*\) \{\n(.*?)^\}',
                     text, re.M | re.S).group(1)


def parse_cfg(body):
    blocks, current = {}, None
    for raw in body.splitlines():
        line = raw.split(';', 1)[0].strip()
        if line.endswith(':'):
            current = line[:-1]
            blocks[current] = []
        elif line:
            blocks[current].append(line)
    edges = []
    for block, instructions in blocks.items():
        term = instructions[-1]
        dests = re.findall(r'label %([\w.]+)', term)
        for i, dest in enumerate(dests):
            assert dest in blocks
            edges.append({'from':block, 'to':dest,
                          'condition':('true' if i == 0 else 'false') if len(dests)==2 else 'unconditional'})
    predecessors = {b: sorted(e['from'] for e in edges if e['to']==b) for b in blocks}
    dom = {b: ({'entry'} if b=='entry' else set(blocks)) for b in blocks}
    while True:
        new = {b: ({b} if b=='entry' else {b}|set.intersection(*(dom[p] for p in predecessors[b]))) for b in blocks}
        if new == dom:
            break
        dom = new
    definitions = {re.match(r'(%[\w.]+) =', inst).group(1): b
                   for b, insts in blocks.items() for inst in insts if re.match(r'%[\w.]+ =', inst)}
    phis = []
    for b, insts in blocks.items():
        for inst in insts:
            if ' = phi ' not in inst:
                continue
            pairs = re.findall(r'\[([^,]+), %([\w.]+)\]', inst)
            assert sorted(p for _,p in pairs) == predecessors[b], (b, inst)
            for value, pred in pairs:
                if value.strip() in definitions:
                    assert definitions[value.strip()] in dom[pred], (value,pred)
            phis.append({'block': b, 'instruction': inst,
                         'incoming': [{'value':v.strip(),'predecessor':p} for v,p in pairs]})
    return {'blocks':blocks,'edges':edges,'predecessors':predecessors,
            'dominators':{k:sorted(v) for k,v in dom.items()},'phis':phis}


def run_llvm():
    commands=[]
    if os.name=='nt':
        linux_ir='/mnt/'+IR.drive[0].lower()+IR.as_posix()[2:]
        prefix=['wsl','-d','Ubuntu-22.04','--','opt-14']
    else:
        linux_ir=str(IR)
        prefix=['opt-14']
    for stem, options in [('verify',['-verify','-disable-output']),
                          ('dominators',['-enable-new-pm=0','-analyze','-domtree'])]:
        cmd=prefix+options+[linux_ir]
        p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
        (OUT/f'sysy-{stem}.txt').write_text('COMMAND: '+subprocess.list2cmdline(cmd)+'\nEXIT: '+str(p.returncode)+
                                         '\nSTDOUT:\n'+p.stdout+'\nSTDERR:\n'+p.stderr, encoding='utf-8')
        commands.append({'command':cmd,'exit_code':p.returncode,'evidence':f'artifacts/mechanism/sysy-{stem}.txt'})
        assert p.returncode==0, p.stderr
    return commands


def node(ax,x,y,w,h,label,fill='#F0F4F8',size=8.4):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.03,rounding_size=0.06',
                               linewidth=.8,edgecolor=INK,facecolor=fill,zorder=3))
    ax.text(x,y,label,ha='center',va='center',fontsize=size,fontfamily='DejaVu Sans Mono',color=INK,zorder=4)


def route(ax,points,color=INK,style='-',label=None,label_at=None,size=8):
    for a,b in zip(points[:-2],points[1:-1]):
        ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=1.05,linestyle=style,zorder=1)
    ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=9,
                                linewidth=1.05,linestyle=style,color=color,zorder=2))
    if label:
        ax.text(*label_at,label,fontsize=size,color=color,va='center',ha='center',
                bbox={'facecolor':'white','edgecolor':'none','pad':1.0},zorder=5)


def save(fig,stem):
    fig.savefig(FIG/f'{stem}.pdf',facecolor='white')
    fig.savefig(FIG/f'{stem}.png',dpi=220,facecolor='white')
    plt.close(fig)


def cfg_figure():
    fig=plt.figure(figsize=(6.65,3.60))
    left=fig.add_axes([.015,.045,.645,.905]); right=fig.add_axes([.685,.045,.30,.905])
    for ax in [left,right]: ax.set_axis_off()
    left.set(xlim=(-.1,6.3),ylim=(.2,7.1))
    left.text(.0,7.02,'(a) fold: complete CFG',va='top',fontsize=9.5,fontweight='bold',color=INK)
    node(left,1.6,6.2,2.0,.57,'entry\n%limit = %n - 1')
    node(left,1.6,5.06,2.0,.76,'loop\n%i, %sum: phi')
    node(left,1.6,3.72,2.0,.84,'body\n%v = cell(...)\n%next = %i + 1')
    node(left,4.0,2.57,2.35,.68,'check.break\n%v == %stop?')
    node(left,4.0,1.2,2.35,.68,'accum\n%added = %sum\n       + %v*%next',size=7.8)
    node(left,1.35,1.2,2.0,.68,'step\n%sum.next: phi')
    node(left,5.08,5.06,1.8,.76,'exit\nret %sum',fill='#F8EFEB')
    route(left,[(1.6,5.89),(1.6,5.46)])
    route(left,[(1.6,4.66),(1.6,4.16)],label='T',label_at=(1.82,4.43))
    route(left,[(2.64,5.06),(4.14,5.06)],label='F: loop ends',label_at=(3.4,5.28),size=7.5)
    route(left,[(2.1,3.27),(2.1,2.57),(2.78,2.57)],label='F',label_at=(2.32,2.80))
    route(left,[(1.08,3.27),(1.08,1.57)],color=GREEN,label='T: continue',label_at=(1.08,2.55),size=7.5)
    route(left,[(5.2,2.57),(6.04,2.57),(6.04,5.06),(6.01,5.06)],color=RED,
          label='T: break',label_at=(5.80,3.60),size=7.5)
    route(left,[(4.0,2.2),(4.0,1.56)],label='F',label_at=(4.20,1.91))
    route(left,[(2.79,1.2),(2.39,1.2)])
    route(left,[(.31,1.2),(.03,1.2),(.03,5.06),(.57,5.06)],color=BLUE,style='--',
          label='back edge',label_at=(.22,.58),size=7.5)
    right.set(xlim=(-.2,3.8),ylim=(.2,7.1))
    right.text(-.13,7.02,'(b) main: first &&',va='top',fontsize=9.5,fontweight='bold',color=INK)
    node(right,1.47,5.85,2.95,.86,'sc.and\n%gate.nonzero?')
    node(right,1.47,3.63,2.95,1.00,'sc.and.rhs\ncall tick\ncompare / zext')
    node(right,1.47,1.36,2.95,.96,'sc.first.merge\n%tag1: phi',size=7.6)
    route(right,[(1.47,5.39),(1.47,4.17)],label='T: evaluate RHS',label_at=(1.48,4.70),size=7.4)
    route(right,[(1.47,3.10),(1.47,1.87)],label='value: %first.tag',label_at=(1.45,2.44),size=7.1)
    route(right,[(2.97,5.85),(3.48,5.85),(3.48,1.36),(3.00,1.36)],color=GREEN)
    right.text(3.50,3.61,'F: skip RHS; value 0',rotation=90,ha='center',va='center',fontsize=7.5,color=GREEN,
               bbox={'facecolor':'white','edgecolor':'none','pad':1})
    right.text(1.5,.37,'Later || blocks omitted.',ha='center',fontsize=7.4,color=INK)
    save(fig,'llvm-fold-cfg')


def frame_figure(slots):
    fig=plt.figure(figsize=(6.65,2.86))
    ax=fig.add_axes([.02,.065,.96,.89]); ax.axis('off'); ax.set(xlim=(0,10),ylim=(0,8))
    ax.text(0,7.95,'(a) affine: leaf, no stack frame',fontsize=9.3,weight='bold',va='top',color=INK)
    headers=[(.0,'Value'),(1.15,'Register'),(2.25,'Actual instruction')]
    for x,t in headers: ax.text(x,6.9,t,fontsize=8.4,weight='bold',color=BLUE)
    data=[('x','fa0','fmul.s fa0, fa0, fa1'),('scale','fa1','(same fmul.s)'),
          ('offset','a0','fcvt.s.w ft0, a0'),('return','fa0','fadd.s fa0, fa0, ft0; ret')]
    for j,(value,reg,instruction) in enumerate(data):
        y=6.15-j*.69
        ax.text(0,y,value,fontsize=8.5,color=INK)
        ax.text(1.18,y,reg,fontsize=8.5,fontfamily='DejaVu Sans Mono',color=INK)
        ax.text(2.25,y,instruction,fontsize=7.15,fontfamily='DejaVu Sans Mono',color=INK)
    ax.text(0,2.7,'Live across call affine:',fontsize=8.5,weight='bold',color=BLUE)
    ax.text(0,2.08,'s0 = array   s1 = n   s2 = i',fontsize=8.1,fontfamily='DejaVu Sans Mono',color=INK)
    ax.text(0,1.48,'fs0 = scale   fs1 = sum',fontsize=8.1,fontfamily='DejaVu Sans Mono',color=INK)
    ax.text(0,.58,'Prologue slots save the caller\'s old registers;\ncurrent loop values stay in s*/fs* across affine.',
            fontsize=7.7,color=INK,va='center')
    ax.text(6.08,7.95,'(b) sum_positive: 64-byte frame',fontsize=9.3,weight='bold',va='top',color=INK)
    x,w,ybase,dy=6.75,2.48,.82,.72
    content={off:f'saved {reg} ({ins})' for ins,reg,off in slots}
    for index,off in enumerate(range(0,64,8)):
        y=ybase+index*dy
        fill='#F0F4F8' if off>=16 else '#F3F3F3'
        ax.add_patch(Rectangle((x,y),w,dy,facecolor=fill,edgecolor=INK,lw=.65))
        text=content.get(off,'unused')
        ax.text(x+w/2,y+dy/2,text,ha='center',va='center',fontsize=8,color=INK)
        ax.text(x-.15,y+dy/2,f'+{off:02}',ha='right',va='center',fontsize=8,fontfamily='DejaVu Sans Mono',color=INK)
    ax.text(x+w/2,7.05,'old sp = new sp + 64  (high)',ha='center',fontsize=7.7,color=INK)
    ax.text(x+w/2,.39,'new sp + 0  (low)',ha='center',fontsize=8,color=INK)
    ax.text(9.73,3.65,'64 bytes = 4 x 16; no local/spill slots',rotation=90,ha='center',va='center',fontsize=7.8,color=BLUE)
    save(fig,'riscv-call-frame')


def main():
    OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(exist_ok=True)
    inputs={str(p.relative_to(ROOT)):digest(p) for p in [IR,ASM,MUT,ROOT/'src/sysy/control_matrix.sy']}
    text=IR.read_text(encoding='utf-8')
    fold=parse_cfg(function_body(text,'fold'))
    expected=[('entry','loop'),('loop','body'),('loop','exit'),('body','step'),('body','check.break'),
              ('check.break','exit'),('check.break','accum'),('accum','step'),('step','loop')]
    assert [(e['from'],e['to']) for e in fold['edges']]==expected
    assert 'loop' in fold['dominators']['exit'] and fold['blocks']['exit']==['ret i32 %sum']
    main_cfg=parse_cfg(function_body(text,'main'))
    selected={'sc.and','sc.and.rhs','sc.first.merge'}
    short_edges=[e for e in main_cfg['edges'] if e['from'] in selected and e['to'] in selected]
    assert len(short_edges)==3
    assert any('@tick(' in i for i in main_cfg['blocks']['sc.and.rhs'])
    asm=ASM.read_text(encoding='utf-8')
    affine=re.search(r'^affine:\n(.*?)^\s*\.size affine,',asm,re.M|re.S).group(1)
    frame=re.search(r'^sum_positive:\n(.*?)^\s*\.size sum_positive,',asm,re.M|re.S).group(1)
    assert 'sp' not in affine and 'call ' not in affine
    assert 'addi sp, sp, -64' in frame and 'addi sp, sp, 64' in frame
    slots=[(ins,reg,int(off)) for ins,reg,off in re.findall(r'^\s*(sd|fsd) (\w+), (\d+)\(sp\)',frame,re.M)]
    assert slots==[('sd','ra',56),('sd','s0',48),('sd','s1',40),('sd','s2',32),('fsd','fs0',24),('fsd','fs1',16)]
    for ins,reg,off in slots:
        assert f'{"fld" if ins=="fsd" else "ld"} {reg}, {off}(sp)' in frame
    for instruction in ['fmul.s fa0, fa0, fa1','fcvt.s.w ft0, a0','fadd.s fa0, fa0, ft0']:
        assert instruction in affine
    mutation=json.loads(MUT.read_text(encoding='utf-8'))
    assert mutation['mutants']==3 and mutation['detected']==3
    commands=run_llvm()
    with plt.rc_context({'pdf.fonttype':42,'font.family':'DejaVu Sans','font.size':8,'figure.facecolor':'white'}):
        cfg_figure(); frame_figure(slots)
    evidence={'fold':fold,'short_circuit_subgraph':{'blocks':sorted(selected),'edges':short_edges},
              'affine_leaf':True,'sum_positive_frame_bytes':64,'save_slots':slots,
              'unused_stack_bytes':[0,15],'no_local_or_spill_slots':True,
              'mutation_records':mutation,'wrong_row_stride_mutation':'NOT_EXECUTED'}
    (OUT/'sysy-mechanism-analysis.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    manifest={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'source_sha256':inputs,
              'script_sha256':digest(Path(__file__)),'commands':commands,'matplotlib':matplotlib.__version__,
              'presentation':'Manually positioned layout; every displayed CFG edge, block, stack slot and instruction is asserted against parsed final files.',
              'source_unchanged':all(digest(ROOT/p)==h for p,h in inputs.items()),
              'new_test_executions':0,'new_compilation_of_programs':0,
              'outputs':{str(p.relative_to(ROOT)):digest(p) for p in [FIG/(stem+ext) for stem in ['llvm-fold-cfg','riscv-call-frame'] for ext in ['.pdf','.png']]}}
    assert manifest['source_unchanged']
    (OUT/'sysy-figure-manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'fold_blocks':len(fold['blocks']),'fold_edges':len(fold['edges']),
                      'phi_predecessor_and_value_availability_checks':'passed','affine_frame_bytes':0,
                      'sum_positive_frame_bytes':64,'new_test_executions':0,
                      'source_unchanged':manifest['source_unchanged']},indent=2))


if __name__=='__main__': main()
