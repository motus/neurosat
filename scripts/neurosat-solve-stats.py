#!/usr/bin/env python3

import re
import sys
from collections import defaultdict


_RE_FNAME = re.compile(r'.*neurosat-experiment-1-(\d+)-(\d+)\.log$')
_RE_SAT = re.compile(r'_sat=([01])\.dimacs\]')
_RE_VALID = re.compile(r'\((True|False), ([N[])')

sat_solved = defaultdict(set)
sat_all = defaultdict(set)
for fname in sys.argv[1:]:
    sys.stderr.write("%-64s\r" % fname)
    [(n_vars, _n_iter)] = _RE_FNAME.findall(fname)
    n_vars = int(n_vars)
    with open(fname) as fh_input:
        for line in fh_input:
            split = line.split(' ', 1)
            if len(split) != 2:
                continue
            (key, val) = split
            is_sat = _RE_SAT.findall(key)
            if not is_sat:
                continue
            is_sat = int(is_sat[0])
            if is_sat:
                sat_all[n_vars].add(key)
            [(is_valid, has_solution)] = _RE_VALID.findall(val)
            is_valid = is_valid == 'True'
            has_solution = has_solution == '['
            if is_sat and is_valid and has_solution:
                sat_solved[n_vars].add(key)

sys.stderr.write("\n")

print("n_vars,sat,sat_good,sat_good_pct")
for n_vars in [20, 40, 60, 80]:
    n_sat = len(sat_all[n_vars])
    n_solved = len(sat_solved[n_vars])
    print("%d,%d,%d,%.2f" % (n_vars, n_sat, n_solved, n_solved * 100.0 / n_sat))
