
from typing import Dict, List, Tuple, Union, Callable, Set, cast


import random
import math
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
    for i in range(len(lst)-1):
        value += distances[lst[i]][lst[i+1]]
    value += distances[lst[-1]][0]
    value += distances[0][lst[0]]
    return value








class Particle (object):
    """
    An instance of this class represents a particle used in this algorithm.

    """
    
    def __init__(self,
                distances : Dict[int, Dict[int,int]],
                picking_list : List[int],
                w : float,
                C1 : float,
                C2 : float

                ) -> None:

        '''
        :param deepsearch: Probability to do deep search and, if so, probability to do full deep search  
        :param max_depth: Maximum number of iteration in case of deep search
        :param w: Velocity weigths {'g' for the gbest, 'gr' for the greedy, 'p' for the pbest, 'i' for the intention}
        :param accepted_err: The accepted deterioration of the current position if worse than the
                            current pbest. It prevents the particle to deteriorate.

        :attr current: The current solution.
        :attr intention: The current intention.
        :attr pbest: The current personal best found do far.
        :attr vcurrent: The cost of the current.
        :attr vintention: The cost of the intention.
        :attr vpbest: The cost of the personal best.

        :attr no_imp: The number of iterations with no improvement.

        '''
        
        # set parameters
        self.distances = dict(distances)
        self.picking_list = list(picking_list)

        self.w = w
        self.C1 = C1
        self.C2 = C2

        self.no_imp : int = 0
        


        # starting solutions
        self.current = list(picking_list)
        random.shuffle(self.current)

        # personal best
        self.pbest = list(self.current)
        self.vpbest = _compute_distance(self.pbest, distances)


        # greedy solution
        self.greedy = self.greedy_solution()
        self.greedy_speed = self.difference (self.current, self.greedy)


        # speed
        rnd = list(picking_list)
        random.shuffle(rnd)
        self.speed = self.difference (self.current, rnd)




    @staticmethod
    def difference (sol1 : List[int], sol2 : List[int]) -> Dict[int,int]:
        """
        This method calculates the speed as the difference between two
        sequences.
        The speed is defined as the number of shifts on the right (+) or
        on the left (-) that each node of sol1 has to do, to turn sol1 
        into sol2.

        :param sol1: First solution.
        :param sol2: Second solution.
        :return: The speed.

        """
        speed : Dict[int,int] = {}
        for pos, node in enumerate(sol1):
            newpos = sol2.index (node)
            speed[node] = newpos - pos

        return speed





    def greedy_solution (self) -> List[int]:
        """
        This method calculates the greedy solution.

        """
        c_node : int = 0
        sol : List[int] = []
        options = list(self.picking_list)

        while len(options) > 0:
            c_node = sorted(options, key=lambda i: self.distances[c_node][i])[0]
            options.remove(c_node)
            sol.append (c_node)

        return sol



                        

    


    def move (self, gbest : List[int], vgbest : int) -> Tuple[List[int], int]:
        """
        This method represents the movement of the particle.

        """
        new_solution = [-1 for i in range(len(self.picking_list))]
        
        for pos, node in enumerate(self.current):
            
            i, j = max(0, min(pos + self.speed[node], len(self.picking_list) - 1)), max(0, min(pos + self.speed[node], len(self.picking_list) - 1))
            
            
            while new_solution[i] != -1 and new_solution[j] != -1:
                i, j = max(i - 1, 0), min(j + 1, len(self.picking_list) - 1)


            if new_solution[i] == -1 and new_solution[j] == -1:
                selected = random.choice([i, j])
                new_solution[selected] = node
            elif new_solution[i] == -1 and new_solution[j] != -1:
                new_solution[i] = node
            else:
                new_solution[j] = node

        # Calculate the cost of the new solution
        self.current = new_solution
        cost = _compute_distance (self.current, self.distances)



        # Eventually update pbest
        if cost < self.vpbest:
            self.pbest, self.vpbest = list(self.current), cost


        # Update speed
        v1 : Dict[int, int] = self.difference (self.current, self.pbest)
        v2 : Dict[int, int] = self.difference (self.current, gbest)

        new_speed : Dict[int,int] = {}

        for node in self.picking_list:
            c1 = random.random() * self.C1
            c2 = random.random() * self.C2 
            winner = max (self.w, c1, c2)

            if winner == self.w:
                new_speed[node] = self.speed[node]
            elif winner == c1:
                new_speed[node] = v1[node]
            else:
                new_speed[node] = v2[node]

        self.speed = new_speed

                
                

        return self.pbest, self.vpbest











            


class SpeedPSO:
    """
    An instance of this class represents the Particle Swarm Optimization designed by Mattia in December 2019.

    An Hibrid PSO for TSP
    Solution is generated node by node
    selecting from four possibilities, namely: current solution, particle best, overall best
    and intention; the latter one is a random sequence.
    Say that the generated sequence is 1-3-4 and the alternative are:
    1-2-3-4-5; 5-4-3-2-1; 3-2-1-5-4; 5-4-1-2-3
    so "suggested nodes" are: (5, 3, nan, 1), since 3 is already in, (5,1) remain
    choice depends (in a probabilistic way on the corrected distance from 3 to 5 and to 1 to 5
    the less the better. Distance is corrected with weigth used to give more importance
    to the current solution, then to the best and so on. 

    This is the basic generation scheme. Solution may be shaked (using a first level or
    deep level 2Opt Procedure)


    """

    def __init__ (self,*,
                distances : Dict[int, Dict[int,int]],
                picking_list : List[int],
                era : int = 10_000,
                particles : int = 40,
                w : float = 0.8,
                C1 : float = 2.0,
                C2 : float = 2.0,
                max_noimp : int = 1000,
                print_every : int = 100,
        ) -> None:
        """
        Initialize.
        
        :param distances: The distance matrix.
        :param era: The number of iterations.
        :param particles: The number of particles.
        :param max_noimp: The maximum number of iterations with no getting any improvement.
        :param print_every: The number of iterations between a log and the next one.

        :attr history: The history of the best solutions found by the algorithm.
        :attr computations: The number of iterations needed to find the best.

        """

        self.era = era
        self.max_noimp = max_noimp
        self.print_every = print_every
        
        self.distances = distances
        self.particles = particles
        self.picking_list = picking_list
        self.w = w
        self.C1 = C1
        self.C2 = C2
        
        self.swarm : List[Particle] = [Particle(distances, picking_list, w, C1, C2) for _ in range(particles)]        

        self.history : List[int]
        self.computations : int = 0
        self.computational_time : float = 0.0
    
    
    def reset (self):
        self.swarm = [Particle(self.distances, self.picking_list, self.w, self.C1, self.C2) for _ in range(self.particles)]
        self.history = []
        self.computations = 0
        self.computational_time = 0.0
    
    
    
    def run (self, verbose : bool = False) -> Tuple[List[int], int]:
        """
        This is the method to execute the algorithm.
        It finally returns the best solution found and its cost.

        :return: gbest, vgbest

        """
        start = time.time()

        # Initilaize the best starting position
        gbest : List[int]
        vgbest : int = cast(int, float("inf"))
        for particle in self.swarm:
            if particle.vpbest < vgbest:
                gbest, vgbest = list(particle.pbest), particle.vpbest
                
        new_vgbest : int = vgbest
        new_gbest : List[int] = list(gbest)
        
        self.history = [vgbest]

        # Iterations
        noimp = 0
        for i in range(self.era):
            for particle in self.swarm:
                pbest, vpbest = particle.move (gbest, vgbest)
                if vpbest < new_vgbest:
                    new_gbest, new_vgbest = list(pbest), vpbest

            if new_vgbest < vgbest:
                gbest, vgbest = new_gbest, new_vgbest
                noimp = 0
                self.computations = i * len(self.swarm)
            else:
                noimp += 1
                if noimp > self.max_noimp:
                    break

            self.history.append(vgbest)

            if i % self.print_every == 0 and verbose is True:
                print('Epoch', i, ' Best: ', vgbest)
                
        # Set the computational time
        self.computational_time = time.time() - start

        return gbest, vgbest