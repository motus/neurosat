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
import numpy as np
import random
import datetime
import subprocess
import pickle
import sys
import os
import time
import glob
import argparse
from options import add_neurosat_options
from neurosat import NeuroSAT

parser = argparse.ArgumentParser()
add_neurosat_options(parser)

parser.add_argument('solve_dir', action='store', type=str)
parser.add_argument('restore_id', action='store', type=int)
parser.add_argument('restore_epoch', action='store', type=int)
parser.add_argument('n_rounds', action='store', type=int)
parser.add_argument('n_outer_rounds', action='store', type=int)
parser.add_argument('--limit_examples', action='store', type=int, default=0)

opts = parser.parse_args()
setattr(opts, 'run_id', None)
setattr(opts, 'n_saves_to_keep', 1)

print(opts)

g = NeuroSAT(opts)
g.restore()

# filenames = [opts.solve_dir + "/" + f for f in os.listdir(opts.solve_dir)]
filenames = glob.glob(opts.solve_dir + '/*', recursive=True)

for filename in filenames:

    with open(filename, 'rb') as f:
        problems = pickle.load(f)

    total_examples = 0
    for i, problem in enumerate(problems, 1):

        solutions = None
        init_L_h, init_L_c, init_C_h, init_C_c = None, None, None, None

        start = time.clock()
        for iter_index in range(opts.n_outer_rounds):
            print("Round %4d of %d..." % (iter_index + 1, opts.n_outer_rounds), end='\r')
            solutions, init_L_h, init_L_c, init_C_h, init_C_c = \
                g.find_solutions(problem, iter_index,
                                 init_L_h, init_L_c, init_C_h, init_C_c, solutions)

        print()
        num_solutions = 0
        for batch, solution in enumerate(solutions):
            print("[%s] %s" % (problem.dimacs[batch], str(solution)))
            if solution[0] and solution[2] is not None:
                num_solutions += 1

        print("%s batch %d/%d: %d/%d=%.2f%% solved. %d rounds ran in %.2f s" % (
            filename, i, len(problems), num_solutions, len(solutions),
            num_solutions * 100.0 / len(solutions), opts.n_outer_rounds, time.clock() - start))

        total_examples += len(solutions)
        if opts.limit_examples > 0 and total_examples >= opts.limit_examples:
            break
