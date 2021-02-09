from typing import List, Dict, Tuple, Callable, Set, Union, cast

import random
import numpy as np # type: ignore
import itertools
import time






def _random_velocity (nodes : int) -> List[Tuple[int,int]]:
    """
    This method is used to generate a random velocity: a list of swaps
    to change a solution.

    :param nodes: The number of nodes that might be swapped.
    :return: A list of swaps, represented by tuples. Each tuple reports
            the index in the picking list of the swapped nodes.

    """
    tabu : Set[Tuple[int,int]] = {(i, i) for i in range (nodes)}
    swaps : List[Tuple[int,int]] = []
    while len(swaps) < nodes:
        sw = (random.randint(0, nodes-1), random.randint(0, nodes-1))
        if not sw in tabu:
            swaps.append (sw)
            tabu.add (sw)

    return swaps










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










def _subtract (seq1 : List[int], seq2 : List[int]) -> List[Tuple[int,int]]:
    """
    This method represents the subtraction operator used by Zhou.
    Given two sequences of nodes, it returns the list of swaps needed
    to make a sequence equal to the other.

    :param seq1: First solution.
    :param seq2: Second solution.
    :return: The swaps needed to make swap1 == swap2.

    """
    s1, s2 = np.array(list(seq1)), np.array(list(seq2))
    swaps = []
    i = 0
    while not all(s1 == s2):
        if not i in np.where(s1 == s2)[0]:
            j = np.where (s1 == s2[i])[0][0]
            swaps.append ((i, j))
            s1[i], s1[j] = s1[j], s1[i]
        i += 1

    return swaps









def _product (weight : float, swaps : List[Tuple[int,int]]) -> List[Tuple[int,int]]:
    """
    This method represents the product operator used by Zhou.

    :param weight: The weight assigned to that component of the speed
    :param swaps: The swaps in the velocity.
    :return: A new list of swaps.

    """
    return [(round(weight * i), round(weight * j)) for i, j in swaps]









def _sum (v1 : List[Tuple[int,int]], v2 : List[Tuple[int,int]]) -> List[Tuple[int,int]]:
    """
    This method represents the sum operator between velocities used by Zhou.

    :param v1: First list of swaps.
    :param v2: Second list of swaps.

    :raturn: Another list of swaps.

    """
    swaps = []
    for s1, s2 in itertools.zip_longest(v1, v2, fillvalue=None):
        if s1 is None:
            swaps.append (s2)
        elif s2 is None:
            swaps.append (s1)
        else:
            swaps.append ( (int(np.ceil((s1[0] + s2[0]) / 2)) , int(np.ceil((s1[1] + s2[1]) / 2))) )

    return swaps












class Particle (object):
    """
    An instance of this class represents a particle used in the 
    algorithm by Zhou.

    """

    def __init__ (self,
                distances : Dict[int, Dict[int,int]],
                picking_list : List[int],
                alpha : float,
                beta : float,
                gamma : float,
                new_version : bool = True
                ) -> None:
        """
        Initialize.

        :attr distances: The distance matrix.
        :attr picking_list: The picking list.
        :attr alpha: The parameter <alpha> (i.e. probability to turn into the gbest).
        :attr beta: The parameter <beta> (i.e. probability to turn into the pbest).
        :attr gamma: The parameter <gamma> (i.e. probability relative to the current velocity).
        :attr new_version: If TRUE the new version of the algorithm is used, otherwise is used Zhou2007

        :attr current: The current solution.
        :attr pbest: The personal best found so far.
        :attr vcurrent: The cost of the current.
        :attr vpbest: The cost of the pbest.
        :attr v: The current velocity.

        """
        self.distances = distances
        self.picking_list = picking_list
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.new_version = new_version

        self.current : List[int] = list(picking_list)
        random.shuffle (self.current)
        self.vcurrent = _compute_distance (self.current, distances)

        self.pbest : List[int] = list(self.current)
        self.vpbest : int = self.vcurrent

        self.velocity : List[Tuple[int,int]] = _random_velocity(len(picking_list))








    def move (self, gbest : List[int], vgbest : int) -> Tuple[List[int], int]:
        """
        This method represents the movement of the particle.

        :param gbest: The current globar best.
        :param vgbest: The cost of the current global best.

        :return: The current personal best and its cost.

        """
        
        # Move according to the current velocity
        for i, j in self.velocity:
            self.current[i], self.current[j] = self.current[j], self.current[i]

        # Evaluate the new solution and eventually update the pbest
        self.vcurrent = _compute_distance (self.current, self.distances)
        if self.vcurrent < self.vpbest:
            self.pbest, self.vpbest = list(self.current), self.vcurrent

        # Calculate the new velocity
        gamma : float; beta : float; alpha : float
        if self.new_version is True:
            gamma = self.gamma
            alpha = self.alpha * random.random()
            beta = self.beta * random.random()
        else:
            gamma = 1.0
            alpha = self.alpha
            beta = self.beta

        new_velocity = _sum (_product(gamma, self.velocity), _sum (_product (alpha, _subtract (self.current, gbest)), _product (beta, _subtract (self.current, self.pbest))))
        
        # Compute the sequence which would be obtained using the new velocity on the current one
        intention = list(self.current)
        for i, j in new_velocity:
            intention[i], intention[j] = intention[j], intention[i]
        
        # Calculate the new velocity using the minimum number of swaps needed
        self.velocity = _subtract (self.current, intention)

        return self.pbest, self.vpbest
















class Zhou_PSO (object):
    '''
    A Particle Swarm Optimization designed for the Travelling Salesman Problem.

    The particularity of this implementation lays in the calculation of the distance
    between two tours (e.g. T1 and T2); it is defined as the minimum number of 
    swap operations needed to turn T1 into T2.
    
    The velocity is therefore defined as a minimal set of swap operations, and it
    is updated as follows.
    
    V(t) = gamma * V(t-1) + r * alpha * (current - gbest) + r * beta * (current - pbest)

    where r is a random number between 0 and 1, <gamma>, <alpha> and <beta> are the probabilities
    to keep the swap operation defined by the corresponding distances (parameters of the algorithm).

    In this way, the new new velocity might not be a minimal set. In this case, the minimal
    set is firstly obtained and then the velocity is updated.

    '''

    def __init__ (self, *,
                distances : Dict[int, Dict[int,int]],
                picking_list : List[int],
                particles : int = 30,
                alpha : float = 0.4,
                beta : float = 0.2,
                gamma : float = 1.0,
                max_iter : int = 10000,
                max_noimp : int = 1000,
                print_every : int = 100,
                new_version : bool = True

                ) -> None:
        """
        Initialize.

        :attr max_iter: The number of iterations.
        :attr max_noimp: The max number of iterations with no improvement.
        :attr print_every: The number of iterations between a log and the next.
        :attr history: The history of the best solutions found.
        :attr computations: The number of iterations needed to find the best.
        
        :param particles: The number of particles.
        :param distances: The distance matrix.

        """
        self.swarm : List[Particle] = [Particle(distances, picking_list, alpha, beta, gamma, new_version) for _ in range(particles)]
        
        self.max_iter = max_iter
        self.max_noimp = max_noimp
        self.print_every = print_every
        
        self.particles = particles
        self.particle_data = {"distances" : distances,
                              "picking_list": picking_list,
                              "alpha":alpha,
                              "beta": beta,
                              "gamma": gamma,
                              "new_version": new_version
                             }

        self.history : List[int]
        self.computations : int = 0
        self.computational_time : float = 0.0
            
            
    
    def reset (self):
        self.history = []
        self.computations = 0
        self.computational_time = 0.0
        self.swarm = [Particle(**self.particle_data) for _ in range(self.particles)]





    def run (self, verbose : bool = False) -> Tuple[List[int], int]:
        """
        This method represents the execution of the algorithm.

        :param verbose: If TRUE every <print_every> iterations a log takes place.
        :return: The gbest and its cost.

        """
        # Initialise the starting time
        start = time.time()

        # Initialize the gbest
        gbest : List[int]; vgbest : int = cast(int, float("inf"))
        for p in self.swarm:
            if p.vpbest < vgbest:
                gbest, vgbest = list(p.pbest), p.vpbest
        new_gbest, new_vgbest = list(gbest), vgbest
        self.history = [vgbest]

        # Iterate
        noimp : int = 0
        for i in range (self.max_iter):

            # Move particles
            for p in self.swarm:
                sol, cost = p.move (gbest, vgbest)
                if cost < new_vgbest:
                    new_gbest, new_vgbest = list(sol), cost

            # Update the old_vgbest and check an eventual improvement
            if new_vgbest < vgbest:
                self.computations = i * len(self.swarm)
                noimp = 0
                gbest, vgbest = list(new_gbest), new_vgbest
            else:
                noimp += 1
                # Eventually breaks if no improvement for long time
                if noimp >= self.max_noimp:
                    break

            # Save in the history this iteration
            self.history.append (vgbest)

            # Logs
            if i % self.print_every == 0 and verbose is True:
                print('Epoch', i, ' Best: ', vgbest)
                
        # Set the computational time
        self.computational_time = time.time() - start

        return gbest, vgbest