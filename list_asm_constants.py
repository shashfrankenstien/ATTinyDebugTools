# get any ldi instructions with non numeric operands

import os
from pathlib import Path
import re
import json

# PROJPATH = os.path.dirname(os.path.abspath(__file__))
PROJPATH = os.getcwd()
SRCPATH = os.path.join(PROJPATH, 'src')
DISPATH = os.path.join(PROJPATH, 'build', 'kernel.dis')



def src_parse_ldi(line):
    line = line.replace('ldi', '')
    reg, val = line.split(',')
    val = val.strip()

    litterals = re.findall(r"\'.\'", val)
    if litterals:
        for lit in litterals:
            val = val.replace(lit, str(ord(lit.strip("'"))))
    return reg.strip(), val


def src_get_ldi():
    out = {}
    for f in Path(SRCPATH).rglob('*.asm'):
        with open(f, 'r') as asm:
            label = None
            for l in asm.readlines():
                if not l.startswith(' ') and not l.startswith(';') and not l.startswith('.') and l.strip():
                    label = l.split(";")[0].replace(":", "").strip()
                    out[label] = []
                if l.strip().lower().startswith('ldi'):
                    ldi = str(l.strip().split(';')[0]).strip()
                    out[label].append(src_parse_ldi(ldi))

    return out



def dis_get_ldi():
    out = {}
    with open(DISPATH, 'r') as dis:
        label = None
        for l in dis.readlines():
            res_label = re.findall(r'^[0-9a-fA-F]+ \<(.+)\>', l)
            res_ldi = re.findall(r'ldi\s(r\d+?), .+?;\s(.*)', l)
            if res_label:
                label = res_label[0]
                out[label] = []
            elif res_ldi:
                out[label].append(res_ldi[0])

    return out



def do_algebra(lut, eq, res):
    splits = re.findall(r'[^\s\(\)]+', eq)
    if len(splits) == 1:
        return None # nothing to do

    for s in splits:
        if s in lut:
            eq = eq.replace(s, str(lut[s]))
    try:
        solved = eval(eq)
        return True # no new keys

    except NameError:
        new_splits = re.findall(r'[^\s\(\)\+\*\-\/]+', eq)
        new_splits = list(filter(lambda s: not str(s).isnumeric(), new_splits))
        if len(new_splits) != 1:
            return None # unsupported
            print(eq)

        to_solve = new_splits[0]
        calc = lambda v: int(eval(eq.replace(to_solve, str(v))))
        solvedm1 = calc(-1)
        solved0 = calc(0)
        solved1 = calc(1)

        if res == solved0:
            return (to_solve, -1)
        elif res == solved0:
            return (to_solve, 0)
        elif res == solved1:
            return (to_solve, 1)

        elif abs(res-solved1) > abs(res-solvedm1): # negative value
            for i in range(2**16):
                if res == calc(i*-1):
                    return (to_solve, i*-1)
        elif abs(res-solved1) < abs(res-solvedm1): # positive value
            for i in range(2**16):
                if res == calc(i):
                    return (to_solve, i)



def match_ldi(src, dis):
    out = {}
    for key in src:
        for i, elem in enumerate(src[key]):
            sreg, sval = elem
            dreg, dval = dis[key][i]
            if sval.startswith('0x'):
                continue
            if dreg == sreg and sval != dval:
                out[sval] = dval

    # resolve hi8, low8 and pm
    for k,v in out.copy().items():
        if k.startswith('hi8'):
            low_k = k.replace('hi8', 'lo8')
            low_v = out[low_k]
            new_k = k.replace('hi8', '').strip('(').strip(')')
            pm_fact = 1
            if new_k.startswith("pm("):
                pm_fact = 2
                new_k = new_k.replace("pm(", '')
            out[new_k] = ((256 * int(v)) + int(low_v)) * pm_fact
            del out[k]
            del out[low_k]

    out = {k: int(str(v)) for k,v in out.items()}

    # solve simple math
    for k,v in out.copy().items():
        new = do_algebra(lut=out, eq=k, res=v)
        if new:
            del out[k]
        if isinstance(new, tuple):
            out[new[0]] = new[1]

    # printing
    name_size = 80
    for k,v in sorted(out.items()):
        if len(k) > name_size:
            k = k[:name_size-2] + '..'
        str_out = ("{" + f"k:>{name_size}" + "}").format(k=k)
        str_out += f" | {hex(v):>10} | {v}"
        print(str_out)



if __name__ == '__main__':
    src = src_get_ldi()
    dis = dis_get_ldi()

    match_ldi(src, dis)

