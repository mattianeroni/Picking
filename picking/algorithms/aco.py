

from typing import List, Tuple, Dict, Set, Optional

import random
import numpy as np # type: ignore
import time







def _compute_distance (lst : List[int], distances : List[List[int]]) -> int:
    """
    Given a picking list and a distance matrix, this method calculates the 
    distance ran to complete the picking list.

    :param lst: The picking list
    :param distances: The distance matrix
    :return: The distance ran.

    """
    value : int = 0
    for i in range(len(lst) - 1):
        value += distances[lst[i]][lst[i+1]]
    value += distances[lst[-1]][0]
    value += distances[0][lst[0]]
    return value








class AntColony (object):
    """
    This is the Ant Colony Optimization algorithm described by DeSanctis et al. (2018).

    """

    def __init__ (self,
                distances : Dict[int, Dict[int,int]],
                picking_list : List[int],
                pher_init : float = 0.1,
                ro : float = 0.9,
                Q : float = 2.0,
                alpha : float = 1.0,
                beta : float = 5.0,
                evaporate : bool = False,
                max_iter : Optional[int] = None,
                max_noimp : int = 1000,
                print_every : int = 100
                ) -> None:
        """
        Initialize.

        :attr distances: The distance matrix.
        :attr ro: A parameter that defines the evaporation of the pheromone.
        :attr Q: A parameter that defines the increment of the pheromone on
                the new best path.
        :attr alpha, beta: Parameters of the empirical distribution used to 
                            select the next node at each step.
        :attr evaporate: If TRUE the pheromone evaporates at every iteration,
                        otherwise only when a better best solution is found.
        :attr max_iter: The number of iterations.
        :attr max_noimp: Maximum number of iterations without improvement.
        :attr print_every: The iterations between a log and the next one.

        :attr pheromone: The pheromone on each arch.
        :attr best: The best solution found so far.
        :attr vbest: the cost of the current best.
        :attr history: The history of the best solutions found.
        :attr computations: The number of solutions explored before finding the best.

        :param pher_init: The initial pheromone (it is always 0 on arcs (i,j) where i == j)
        
        """
        self.distances = distances
        self.picking_list = picking_list
        self.ro = ro
        self.Q = Q
        self.alpha = alpha
        self.beta = beta
        self.evaporate = evaporate
        self.max_iter = max_iter or len(distances) * 100
        self.max_noimp = max_noimp
        self.print_every = print_every
        self.pher_init = pher_init


        # Initialize the best
        self.best : List[int] = list(self.picking_list)
        random.shuffle(self.best)
        self.vbest : int = _compute_distance (self.best, distances)

        # Initialize the pheromone
        self.pheromone : Dict[int, Dict[int, float]] = {}
        for i in distances:
            self.pheromone[i] = {}
            for j in distances:
                if i != j:
                    self.pheromone[i][j] = pher_init
                else:
                    self.pheromone[i][j] = 0

        # Initialize the history and the number of iterations
        # needed to find the best.
        self.history : List[int] = [self.vbest]
        self.computations : int = 0
        self.computational_time : float = 0.0








    def _evap (self) -> None:
        """
        This method evaporates the pheromone.

        """
        for i in self.distances:
            for j in self.distances:
                self.pheromone[i][j] *= self.ro







    def _update (self) -> None:
        """
        This method updates the pheromone on the best path.
        In the next iterations, higher is the pheromone on an arc,
        greater is the possibility to select it.

        """
        for i in range (len(self.picking_list) - 1):
            self.pheromone[self.best[i]][self.best[i + 1]] += (self.Q / self.distances[self.best[i]][self.best[i + 1]])
        self.pheromone[0][self.best[0]] += (self.Q / self.distances[0][self.best[0]])
        self.pheromone[self.best[-1]][0] += (self.Q / self.distances[self.best[-1]][0])





    def _next_node (self, options : List[Tuple[int,float]]) -> int:
        """
        This method returns the next node during the constructing process that 
        brings to a new solution.

        The node is selected in a list of possible <options>. Each option is given
        by a tuple containing (the node, its desirability).

        Given i the current node, the desirability of node j (i.e. d(j)) is
        calculated as follows:

        d(j) = ph(i,j)^alpha / dist(i,j)^beta

        where alpha and beta are parameters of the algorithm, dist(i,j) is the
        distance from i to j, and ph(i,j) is the pheromone on the edge (i,j).

        The probability to select a node is calculated dividing its desirability
        for the total desirability of all the options.        


        :param options: List of tuples (node, desirability of node).
        :return: The selected node.

        """
        p : float = 0.0
        r = random.random()
        total = sum (op[1] for op in sorted(options, key=lambda i : i[1], reverse=True))

        for op, prob in options:
            p += prob/total
            if r < p:
                return op
        return -1









    def _new_solution (self) -> Tuple[List[int], int]:
        """
        This method construct node by node a new solution.

        :return: The new solution and its cost.

        """
        c_node = 0
        new_sol : List[int] = []; vnew_sol : int = 0
        tabu : Set[int] = {0}
        options : List[int] = list(self.picking_list)

        for i in range (len(self.picking_list)):
            options_params : List[Tuple[int,float]] = [(op, self.pheromone[c_node][op]**self.alpha / self.distances[c_node][op]**self.beta) for op in options]
            n_node = self._next_node (options_params)
            tabu.add (n_node)
            new_sol.append(n_node)
            options.remove (n_node)
            vnew_sol += self.distances[c_node][n_node]
            c_node = n_node
        vnew_sol += self.distances[c_node][0]

        return new_sol, vnew_sol

    
    
    def reset (self):
        # Initialize the best
        self.best = list(self.picking_list)
        random.shuffle(self.best)
        self.vbest = _compute_distance (self.best, self.distances)

        # Initialize the pheromone
        for i in self.distances:
            for j in self.distances:
                if i != j:
                    self.pheromone[i][j] = self.pher_init
                else:
                    self.pheromone[i][j] = 0

        # Initialize the history and the number of iterations
        # needed to find the best.
        self.history = [self.vbest]
        self.computations = 0
        self.computational_time = 0.0






    def run (self, verbose : bool = False) -> Tuple[List[int], int]:
        """
        This method represents the execution of the algorithm.

        :param verbose: If TRUE a log takes place every <print_every> iterations.
        :return: The best solution and its cost.

        """
        start = time.time()
        noimp : int = 0
        for i in range (self.max_iter):
            
            # Build a new solution
            new_sol, vnew_sol = self._new_solution ()

            # Eventually evaporate pheromone
            if self.evaporate is True:
                self._evap ()

            # Eventually update best, iterations with no improvement
            # and computations needed to find the best.
            if vnew_sol < self.vbest:
                self.best, self.vbest = new_sol, vnew_sol
                self._evap ()
                self._update ()
                noimp = 0
                self.computations = i
            else:
                noimp += 1
                if noimp > self.max_noimp:
                    break

            # Update history
            self.history.append (self.vbest)

            # Logs
            if verbose is True and i % self.print_every == 0:
                print('Epoch', i, ' Best: ', self.vbest)
                
        # Set computational time
        self.computational_time = time.time() - start

        return self.best, self.vbest