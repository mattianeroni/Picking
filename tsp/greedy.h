#ifndef ACO_GREEDY_H
#define ACO_GREEDY_H


#include <array>
#include <vector>
#include <algorithm>
#include "problem.h"
#include <iostream>


using std::array;
using std::vector;
using generator::Problem;


// N is the legnth of the picking list
// Q is the size of the graph
template <std::size_t N, std::size_t Q>



class Greedy{

public:
    Problem<N, Q> problem;
    array<int, N> best;
    long          cost;

    Greedy(Problem<N,Q>);           // Constructor

    void operator()();              // Executor

    void reset();                   // Reset the best

private:
    long _getcost(array<int,N>);    // Get the cost of the solution

};


// Constructor
template <std::size_t N, std::size_t Q>
Greedy<N,Q>::Greedy(Problem<N,Q> p) : problem(p){}

// Executor
template <std::size_t N, std::size_t Q>
void Greedy<N,Q>::operator()()
{
    int cnode = 0, i = 0;
    auto dists = problem.distance_matrix;
    vector<int> v (problem.pickinglist.begin(), problem.pickinglist.end());
    while (v.size() > 0) {
        std::sort(v.begin(), v.end(),
                  [cnode, dists](int node, int node2) { return dists[cnode][node] < dists[cnode][node2]; });
        cnode = v[0];
        v.erase(v.begin());
        best[i] = cnode;
        ++i;
    }
    cost = _getcost(best);
}


// Executor
template <std::size_t N, std::size_t Q>
void Greedy<N,Q>::reset()
{
    (*this).best = problem.pickinglist;
    (*this).cost = _getcost((*this).best);
}



// Get the cost of a solution
template <std::size_t N, std::size_t Q>
long Greedy<N,Q>::_getcost(array<int,N> sol)
{
    long sum = 0; int cnode = 0;
    for (auto i : sol){
        sum += problem.distance_matrix[cnode][i];
        cnode = i;
    }
    sum += problem.distance_matrix[cnode][0];
    return sum;
}

#endif //ACO_GREEDY_H