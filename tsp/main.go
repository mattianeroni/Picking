package main

import (
	"aco/aco"
	"fmt"
	"time"
	"math/rand"
)

func main () {

	rand.Seed(time.Now().Unix())



	problem := aco.NewTSP(1000, 40)
	dists := problem.DistanceMatrix()


	algorithm := aco.NewACO(3000, dists, 0.9, 100.0, 1.0, 2.0, 0.1)
	algorithm.Solve(problem)

	algorithm.Plot()


	fmt.Println ("Program correctly concluded.")
}
