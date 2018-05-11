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

import math
import os
import numpy as np
import random
import pickle
import argparse
import sys
from solver import solve_sat
from mk_problem import mk_batch_problem
from gen_sr_dimacs import init_opts, gen_iclause_pair2


class GenerationOpts:
    def __init__(self, opts):
        self.min_n = opts.min_n
        self.max_n = opts.max_n
        self.p_k_2 = opts.p_k_2
        self.p_geo = opts.p_geo


def mk_dataset_filename(opts, n_batches):
    return "%s/npb=%d_nb=%d.pkl" % (opts.out_dir, opts.max_nodes_per_batch, n_batches)

parser = argparse.ArgumentParser()
parser.add_argument('--max_nodes_per_batch', action='store', type=int)
parser.add_argument('--one', action='store', dest='one', type=int, default=0)

opts = init_opts(parser)

n_batch = 0
n_nodes_in_batch = 0
gen_opts = GenerationOpts(opts)


if pair % opts.print_interval == 0:
    print("[%d]" % pair)

batch_range = 0.3
n_pairs_per_var = opts.n_pairs / (opts.max_n - opts.min_n + 1)
n_pairs_rem = opts.n_pairs

for n_vars in range(opts.min_n, opts.max_n + 1):

    n_pairs = min(
        n_pairs_rem,
        random.randint(n_pairs_per_var * (1.0 - batch_range),
                       n_pairs_per_var * (1.0 + batch_range)))

    for pair in range(n_pairs):

        gen_opts.min_n = n_vars
        gen_opts.max_n = n_vars
        _, iclauses_unsat, iclauses_sat = gen_iclause_pair2(gen_opts)

    for iclauses in (iclauses_unsat, iclauses_sat):
        n_clauses = len(iclauses)
        n_cells = sum([len(iclause) for iclause in iclauses])

        n_nodes = 2 * n_vars + n_clauses
        if n_nodes > opts.max_nodes_per_batch:
            continue

        batch_ready = False
        if (opts.one and len(problems) > 0):
            batch_ready = True
        elif (prev_n_vars and n_vars != prev_n_vars):
            batch_ready = True
        elif (not opts.one) and n_nodes_in_batch + n_nodes > opts.max_nodes_per_batch:
            batch_ready = True

        if batch_ready:
            batches.append(mk_batch_problem(problems))
            print("batch %d done (%d vars, %d problems)...\n" % (len(batches), n_vars, len(problems)))
            del problems[:]
            n_nodes_in_batch = 0

        prev_n_vars = n_vars

        is_sat, stats = solve_sat(n_vars, iclauses)
        problems.append((filename, n_vars, iclauses, is_sat))
        n_nodes_in_batch += n_nodes

if len(problems) > 0:
    batches.append(mk_batch_problem(problems))
    print("batch %d done (%d vars, %d problems)...\n" % (len(batches), n_vars, len(problems)))
    del problems[:]

# create directory
if not os.path.exists(opts.out_dir):
    os.mkdir(opts.out_dir)

dataset_filename = mk_dataset_filename(opts, len(batches))
print("Writing %d batches to %s...\n" % (len(batches), dataset_filename))
with open(dataset_filename, 'wb') as f_dump:
    pickle.dump(batches, f_dump)
