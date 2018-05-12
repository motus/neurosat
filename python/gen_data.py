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


def get_splits(n_pairs, min_n, max_n):
    return list(zip(range(min_n, max_n),
                    sorted(random.randint(0, n_pairs)
                           for _ in range(max_n - min_n)))) \
           + [(max_n, n_pairs)]


def mk_dataset_filename(opts, n_batches, n_file):
    return "%s/f=%03dnpb=%d_nb=%04d.pkl" % (opts.out_dir, n_file, opts.max_nodes_per_batch, n_batches)


parser = argparse.ArgumentParser()
parser.add_argument('--max_nodes_per_batch', action='store', type=int)
parser.add_argument('--max_batches_per_file', action='store', type=int, default=1000)
parser.add_argument('--one', action='store', dest='one', type=int, default=0)

opts = init_opts(parser)


# create directory
if not os.path.exists(opts.out_dir):
    os.mkdir(opts.out_dir)


batches = []
problems = []
n_batch = 1
n_file = 1
n_nodes_in_batch = 0

gen_opts = GenerationOpts(opts)
prev_pairs = 0

for n_vars, total_pairs in get_splits(opts.n_pairs, opts.min_n, opts.max_n):

    for pair in range(total_pairs - prev_pairs + 1):

        gen_opts.min_n = n_vars
        gen_opts.max_n = n_vars
        _, iclauses_unsat, iclauses_sat = gen_iclause_pair2(gen_opts)

        n_clauses = len(iclauses_sat)  # same number for sat/unsat
        n_cells = sum([len(iclause) for iclause in iclauses_sat])
        n_nodes = 2 * n_vars + n_clauses

        if n_nodes > opts.max_nodes_per_batch:
            continue

        for iclauses in (iclauses_unsat, iclauses_sat):

            is_sat, stats = solve_sat(n_vars, iclauses)
            problems.append((None, n_vars, iclauses, is_sat))
            n_nodes_in_batch += n_nodes

            if opts.one or n_nodes_in_batch >= opts.max_nodes_per_batch:
                batches.append(mk_batch_problem(problems))
                print("batch %4d done (%2d vars, %6d problems)..." % (n_batch, n_vars, len(problems)))
                problems = []
                n_nodes_in_batch = 0
                n_batch += 1

                if len(batches) >= opts.max_batches_per_file:
                    dataset_filename = mk_dataset_filename(opts, len(batches), n_file)
                    print("# Writing %d batches to %s..." % (len(batches), dataset_filename))
                    with open(dataset_filename, 'wb') as f_dump:
                        pickle.dump(batches, f_dump)
                    batches = []
                    n_file += 1

    prev_pairs = total_pairs

    if problems:
        batches.append(mk_batch_problem(problems))
        print("batch %4d done (%2d vars, %6d problems)..." % (n_batch, n_vars, len(problems)))
        problems = []
        n_nodes_in_batch = 0
        n_batch += 1

if len(batches):
    dataset_filename = mk_dataset_filename(opts, len(batches), n_file)
    print("# Writing %d batches to %s..." % (len(batches), dataset_filename))
    with open(dataset_filename, 'wb') as f_dump:
        pickle.dump(batches, f_dump)
    batches = []
    n_file += 1
