# Copyright 2018 Daniel Selsam. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import numpy as np
import random
import argparse
import PyMiniSolvers.minisolvers as minisolvers


def write_dimacs_to(n_vars, iclauses, out_filename):
    with open(out_filename, 'w') as f:
        write_dimacs_to_file(n_vars, iclauses, f)

def write_dimacs_to_file(n_vars, iclauses, f, is_sat=None):
    if is_sat is not None:
        f.write("\nc sat %d\n" % is_sat)
    f.write("p cnf %d %d\n" % (n_vars, len(iclauses)))
    for c in iclauses:
        for x in c:
            f.write("%d " % x)
        f.write("0\n")

def mk_out_filenames(opts, n_vars, t):
    prefix = "%s/sr_n=%d_mink=%d_maxk=%d_t=%d" % \
        (opts.out_dir, n_vars, opts.min_k, opts.max_k, t)
    return ("%s_sat=0.dimacs" % prefix, "%s_sat=1.dimacs" % prefix)

def generate_k_iclause(n, k):
    vs = np.random.choice(n, size=min(n, k), replace=False)
    return [v + 1 if random.random() < 0.5 else -(v + 1) for v in vs]


def gen_iclause_pair(opts):
    return _gen_iclause_pair(opts.min_n, opts.max_n, opts.min_k, opts.max_k)


def _gen_iclause_pair(min_n, max_n, min_k, max_k):
    n = random.randint(min_n, max_n)

    solver = minisolvers.MinisatSolver()
    for i in range(n): solver.new_var(dvar=True)

    iclauses = []

    while True:
        k = random.randint(min_k, min(max_k, n-1))
        iclause = generate_k_iclause(n, k)

        solver.add_clause(iclause)
        is_sat = solver.solve()
        if is_sat:
            iclauses.append(iclause)
        else:
            break

    iclause_unsat = iclause
    iclause_sat = [- iclause_unsat[0] ] + iclause_unsat[1:]
    return n, iclauses, iclause_unsat, iclause_sat


def gen_iclause_pair_n_vars(opts, n_vars):
    """
    Generate a pair of UNSAT/SAT problems with the given number of variables.

    Arguments:
        opts -- problem generation parameters.
            Must have `min_n`, `max_n`, `p_k_2`, and `p_geo` attributes.

    Returns:
        `([], [])` -- a pair of (UNSAT problem, SAT problem).
    """
    _, iclauses, iclause_unsat, iclause_sat = \
        _gen_iclause_pair(n_vars, n_vars, opts.min_k, opts.max_k)

    return (iclauses + [iclause_unsat], iclauses + [iclause_sat])


def init_opts(parser):
    parser.add_argument('out_dir', action='store', type=str)
    parser.add_argument('n_pairs', action='store', type=int)

    parser.add_argument('--min_n', action='store', dest='min_n', type=int, default=40)
    parser.add_argument('--max_n', action='store', dest='max_n', type=int, default=40)

    parser.add_argument('--min_k', action='store', dest='min_k', type=int, default=2)
    parser.add_argument('--max_k', action='store', dest='max_k', type=int, default=10)

    parser.add_argument('--py_seed', action='store', dest='py_seed', type=int, default=None)
    parser.add_argument('--np_seed', action='store', dest='np_seed', type=int, default=None)

    parser.add_argument('--print_interval', action='store', dest='print_interval', type=int, default=100)
    opts = parser.parse_args()

    if opts.py_seed is not None: random.seed(opts.py_seed)
    if opts.np_seed is not None: np.random.seed(opts.np_seed)

    return opts


if __name__ == "__main__":
    opts = init_opts(argparse.ArgumentParser())
    for pair in range(opts.n_pairs):
        if pair % opts.print_interval == 0: print("[%d]" % pair)
        n_vars, iclauses, iclauses_unsat, iclauses_sat = gen_iclause_pair(opts)
        out_filenames = mk_out_filenames(opts, n_vars, pair)
        write_dimacs_to(n_vars, iclauses + [iclauses_unsat], out_filenames[0])
        write_dimacs_to(n_vars, iclauses + [iclauses_sat], out_filenames[1])
