#include <iostream>
#include <array>
#include <stdlib.h>

#include "greedy.h"
#include "problem.h"
#include "aco.h"

using std::cout;
using std::endl;
using std::array;
using std::srand;



void experiment (){

    srand(time(NULL));                       // Set the random seed
    cout << "Problem Greedy ACO WACO ACO_comp WACO_comp" <<endl;
    for (int i = 0; i < 5; ++i){                        // Problems

        int area[2] = {10000, 10000};
        auto problem = generator::get<60, 61>(area);   //Length of the picking list

        auto greedy = Greedy(problem);
        greedy();
        auto aco = ACO (problem, 0.1, 1.0,5.0, 100.0, 0.5, 0.0, false, 0);
        auto aco2 = ACO (problem, 0.1, 1.0,5.0, 100.0, 0.5, 1.0, false, 400);



        for (int j = 0; j < 5; ++j){                    // Executions on the same problem

            aco(2000, false);
            aco2(2000, false);
            cout << i + 1 << " " << greedy.cost << " " << aco.cost << " " << aco2.cost << " " << aco.computations << " "<< aco2.computations<< endl;

            aco.reset(); aco2.reset();
        }
        cout << endl;
    }
}



int main() {
    experiment();
    cout << "Program concluded." << endl;
    return 0;
}




void tuning (){

    srand(time(NULL));                       // Set the random seed

    int probs[3] = {20, 30, 40};
    long Ms[3] = {200, 400, 600};
    float ros[3] = {0.5, 0.9, 1.0};


    int area[2] = {10000, 10000};
    auto problem = generator::get<40, 60>(area);   //Length of the picking list

    for (auto m : Ms){
        for (auto ro : ros) {
            for (int t = 0; t < 3; ++t) {

                auto aco = ACO(problem, 0.1, 1.0, 5.0, 100.0, 0.5, ro, false, m);
                aco(3000, false);

                cout << m << " " << ro << " " << aco.cost << endl;
            }
        }
    }
}