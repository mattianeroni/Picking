#ifndef ACO_ACO_H
#define ACO_ACO_H



#include <iostream>
#include <array>
#include <vector>
#include <algorithm>
#include <math.h>


#include "problem.h"

using std::vector;
using std::array;
using std::pow;

// Namespace with the problem class
using namespace generator;







// Template the size of the picking list N
// Template the size of the distance matrix Q
template <std::size_t N, std::size_t Q>




class ACO {

        // An instance of this class represents the Ant Colony Optimization algorithm.

public:


    float        alpha, beta, q, ro, rowu;     // Parameters of the algorithm
    Problem<N,Q> problem;                      // The problem to solve
    array<int,N> best;                         // The best solution
    long         cost;                         // The cost of the best solution
    bool         evaporate;                    // If true the pheromone evaporates at each loop
    long         computations;                 // Number of computations needed to find the best

    array<array<float,Q>,Q> pher;              // The pheromone matrix

    // Constructor
    ACO(Problem<N,Q> problem, float init_pher=0.1, float alpha=1.0, float beta=5.0, float q=100.0, float ro=0.5,float rowu=1.0, bool evaporate=false, long wu_iter=400);

    // Destructor
    ~ACO();

    // The execution
    void operator() (long maxiter, bool verbose);

    // Reset the best solutions
    void reset();


private:

    // Generates a new solution
    array<int,N> _newsolution ();

    // Get the cost of a solution
    long _getcost (array<int,N> sol);

    // Evaporate
    void _evaporate();

    // Update pheromone on a new best path
    void _update(array<int,N> best);
};



// Destructor
template <std::size_t N, std::size_t Q>
ACO<N,Q>::~ACO(){}




// Constructor
// Template the size of the picking list N
// Template the size of the distance matrix Q
template <std::size_t N, std::size_t Q>
ACO<N,Q>::ACO(Problem<N,Q> problem, float init_pher, float alpha, float beta, float q, float ro,float rowu, bool evaporate, long wu_iter)
: problem(problem), alpha(alpha), beta(beta), q(q), rowu(rowu), evaporate(evaporate), ro(ro)
{
    (*this).best = problem.pickinglist;
    (*this).cost = _getcost((*this).best);
    // Initialize the pheromone matrix
    for (int i = 0; i < Q; ++i)
        for (int j = 0; j < Q; ++j)
            pher[i][j] = i != j ? init_pher : 0.0;

    // Warmup
    for (long a = 0; a < wu_iter; ++a) {
        // diststances 
        array<array<int,Q>,Q> dists = problem.distance_matrix;
        for (int i = 0; i < Q; ++i) dists[i][i] = 1.0;
        
        // probabilities of increase
        array<array<int,Q>,Q> probs;
        for (int i = 0; i < Q; ++i){
            double sum = 0.0;
            for (int j = 0; j < Q; ++j){
                auto delta = pow(pher[i][j], alpha) / pow(dists[i][j], beta);
                probs[i][j] = delta;
                sum += delta;
            }
            
            for (int j = 0; j < Q; ++j)
                probs[i][j] /= sum;
            
        }
        
        // increase pheromone
        for (int i = 0; i < Q; ++i)
            for (int j = 0; j < Q; ++j)
                pher[i][j] += probs[i][j] * q / dists[i][j];
        
        // evaporate
        for (int i = 0; i < Q; ++i)
            for (int j = 0; j < Q; ++j)
                pher[i][j] *= rowu;
    }
}

// Reset the best
template <std::size_t N, std::size_t Q>
void ACO<N,Q>::reset()
{
    (*this).best = problem.pickinglist;
    (*this).cost = _getcost((*this).best);
    (*this).computations = 0;
}


// The execution of the algorithm
template <std::size_t N, std::size_t Q>
void ACO<N,Q>::operator() (long maxiter, bool verbose)
{
    for (long iter = 0; iter < maxiter; ++iter){

        // Evaporate
        if (evaporate) _evaporate();

        // Generates a new solution
        auto newsolution = _newsolution();
        auto newcost = _getcost(newsolution);

        // Eventually update the best
        if (newcost < cost){
            cost = newcost; best = newsolution;
            _update(best);
            _evaporate();
            computations = iter;
        }

        // Log current results
        if (verbose && iter % 100 == 0)
            std::cout << "Iteration: " << iter << "; Cost: " << cost << std::endl;
    }
}




// Generates a new solution
template <std::size_t N, std::size_t Q>
array<int,N> ACO<N,Q>::_newsolution()
{
    //array<array<float,Q>,Q> pher = (*this).pher;
    //Problem<N,Q> p = (*this).problem;
    //float alpha = (*this).alpha, beta = (*this).beta;

    array<int,N> sol;
    vector<int> options (problem.pickinglist.begin(), problem.pickinglist.end());
    int cnode = 0, nnode = -1;

    for (int i = 0; i < N; ++i){
        float r = (float) rand() / RAND_MAX,  cum = 0;
        float tot = 0; for(auto op:options){tot += pow(pher[cnode][op],alpha) / pow(problem.distance_matrix[cnode][op],beta);}
        for (auto op : options){
            cum += pow(pher[cnode][op],alpha) / pow(problem.distance_matrix[cnode][op],beta) / tot;
            if (cum > r){nnode = op; break;}
        }
        options.erase(std::find(options.begin(), options.end(), nnode));

        sol[i] = nnode;
        cnode = nnode;
    }

    return sol;
}



// Evaporates the pheromone
template <std::size_t N, std::size_t Q>
void ACO<N,Q>::_evaporate()
{
    for (auto i : pher)
        for (float j : i)
            j *= ro;
}



// Update the pheromone
template <std::size_t N, std::size_t Q>
void ACO<N,Q>::_update(array<int,N> sol)
{
    int cnode = 0;
    for (auto i : sol){
        pher[cnode][i] += q / problem.distance_matrix[cnode][i];
        cnode = i;
    }
    pher[cnode][0] += q / problem.distance_matrix[cnode][0];
}




// Get the cost of a solution
template <std::size_t N, std::size_t Q>
long ACO<N,Q>::_getcost(array<int,N> sol)
{
    long sum = 0; int cnode = 0;
    for (auto i : sol){
        sum += problem.distance_matrix[cnode][i];
        cnode = i;
    }
    sum += problem.distance_matrix[cnode][0];
    return sum;
}




#endif //ACO_ACO_H