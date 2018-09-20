#!/usr/bin/env python3

import re
import sys


_RE_SAT = re.compile(r'_sat=([01])\.dimacs\]')
_RE_VALID = re.compile(r'\((True|False), ([N[])')

sat_solved = set()
sat_all = set()
sat_invalid = set()
for fname in sys.argv[1:]:
    sys.stderr.write("%-64s\r" % fname)
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
                sat_all.add(key)
            [(is_valid, has_solution)] = _RE_VALID.findall(val)
            is_valid = is_valid == 'True'
            has_solution = has_solution == '['
            if is_sat and is_valid and has_solution:
                sat_solved.add(key)
            if not is_valid:
                sat_invalid.add(key)

sys.stderr.write("\n")

print("sat,sat_invalid,sat_good,sat_good_pct")
n_sat = len(sat_all)
n_solved = len(sat_solved)
print("%d,%d,%d,%.2f" % (n_sat, len(sat_invalid), n_solved, n_solved * 100.0 / n_sat))
