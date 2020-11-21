from __future__ import annotations

from typing import Tuple, Dict, List, Set, cast



def floyd_warshall (graph : Dict[int,Dict[int,int]]) -> Tuple[Dict[int,Dict[int,int]], Dict[int,Dict[int,Set[int]]]]:
    """
    This method represents the Floyd Warshall algorithm.

    First a full distance matrix is generated, because in the graph only
    the distance between adiacent nodes is reported. At first, in the full
    distance matrix, the distance between non-adiacent nodes is set equal
    to infinite.
    
    Then, the Floyd Warshall is computed. For each couple of nodes (u,v),
    a third node t is selected. If the d(u,t) + d(t,v) < d(u,v), then 
    d(u,t) + d(t,v) is the new distance between u and v (where d() is the 
    distance function).

    During the execution of the Floyd Warshall we also keep track of the 
    nodes in between two others. This information can be given to the 
    optimization algorithms, in order to have more information concerning
    the possible paths.

    :param graph: The graph of nodes.
    :return: The matrix of shortest distances and the list of nodes in 
            between.

    """
    distances : Dict[int,Dict[int,int]] = {}
    paths : Dict[int,Dict[int, Set[int]]] = {}

    for u in graph:
        distances[u] = {}
        paths[u] = {}

        for v in graph:
            if not distances.get(v):
                distances[v] = {}
                paths[v] = {}

            if v == u:
                distances[u][v] = 0
                distances[v][u] = 0
                paths[u][v] = {}
                paths[v][u] = {}
            else:
                if graph[u].get(v):
                    distances[u][v] = graph[u][v]
                    paths[u][v] = {u}
                    paths[v][u] = {v}

                else:
                    distances[u][v] = cast(int, float("inf"))
                    paths[u][v] = {i for i in range(u + 1, v)}
                    paths[v][u] = set(paths[u][v])


    
    for u in distances:
        for v in distances:
            for t in distances:

                if (newdist := distances[u][t] + distances[t][v]) < distances[u][v]:
                    distances[u][v] = newdist
                    distances[v][u] = newdist

                    paths[u][v] = paths[u][t] | paths[t][v]
                    paths[v][u] = set(paths[u][v])

    for u in distances:
        for v in distances:
            if u in paths[u][v]:
                paths[u][v].remove(u)
            if u in paths[v][u]:
                paths[v][u].remove(u)
            if v in paths[u][v]:
                paths[u][v].remove(v)
            if v in paths[v][u]:
                paths[v][u].remove(v)


    return distances, paths