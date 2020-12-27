#ifndef ACO_PROBLEM_H
#define ACO_PROBLEM_H

#include <array>
#include <math.h>
#include <algorithm>

using std::array;
using std::pair;



namespace generator {


    // N is the length of the picking list
    // Q is the number of nodes in the graph
    template<std::size_t N, std::size_t Q>


    // An instance of this structure represents a problem
    struct Problem {
        array<array<int,Q>, Q> distance_matrix;
        array<int, N> pickinglist;
    };


    // N is the length of the picking list
    // Q is the number of nodes in the graph
    template<std::size_t N, std::size_t Q>

    // The get method generates a new Problem instance
    Problem<N,Q> get(int[2]);

};



// N is the length of the picking list
// Q is the number of nodes in the graph
template<std::size_t N, std::size_t Q>


// This method generates a new problem
// :param Q: The number of nodes in the graph
// :param N: The length of the picking list
// :param area[2]: The size of the space where the nodes stay
generator::Problem<N, Q> generator::get (int area[2]){
    auto p = generator::Problem<N,Q>{};              // Instantiate the problem

    array<pair<int, int>, Q> nodes;                  // The nodes of the graph
    nodes[0] = pair<int,int>(0,0);                   // The origin
    for (int i = 1; i < Q; ++i)
        nodes[i] = pair<int,int>(rand() % area[0], rand() % area[1]);


    // Fill the distance matrix
    p.distance_matrix = array<array<int,Q>,Q>();
    for (int i = 0; i < Q; ++i)
        for (int j = 0; j < Q; ++j)
            p.distance_matrix[i][j] = std::pow(std::pow(nodes[i].first - nodes[j].first, 2) + std::pow(nodes[i].second - nodes[j].second, 2), 0.5);


    // Generate the picking list
    array<int,Q - 1> options;
    for (int i = 0; i < Q - 1; ++i) options[i] = i+1;
    std::random_shuffle(options.begin(), options.end());
    std::copy(options.begin(), options.begin()+N, p.pickinglist.begin());

    // Return the problem instance
    return p;
}

#endif //ACO_PROBLEM_H
