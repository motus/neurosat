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
import argparse
from options import add_neurosat_options
from neurosat import NeuroSAT

parser = argparse.ArgumentParser()
add_neurosat_options(parser)

parser.add_argument('solve_dir', action='store', type=str)
parser.add_argument('restore_id', action='store', type=int)
parser.add_argument('restore_epoch', action='store', type=int)
parser.add_argument('n_rounds', action='store', type=int)

opts = parser.parse_args()
setattr(opts, 'run_id', None)
setattr(opts, 'n_saves_to_keep', 1)

print(opts)

g = NeuroSAT(opts)
g.restore()

outer_rounds = opts.n_rounds
opts.n_rounds = 1

filenames = [opts.solve_dir + "/" + f for f in os.listdir(opts.solve_dir)]

for filename in filenames:

    with open(filename, 'rb') as f:
        problems = pickle.load(f)

    for i, problem in enumerate(problems, 1):

        solutions = None
        init_L_h, init_L_c, init_C_h, init_C_c = None, None, None, None

        start = time.clock()
        for iter_index in range(outer_rounds):
            solutions, init_L_h, init_L_c, init_C_h, init_C_c = \
                g.find_solutions(problem, iter_index,
                                 init_L_h, init_L_c, init_C_h, init_C_c, solutions)

        num_solutions = 0
        for batch, solution in enumerate(solutions):
            print("[%s] %s" % (problem.dimacs[batch], str(solution)))
            if solution[0] and solution[2] is not None:
                num_solutions += 1

        print("Batch %5d of %d: %d of %d solutions found. %d rounds ran in %.2f s" % (
            i, len(problems), num_solutions, len(solutions), outer_rounds, time.clock() - start))
