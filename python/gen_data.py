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
from gen_sr_dimacs import init_opts, gen_iclause_pair_n_vars


def get_splits(n_pairs, min_n, max_n):
    return list(zip(
        range(min_n, max_n),
        sorted(random.randint(0, n_pairs)
               for _ in range(max_n - min_n)))) + [(max_n, n_pairs)]


def mk_dataset_filename(opts, n_batches, n_file, n_problems):
    return "%s/f=%03dnpb=%d_nb=%04d_p=%06d.pkl" % (
        opts.out_dir, n_file, opts.max_nodes_per_batch, n_batches, n_problems)


parser = argparse.ArgumentParser()
parser.add_argument('--max_nodes_per_batch', type=int)
parser.add_argument('--n_files', type=int, default=1, help='Number of files to generate')


opts = init_opts(parser)

# create directory
if not os.path.exists(opts.out_dir):
    os.mkdir(opts.out_dir)

n_problems_total = 0

for n_file in range(opts.n_files):

    batches = []
    problems = []
    n_problems = 0
    n_batch = 1
    n_nodes_in_batch = 0

    for n_vars, total_pairs in get_splits(opts.n_pairs, opts.min_n, opts.max_n):

        prev_pairs = 0
        for pair in range(total_pairs - prev_pairs + 1):

            iclauses_unsat, iclauses_sat = gen_iclause_pair_n_vars(opts, n_vars)

            n_clauses = len(iclauses_sat)  # same number for sat/unsat
            n_cells = sum([len(iclause) for iclause in iclauses_sat])
            n_nodes = 2 * n_vars + n_clauses

            if n_nodes > opts.max_nodes_per_batch:
                continue

            for iclauses in (iclauses_unsat, iclauses_sat):

                is_sat, stats = solve_sat(n_vars, iclauses)
                problems.append((
                    "problem=%08d_vars=%02d_sat=%d" % (n_problems, n_vars, is_sat),
                    n_vars, iclauses, is_sat))
                n_problems += 1
                n_problems_total += 1
                n_nodes_in_batch += n_nodes

                if n_nodes_in_batch >= opts.max_nodes_per_batch:
                    batches.append(mk_batch_problem(problems))
                    print("batch %4d done (%2d vars, %6d problems)..." % (n_batch, n_vars, len(problems)))
                    problems = []
                    n_nodes_in_batch = 0
                    n_batch += 1

        prev_pairs = total_pairs

        if problems:
            batches.append(mk_batch_problem(problems))
            print("batch %4d done (%2d vars, %6d problems)..." % (n_batch, n_vars, len(problems)))
            problems = []
            n_nodes_in_batch = 0
            n_batch += 1

    if batches:
        dataset_filename = mk_dataset_filename(opts, len(batches), n_file, n_problems)
        print("# Writing %d batches and %d problems to %s..."
              % (len(batches), n_problems, dataset_filename))
        random.shuffle(batches)
        with open(dataset_filename, 'wb') as f_dump:
            pickle.dump(batches, f_dump)

print("Done! Generated %d problems." % n_problems_total)
