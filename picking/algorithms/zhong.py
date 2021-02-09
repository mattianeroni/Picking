from __future__ import annotations
from typing import Dict, List, Tuple, Union, Optional, cast, NewType

import random
import numpy as np # type: ignore
import time




# The type Velocity is defined
Velocity = NewType ("Velocity", List[Tuple[Tuple[int, int], float]])










def _compute_distance (lst : List[int], distances : Dict[int, Dict[int, int]]) -> int:
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












def _edge_sequence (lst : List[int]) -> List[Tuple[int,int]]:
    """
    This method, given a sequence of picking positions formalised as a sequence of locations (origin excluded),
    generates a solution formalised by using tuples where each tuple represents an edge part of the solution.
    The resulting formalisation is the same used by Zhong.
    During this process the original list <lst> is not modified.


    :param lst: The picking list
    :return: The picking list formalised according to Zhong's guidelines

    """
    lst_c = list(lst)
    lst_c.insert(0,0)
    lst_c.append(0)
    return [(lst_c[i], lst_c[i + 1]) for i in range (len(lst_c) - 1)]







def _evaluate_edge_sequence (edge_seq : List[Tuple[int,int]], distances : Dict[int, Dict[int, int]]) -> int:
    """
    This method evaluates the cost of a solution (i.e. sequence of picking positions) when
    formalised as a sequence of edges (i.e. tuples) as assumed by Zhong.

    :param edge_seq: The edge sequence formalised according to Zhong.
    :param distances: The distance matrix.
    :return: The cost of the solution.

    """
    return sum (distances[i][j] for i, j in edge_seq)











def _reverse_edge_sequence (edge_seq : List[Tuple[int,int]]) -> List[int]:
    """
    This method transform an edge sequence into a sequence where each element
    represent a node in the order in which it should be visited.
    During this process the original edge sequence <edge_seq> is not modified.

    :param edge_seq: The edge sequence as formalised by Zhong.
    :return: A sequence with the classic formalisation.

    """
    lst : List[int] = []
    edges = list(edge_seq)
    last_node : int = 0
    while len(lst) < len(edge_seq) - 1:
        for i, j in edges:
            if i == last_node and j != 0:
                last_node = j
                lst.append (j)

    return lst








def _triangular (lst : List[int]) -> int:
    """
    The estraction of an item from a list, by using a triangular distribution.
    :return: The estracted element.

    """
    return lst[int(len(lst) - len(lst)*random.random()/2) % len(lst)]










def _subtract_positions (pos1 : List[Tuple[int,int]], pos2 : List[Tuple[int,int]]) -> Velocity:
    """
    This method is used tu subtract a position to the other where positions
    are formalized with edges as suggested by Zhong.
    The result is a velocity containing all the tuples (i.e. edges) used in <pos1>
    and not in <pos2>. Tho each of them is also assigned a weight equal to 1.0.

    :param pos1: The minuend.
    :param pos2: The subtrahend.
    :return: The resulting velocity.

    """
    return cast(Velocity, [(i, 1.0) for i, j in zip(sorted(pos1), sorted(pos2)) if i != j])










def _sum (v1 : Velocity, v2 : Velocity) -> Velocity:
    """
    This method is used to sum to each other two velocities.

    """
    i : Tuple[Tuple[int, int], float]
    j : Tuple[Tuple[int, int], float]
    result = []
    for i, j in zip (v1, v2):
        if i[0] == j[0]:
            result.append ( (i[0], i[1] + j[1]) )
        else:
            if i[1] > j[1]:
                result.append (j)
            else:
                result.append (i)

    return cast (Velocity, result)










def _multiply (w : float, v : Velocity) -> Velocity:
    """
    This method is used to get the multiplication between a scalar and
    a velocity.

    :param w: Scalar.
    :param v: Velocity.
    :return: A new Velocity.

    """
    return cast(Velocity, [(pair, w * weight) for pair, weight in v])










class Particle (object):
    """
    An instance of this class represents a particle used in the algorithm by Zhong.

    """
    def __init__ (self, distances : Dict[int, Dict[int,int]], picking_list : List[int], w : float, lt : int) -> None:
        """
        Initialize.

        :attr distances: The distance matrix
        :attr picking_list: The picking list
        :attr w: The weight assigned to the greedy velocity.
        :attr lt: The different temperatures considered.

        :attr current: The current position
        :attr pbest: The personal best
        :attr vcurrent: The cost of the current solution.
        :attr vpbest: The cost of the personal best

        :attr velocity: The velocity of the particle.

        :attr _dual: The current dual particle.

        :attr temperatures: The list of temperatures.
        
        :attr explorations: The number of solutions explored up to now.

        """
        self.distances = distances
        self.picking_list = picking_list
        self.w = w

        self.current : List[int] = list(picking_list)
        random.shuffle (self.current)
        self.vcurrent = _compute_distance(self.current, distances)

        self.pbest, self.vpbest = list(self.current), self.vcurrent

        self.velocity : Velocity = self._greedy_velocity()

        self._dual : Optional[Particle] = None

        self.temperatures : List[float] = []
            
        self.explorations : int = 0

        x = list(self.current)
        x_cost = self.vcurrent

        while len(self.temperatures) < lt:

            edge_indexes = (random.randint(0, len(picking_list) - 1), random.randint(0, len(picking_list) - 1))
            if edge_indexes[0] > edge_indexes[1]:
                edge_indexes = tuple(reversed(edge_indexes))
                
            
            edge = (x[edge_indexes[0]], x[edge_indexes[1]])

            func = random.randint(1,3)
            candidate : List[int]; candidate_cost : int


            if func == 1:
                candidate, candidate_cost = self._swap(edge, x, distances)
            elif func == 2:
                candidate, candidate_cost = self._insert(edge, x, distances)
            elif func == 3:
                candidate, candidate_cost = self._inverse(edge, x, distances)

            if (delta := abs(candidate_cost - x_cost)) > 0:
                self.temperatures.append (delta)

            if candidate_cost < x_cost:
                x, x_cost = list(candidate), candidate_cost




    @property
    def dual (self) -> Particle:
        """
        This property returns the <_dual> of the particle.

        """
        return cast(Particle, self._dual)


    
    
    @property
    def edge_current (self) -> List[Tuple[int,int]]:
        """
        This property returns the current solution in the format desired 
        by Zhong: as a list of tuples representing the edges which are 
        part of the solution.
        It is possible to calculate the cost of the solution returned using
        the method <_evaluate_edge_sequence>.
        """
        return _edge_sequence(self.current)




    
    
    @property
    def edge_pbest (self) -> List[Tuple[int,int]]:
        """
        This property returns the current pbest in the format desired 
        by Zhong: as a list of tuples representing the edges which are
        part of the solution.
        It is possible to calculate the cost of the solution returned using
        the method <_evaluate_edge_sequence>.

        """
        return _edge_sequence(self.pbest)










    def _greedy_velocity (self) -> Velocity:
        """
        This method returns a new pseudo-greedy velocity, which is built in the following way:
        For each i element of the picking list (included the origin 0), a tuple (i, j) is built, 
        where j is the storage location to visit after i.
        The storage location j is selected using a triangular distribution. Smaller
        is the distance between i and j, bigger is the probability to select j.
        The weight assigned to each tuple is always w, where w is the parameter of
        the algorithm.

        """
        options = [0] + list(self.picking_list)
        v : Velocity = []
        for i in range (len(self.picking_list) + 1):
            j = _triangular (sorted(options, key=lambda x: self.distances[options[i]][x])[1:])
            v.append ( ((options[i], j), self.w) )
        
        return v









    def set_dual (self, particle : Particle) -> None:
        """
        This method is used to set the dual of this particle,
        whose pbest and vpbest are used during the movement.

        The dual is randomly selected from the swarm at each 
        iteration of the algorithm.

        :param particle: The particle selected as dual.

        """
        self._dual = particle




    @staticmethod
    def _swap (edge : Tuple[int, int], solution : List[int], distances : List[List[int]]) -> Tuple[List[int], int]:
        """
        The swap operation introduced by Zhong.

        :param edge: The edge suggesting the modification.
        :param solution: The current solution formalised as an edge sequence.
        :param distances: The distance matrix.
        :return: A new edge sequence and its cost.

        """
        i, j = edge
        if i == j:
            return list(solution), _compute_distance (solution, distances)

        sol = _edge_sequence (solution)
        if edge in sol:
            return list(solution), _compute_distance (solution, distances)

        toreplace : Tuple[int,int]; toremove : Tuple[int,int]; toconnect : Tuple[int,int]
        for ed in sol:
            if ed[0] == i:
                toreplace = ed
            elif ed[0] == j:
                toremove = ed
            elif ed[1] == j:
                toconnect = ed

        sol.append( edge )
        sol.append( (j,toreplace[1]) )
        sol.remove( toreplace )
        sol.remove( toremove )
        sol.append( (toconnect[0], toremove[1]) )
        sol.remove( toconnect )

        return _reverse_edge_sequence(sol), _evaluate_edge_sequence(sol, distances)





    @staticmethod
    def _insert (edge : Tuple[int, int], solution : List[int], distances : List[List[int]]) -> Tuple[List[int], int]:
        """
        The insert operation introduced by Zhong.

        :param edge: The edge suggesting the modification.
        :param solution: The current solution formalised as an edge sequence.
        :param distances: The distance matrix.
        :return: A new edge sequence and its cost.

        """
        if edge[0] == edge[1]:
            return list(solution), _compute_distance(solution, distances)

        sol : List[int] = [0] + list(solution) + [0]

        i, j = sol.index(edge[0]), sol.index(edge[1])
        if i > j or j == 0:
            return (s:=sol[1:-1]), _compute_distance(s, distances)

        r = random.randint (1, len(sol) - j - 1)
        sol = sol[:i+1] + sol[j:j+r] + sol[i+1:j] + sol[j+r:]

        return (s := sol[1:-1]), _compute_distance(s, distances)







    @staticmethod
    def _inverse (edge : Tuple[int, int], solution : List[int], distances : List[List[int]]) -> Tuple[List[int], int]:
        """
        The insert operation introduced by Zhong.

        :param edge: The edge suggesting the modification.
        :param solution: The current solution formalised as an edge sequence.
        :param distances: The distance matrix.
        :return: A new edge sequence and its cost.

        """
        if edge[0] == edge[1]:
            return list(solution), _compute_distance (solution, distances)

        sol : List[int] = [0] + list(solution) + [0]

        i, j = sol.index(edge[0]), sol.index(edge[1])
        if i > j or j == 0:
            return (s:=sol[1:-1]), _compute_distance (s, distances)

        torev = sol[i+1:j+1]
        sol = sol[:i+1] + list(reversed(torev)) + sol[j+1:]

        return (s := sol[1:-1]), _compute_distance(s, distances)






    def move (self, gbest : List[int], vgbest : int) -> Tuple[List[int], int]:
        """
        This method represents the movement of the particle, followed by 
        its velocity update.

        :param gbest: The global best of the whole swarm.
        :param vgbest: The cost of the gbest.
        :return: The pbest of the particle and its cost.

        """
        t_count = [0, 0]

        # Move particle
        for edge, _ in self.velocity:

            # Try all three options: swap, insert, and inverse
            options : List[Tuple[List[int], int]] = [self._swap(edge, self.current, self.distances),
                                                    self._insert(edge, self.current, self.distances),
                                                    self._inverse(edge, self.current, self.distances)]

            # Select the best one
            bopt, bopt_cost = sorted(options, key=lambda i: i[1])[0]
            rnd = random.random()

            # If better than current update
            if bopt_cost < self.vcurrent:
                self.current, self.vcurrent = bopt, bopt_cost
                if self.vcurrent < self.vpbest:
                    self.pbest, self.vpbest = list(self.current), self.vcurrent
            # Otherwise there is a certain possibility to update as well
            elif ( delta:=(bopt_cost - self.vcurrent) / max(t_count[0], 1) ) < 0.000001 or rnd < np.exp(-delta):
                t = - (bopt_cost - self.vcurrent) / np.log(rnd)
                t_count[0] += 1
                t_count[1] += t
                self.current, self.vcurrent = bopt, bopt_cost
        
        # Update the solutions explored
        self.explorations += 3 * len(self.velocity)

        # Temperature update
        if t_count[0] != 0 or t_count[1] != 0:
            self.temperatures.pop (0) 
            self.temperatures.append(t_count[1] / t_count[0])
            self.temperatures.sort(reverse=True)



        # Velocity update
        greedy : Velocity = self._greedy_velocity()
        learning : Velocity = _subtract_positions (self.dual.edge_pbest, self.edge_current)
        rnd = random.random()
        self.velocity = _sum (_multiply (self.w, greedy), _multiply(rnd, learning))

        return self.pbest, self.vpbest























class Zhong_PSO (object):
    '''
    Solutions are coded with a ‘edge-based’ notation where the  value j in position i indicate node visited after i (i.e., the edge ij).
    For instance, using a tuple-based notation, the following sequence {0 - 2 - 3 - 1- 5 - 6 - 4 - 0}  would be coded in the following way:
    {(0, 2), (1, 5), (2, 3), (3, 1), (4, 0), (5, 6), (4, 0)}
    Velocities are coded with the same approach used for sequences, but in this case a weight is attributed to each edge,
    e.g. : {[(0, 2), 0.5], [(1, 5), 1], …, [(n, k), x]}.
    Also, nodes of < velocity sequences does not necessarily form a tour, they just denote possible new edge that 
    could be inserted in a sequence.
    Distance between two solutions (S1 – S2) equals S1, without the edges that are also in S2;
    kind of  {[(0, 2),w = 1], [None, w = 0,] …} where w is a weight equal to 1 if an edge is maintained,
    and zero otherwise. By doing so the difference of two sequences generates a velocity. 
    Velocities are summed taking for each edge starting at i the one with the highest weight, 
    if the edge is equal the weigth are summed. eg V1 = {[(0, 2), 0.5], [(1, 5), 1], …,} , V2 = {[(0, 2), 0.8], [(1, 7), 1.2], …,} 
    so V1+ V2 = {[(0, 2), 1.3], [(1, 7), 1.2], …,}
    Velocity is updated as it follows: 
    Where VR is a greedy velocity created as it follows. For each node i an edge ij with weigth 1 is created,
    by randomly selecting the next city j (with a probability depending on the distance ij). Eg. Vr = {[(0, 3),1], [(1, 5), 1] …., [(n, k), 1]}.
    Current is the actual solution of particle i, while best is the best solution (obtained so far) by another particle of the swam.
    The multiplicative factor W (fixed) and r (random) multiply the weights of each node.
    The new velocity is used to generate a new sequence in an incremental way: each edge of the velocity 
    vector is considered for possible insertion, for instance if V = {[(0, 3),1], [(1, 5), 1]  … } the sequence obtained 
    inserting edge  (0,3) is created, next the sequence obtained insertin edge (1, 5) is considered and so on. 
    Any time a new sequence is created inserting a node if it improves or even if it  gets worst but it is accepted (using
    a methropolis acceptance criterion as in a simulated annealing), it is used as a starging point for the next generation.
    For each node three possible insertion approach are considered: swap, insert and revers, as shown in the figures below.

    '''

    def __init__ (self, *,
                distances : Dict[int, Dict[int,int]],
                picking_list : List[int],
                particles : int = 30,
                w : float = 1.0,
                lt : int = 1000, 
                max_iter : int = 10000,
                max_noimp : int = 1000,
                print_every : int = 100

                ) -> None:
        """
        Initialize.

        :attr max_iter: The number of iterations.
        :attr max_noimp: The max number of iterations with no improvement.
        :attr print_every: The number of iterations between a log and the next.
        :attr history: The history of the best solutions found.
        :attr computations: The number of solutions explored before finding the best.
        
        :param particles: The number of particles.
        :param distances: The distance matrix.

        """
        self.swarm : List[Particle] = [Particle(distances, picking_list, w, lt) for _ in range(particles)]
        
        self.max_iter = max_iter
        self.max_noimp = max_noimp
        self.print_every = print_every
        
        self.particles = particles
        self.distances = distances
        self.picking_list = picking_list
        self.w = w
        self.lt = lt

        self.history : List[int]
        self.computations : int = 0
        self.computational_time : float = 0.0
            
    
    
    
    def reset (self):
        self.history = []
        self.computations = 0
        self.computational_time = 0.0
        self.swarm = [Particle(self.distances, self.picking_list, self.w, self.lt) for _ in range(self.particles)]




    def run (self, verbose : bool = False) -> Tuple[List[int], int]:
        """
        This method represents the execution of the algorithm.
        
        :param verbose: If TRUE evey <print_every> iterations the current 
                        best is logged.
        :return: The best solution found and its cost.

        """
        # Initialize the starting time
        start = time.time()
        
        # Initialize the best
        gbest : List[int]; vgbest : int = cast(int,float("inf"))
        for particle in self.swarm:
            if particle.vpbest < vgbest:
                gbest, vgbest = particle.pbest, particle.vpbest

        new_gbest, new_vgbest = list(gbest), vgbest
        self.history = [vgbest]

        # Iterate
        noimp : int = 0
        for i in range (self.max_iter):

            # Move particles
            for particle in self.swarm:
                # Select another particle pbest and pass it to this particle
                other : Particle = random.choice (self.swarm)
                while other is particle:
                    other = random.choice (self.swarm)

                particle.set_dual (other)

                # Move
                sol, cost = particle.move (gbest, vgbest)

                # For each particle, in case of improvement, we keep track of it
                # to update the gbest without doing a further for loop
                if cost < new_vgbest:
                    new_gbest, new_vgbest = sol, cost

            # Update the vgbest and check an eventual improvement
            if new_vgbest < vgbest:
                noimp = 0
                self.computations = sum(p.explorations for p in self.swarm)
                gbest, vgbest = list(new_gbest), new_vgbest
            else:
                noimp += 1
                # Eventually breaks if no improvement for long time
                if noimp >= self.max_noimp:
                    break

            # Update the history
            self.history.append (vgbest)

            # Eventually log the results
            if verbose is True and i % self.print_every == 0:
                print ('Epoch', i, ' Best: ', vgbest)
        
        # Set the computational time
        self.computational_time = time.time() - start

        return gbest, vgbest