
from typing import Dict, List, Tuple, Union, Callable, Set, cast


import random
import math
import time








def _bra (lst : List[int], beta : float = 0.3) -> int:
    """
    The estraction of an item from a list, by using a biased randomisation based
    on a quasi-geometric distribution (i.e. f(x) = (1-beta)^x).

    :param beta: The parameter of the quasi-geometric.
    :return: The estracted element.

    """
    return lst[int(math.log(random.random(), 1 - beta)) % len(lst)]





def _triangular (lst : List[int]) -> int:
    """
    The estraction of an item from a list, by using a triangular distribution.
    :return: The estracted element.

    """
    return lst[int(len(lst) - len(lst)*random.random()/2) % len(lst)]






def _make_negative_exp (max_iter : int = 1000, max_v : float = 1.0, min_v : float = 0.5) -> Callable[[int],float]:
    """
    This method generates an exponential function used to increase the weight 
    given to the current position of the particle.
    As the number of iterations increase, the particles get more and more static.

    ***Note*** : Lower is the value of the weight, grater is the relevance given to
    the current position of the particles. Hence, for a low weight, the particles are
    more static. As the number of iterations without improvement increases, the 
    mobility of the particles increases too.

    :param max_iter: The maximum number of iterations
    :param max_v: The maximum value the weight of the current position must assume
    :param min_v: The minimum value the weight of the current position must assume
    :return: A callable function which represents the exponential needed.

    def negative_exp (x : int) -> float

        :param x: The current iteration without improvement.
        :return: The weight of the current position of the particles.

    """
    alpha = math.log(max_v + min_v)/max_iter

    def negative_exp (x : int) -> float:
        return math.exp(alpha * x) - min_v

    return negative_exp








def _negative_exp (x : int, alpha : float) -> float:
    """
    This method return the negative exponential according to equation
                        
                        f(x) = e^(-alpha*x)
    
    :param x: The input.
    :param alpha: The parameter of the exponential (the higher is alpha, the
                    faster is the decrease).
    :return: The output f(x).
    
    """
    return math.exp(-alpha*x)







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








def _two_opt (lst : List[int], i : int, j : int) -> List[int]:
    """
    This method, given two cutting positions i and j, makes a 2-Opt on the
    starting list.
    
    :param lst: The starting list.
    :param i: First cutting point.
    :param j: Second cutting point.
    :return: The new list.

    """
    return lst[:min(i,j)] + list(reversed(lst[min(i,j):max(i,j)])) + lst[max(i,j):]








def _greedy (lst : List[int], distances : List[List[int]]) -> List[int]:
    """
    This method returns a purely greedy solution.

    :param lst: The list of nodes to visit.
    :param distances: The distance matrix.
    :return: The nodes in the order in which they should be visited.
    
    """
    c_node = 0; sol : List[int] = []; options = list(lst)
    while len(options) > 0:
        options = sorted(options, key=lambda i: distances[c_node][i])
        c_node = options.pop(0)
        sol.append (c_node)

    return sol








class Particle (object):
    """
    An instance of this class represents a particle used in this algorithm.

    """

    def __init__(self, *,
                distances : Dict[int, Dict[int,int]],
                picking_list : List[int],
                paths : Dict[int,Dict[int, Set[int]]],
                greediness : float = 0.1,
                beta : float = 0.7,
                check_paths : float = 0.1,
                deepsearch : float = 0.05,
                fulldeepsearch : float = 0.5,
                max_depth : int = 2500,

                ) -> None:

        '''
        :param distances: The distance matrix
        :param picking_list: The picking list.
        :param paths: The nodes in between two others
        
        :param greediness: The importance given to the greedy solution. To the random intention is given a weigth 
                            equal to (1 - alpha).
        :param beta: The parameter of the geometric.
        :param check_paths: The probability to include the nodes between node i and j, when going from i to j.
        :param deepsearch: Probability to do deep search.
        :param fulldeepsearch: Probability to do full deep search.  
        :param max_depth: Maximum number of iteration in case of deep search
        

        :attr current: The current solution.
        :attr intention: The current intention.
        :attr pbest: The current personal best found do far.
        :attr vcurrent: The cost of the current.
        :attr vintention: The cost of the intention.
        :attr vpbest: The cost of the personal best.
        :attr greedy: The greedy solution.
        :attr vgreedy: The cost of the greedy solution.
        
        :attr explorations: The number of solutons explored up to now.

        '''

        # set parameters
        self.distances = dict(distances)
        self.picking_list = list(picking_list)
        self.paths = dict(paths)
        
        self.greediness = greediness
        self.beta = beta
        self.check_paths = check_paths
        self.deepsearch = deepsearch
        self.fulldeepsearch = fulldeepsearch
        self.max_depth = max_depth



        # starting solutions
        self.current = list(picking_list)
        random.shuffle(self.current)

        self.pbest = list(self.current)

        self.intention = list(self.current)
        random.shuffle(self.intention)


        # evaluate solutions (i.e., distances)
        self.vpbest, self.vcurrent, self.vintention = cast(int,float("inf")), 0, 0
        self.update_dist ()

        # greedy solution
        self.greedy = _greedy (picking_list, distances)
        self.vgreedy = _compute_distance (self.greedy, distances)
        
        # The number of solutions explored
        self.explorations : int = 0

        
        
        
    def update_dist (self) -> None:
        """
        This method updates the cost of the solutions kept in memory, i.e. current, intention, and pbest.

        """
        self.vcurrent, self.vintention = 0, 0
        for i in range(len(self.picking_list) - 1):
            self.vcurrent += self.distances[self.current[i]][self.current[i+1]]
            self.vintention += self.distances[self.intention[i]][self.intention[i+1]]
        self.vcurrent += self.distances[0][self.current[0]]
        self.vintention += self.distances[0][self.intention[0]]
        self.vcurrent += self.distances[self.current[-1]][0]
        self.vintention += self.distances[self.intention[-1]][0]

        if self.vcurrent < self.vpbest:
            self.vpbest, self.pbest = self.vcurrent, list(self.current)
            
            
            
            
            

    def move (self, gbest : List[int], vgbest : int) -> Tuple[List[int], int]:
        """
        This method represents the movement of the particle that explores a new solution.

        :param gbest: The global best of the whole swarm.
        :param vgbest: The cost of the gbest.
        :return: the personal best and its cost.

        """
        # Reset the current -> !!! To remove if we want to consider it in the 
        #                          construction process.
        self.current = []


        # Initialize variables used in the construction process
        nodes : Set[int] = set(self.picking_list)
        c_node : int = 0
        n_node : int
        options : List[Tuple[int,float]]


        # Construct node-by-node a new solution
        while len(nodes) > 0:

            options = []
            if c_node == 0:
                options = [(self.intention[0], 1.0 - self.greediness),
                           (self.greedy[0], self.greediness),
                           (self.pbest[0], 1.0),
                           (gbest[0], 1.0)
                          ]
                
            else:
                options = [(sol[sol.index(c_node) + 1], w)
                           for sol, w in ((self.intention, 1.0 - self.greediness), (self.greedy, self.greediness),(self.pbest, 1.0), (gbest, 1.0))
                           if sol.index(c_node) != len(sol) - 1 and sol[sol.index(c_node) + 1] in nodes]


            if len(options) == 0:
                n_node = random.choice(list(nodes))
            elif len (options) == 1:
                n_node = options[0][0]
            else:
                n_node = _bra (sorted(options, key=lambda i: self.distances[c_node][i[0]]/i[1]), self.beta)[0]


            nodes.remove (n_node)


            # Eventually include before the new node the nodes on the shortest path
            # between the last visited node and the new one.
            r = random.random()
            if r < self.check_paths:

                in_middle = [i for i in nodes if i in self.paths[c_node][n_node]]

                while len(in_middle) > 0:

                    in_middle = sorted (in_middle, key=lambda i: self.distances[c_node][i])
                    c_node = in_middle.pop(0)
                    self.current.append (c_node)
                    nodes.remove (c_node)


            # Add the new node to the solution
            self.current.append (n_node)
            c_node = n_node

        # Update the number of solutions explored
        self.explorations += 1
        
        # Shuffle the intention
        random.shuffle(self.intention)

        # Update the personal best if needed, the cost of the current
        # and the cost of the new intention
        self.update_dist ()

        # Eventually do a deepsearch
        r = random.random()
        if len(self.picking_list) > 3 and r < self.deepsearch:
            r2 = random.random ()
            if r2 < self.fulldeepsearch:
                self.deep_search(list(self.current), full=True)
            else:
                self.deep_search(list(self.current), full=False)

            if self.vcurrent < self.vpbest:
                self.pbest, self.vpbest = list(self.current), self.vcurrent



        return self.pbest, self.vpbest

    
    
    
    def deep_search(self, lst : List[int], full : bool = False, starting_depth : int = 0) -> None:
        """
        This method does a deepsearch via 2-Opt in the neighbourhood of the 
        current solution.
        
        :param lst: The picking list.
        :param full: If TRUE every time there is an improvement and the maximum depth has
                    not been reached the deepsearch goes on.
        :param starting_depth: Used in case of full == TRUE to control the depth.

        """
        edges = [(i,j) for i in range(0,len(lst)-2) for j in range(i+2,len(lst))]
        random.shuffle(edges)
        self.explorations += len(edges)

        for i, j in edges:
            sol = _two_opt (lst, i, j)
            cost = _compute_distance (sol, self.distances)
            if cost < self.vcurrent:
                self.current, self.vcurrent = list(sol), cost

                if full is True and starting_depth < self.max_depth:
                    starting_depth += 1
                    self.deep_search(sol, True, starting_depth)

                    
                    
                    

                    
                    
                    
                    
class Mattia_PSO:
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
                paths : Dict[int, Dict[int, Set[int]]],
                era : int = 10_000,
                particles : int = 40,
                max_noimp : int = 1000,
                print_every : int = 100,
                finalsearch : bool = True,
                particle_data : Dict[str, Union[int, float, Callable[[int], float], Dict[str,float], Tuple[float,float], List[int], List[List[int]]]]

        ) -> None:
        """
        Initialize.
        
        :param distances: The distance matrix.
        :param era: The number of iterations.
        :param particles: The number of particles.
        :param max_noimp: The maximum number of iterations with no getting any improvement.
        :param print_every: The number of iterations between a log and the next one.

        :attr history: The history of the best solutions found by the algorithm.
        :attr computations: The number of solutions explored before finding the best.

        """

        self.era = era
        self.max_noimp = max_noimp
        self.print_every = print_every
        self.finalsearch = finalsearch



        particle_data["distances"] = distances
        particle_data["picking_list"] = picking_list
        particle_data["paths"] = paths

        self.particle_data = particle_data

        self.swarm : List[Particle] = [Particle(**particle_data) for _ in range(particles)]

        self.history : List[int]
        self.computations : int = 0
        self.computational_time : float = 0.0

    
    def reset(self):
        particles = len(self.swarm)

        self.swarm = [Particle(**self.particle_data) for _ in range(particles)]

        self.history = []
        self.computations = 0

   
    def run (self, verbose : bool = False) -> Tuple[List[int], int]:
        """
        This is the method to execute the algorithm.
        It finally returns the best solution found and its cost.

        :return: gbest, vgbest

        """
        # Initialize starting time
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
                self.computations = sum(p.explorations for p in self.swarm)
            else:
                noimp += 1
                if noimp > self.max_noimp:
                    break

            self.history.append(vgbest)

            if i % self.print_every == 0 and verbose is True:
                print('Epoch', i, ' Best: ', vgbest)
        
        # Final deepsearch
        if self.finalsearch is True:
            for particle in self.swarm:
                particle.deep_search (list(particle.current), True, 0)
                if particle.vcurrent < particle.vpbest:
                    particle.pbest, particle.vpbest = list(particle.current), particle.vcurrent
                    if particle.vpbest < vgbest:
                        gbest, vgbest = list(particle.current), particle.vcurrent
                        self.computations = sum(p.explorations for p in self.swarm)
        
        # Set computational time
        self.computational_time = time.time() - start

        return gbest, vgbest