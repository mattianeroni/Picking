package main

import (
	"aco/aco"
	"fmt"
	"time"
	"math/rand"
)

func main () {

	rand.Seed(time.Now().Unix())

	// Build the problem
	problem := aco.NewTSP(1000, 40)
	dists := problem.DistanceMatrix()

	// Instantiate
	algorithm := aco.NewACO(3000, dists, 0.9, 100.0, 1.0, 2.0, 0.1)
	
	// Optional warmup
	algorithm.Warmup (400)  
	
	// Execution
	algorithm.Solve(problem)
	// Reset for further executions
	algorithm.Reset(false)
	
	// Plot the evolution
	algorithm.Plot()


	fmt.Println ("Program correctly concluded.")
}
