# The class Race written in this file can be used 
# for parallel computing, testing different algorithms
# at the same time.
#
#
#

from multiprocessing import Pool

import random
import numpy as np


def worker(args):
    random.seed(None)
    np.random.seed(None)

    solver, _, n = args
    
    print(f"{solver.__class__.__name__} [{_+1}/{n}]")
    
    solver.reset()
    best, best_c = solver.run()
    
    return {"alg" : solver.__class__.__name__, "cost" : best_c, "computations" : solver.computations, "computational_time" : solver.computational_time, "solution" : best, "history" : list(solver.history)}


class Race:
    def __init__(self, solvers):
        self.solvers = solvers
        self.__results = []

    def __call__(self, n=2):
        self.n = n
        self.results = self._parallel()
        return self

    @property
    def todo(self):
        for solver in self.solvers:
            for _ in range(self.n):
                yield (solver, _, self.n)

    @property
    def results(self):
        return self.__results

    @results.setter
    def results(self, value):
        self.__results = value

    def _parallel(self):

        results = []
        pool = Pool()
        multiple_results = pool.map_async(worker, self.todo, callback=results.extend)
        multiple_results.wait()

        return results
