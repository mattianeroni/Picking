package aco

import (
  "image/color"
  "math"
  "math/rand"
  "time"

  "gonum.org/v1/plot"
  "gonum.org/v1/plot/plotter"
  "gonum.org/v1/plot/vg"
)


// The route type
type Route []Node


// The solutions of the algorithm
type Solution struct {
  Route Route
  Cost int
}



// This function returns the cost of a new route
func getCost (route Route, depot Node, dists [][]int) int {
  cost := 0
  cnode := depot
  for _, node := range route[1:] {
    cost += dists[cnode.id][node.id]
    cnode = node
  }
  cost += dists[cnode.id][depot.id]
  return cost
}


// The Ant Colony Optimization (ACO) algorithm
type AntColonyOptimization struct {

  era int                           // The number of iterations of the algorithm
  dists [][]int                     // The matrix of distances
  ro, Q, a, b float64               // The parameters of the algorithm

  pheromone [][]float64             // The pheromone matrix
  initialPheromon [][]float64       // The initial pheromone before starting the iterations and warmup
  wuPheromone [][]float64           // The initial pheromone after the warmup

  best Solution                     // The best solution found
  computationalTime time.Duration   // Register the computational time
  history []Solution                // The history of best solutions found

}



// Constructor for the ACO
func NewACO (era int, dists[][]int, ro, Q, a, b, pherInit float64) *AntColonyOptimization {
  // Initialize the pheromone matrix and the initial pheromone matrix
  size := len(dists)
  pheromone := make([][]float64, size)
  initialPheromone := make([][]float64, size)
  wuPheromone := make([][]float64, size)

  for i := 0; i < size; i++ {
    pheromone[i] = make([]float64, size)
    initialPheromone[i] = make([]float64, size)
    wuPheromone[i] = make([]float64, size)

    for j := 0; j < size; j++ {
      pheromone[i][j] = pherInit
      initialPheromone[i][j] = pherInit
      wuPheromone[i][j] = pherInit
    }
  }

  return &AntColonyOptimization{era, dists, ro, Q, a, b,pheromone,
    initialPheromone, wuPheromone, Solution{},
    0.0,make([]Solution, 0)}
}



// This method is the warmup procedure
func (self *AntColonyOptimization) Warmup (maxiter int) {
  size := len(self.dists)

  // At each iteration...
  for iter := 0; iter < maxiter; iter++ {

    for i := 0; i < size; i++ {

      // Calculate the probability to upgrade that arc
      var grades = make([]float64, size)
      var totalGrade float64 = 0.0
      for j := 0; j < size; j++ {
        if i != j {
          g := math.Pow(self.pheromone[i][j], self.a) * (1.0 / math.Pow(float64(self.dists[i][j]), self.b))
          grades[j] = g
          totalGrade += g
        } else {
          grades[j] = 0.0
        }
      }

      // Update the pheromone on the arcs
      for j := 0; j < size; j++ {
        prob := grades[j] / totalGrade
        update := prob * self.Q / float64(self.dists[i][j])
        self.pheromone[i][j] += update
        self.wuPheromone[i][j] += update
      }

    }
  }
}



// This method restores the pheromone to the initial value.
// If the argument <complete> is true the pheromone returns how before the warmup,
// otherwise it returns how after the warmup.
func (self *AntColonyOptimization) Reset (complete bool) {
  if complete == true {
    for i := 0; i < len(self.dists); i++ {
      copy(self.pheromone[i], self.initialPheromon[i])
    }
  } else if complete == false {
    for i := 0; i < len(self.dists); i++ {
      copy(self.pheromone[i], self.wuPheromone[i])
    }
  }
}



func (self *AntColonyOptimization) Solve (problem *TSP) Solution {

  // Save the depot
  var depot Node = problem.nodes[0]

  // Chronometer
  start := time.Now()

  // Initialize a random starting solution
  nodes := problem.nodes[1:]
  rand.Shuffle(len(nodes), func(i, j int) {
    nodes[i], nodes[j] = nodes[j], nodes[i]
  })
  ccost := getCost(nodes, depot, self.dists)
  csol := Solution{nodes, ccost}
  self.history = append(self.history, csol)


  // Iterations
  for e := 0; e < self.era; e++ {

    // Generate a new solution from scratch
    newRoute := self.getRoute(nodes, depot)
    newCost := getCost(newRoute, depot, self.dists)
    newSol := Solution{newRoute, newCost}

    if newCost < ccost {
      // Update the best solution
      ccost, csol = newCost, newSol

      // Update the pheromone if the new solution is better
      self.updatePheromone(newRoute)

      // Evaporate pheromone
      self.evaporatePheromone()

      self.history = append(self.history, csol)
    }



  }

  // Save computational time
  self.computationalTime = time.Now().Sub(start)
  // Set and return the best solution
  self.best = csol
  return csol
}


// Create a new solution from scratch
func (self *AntColonyOptimization) getRoute(nodes Route, depot Node) Route {
  // Init the list of options and the new route
  options := make([]Node, len(nodes))
  copy(options, nodes)
  newRoute := make(Route, len(nodes))

  // Set the current node and define next node
  var currentNode Node = depot
  var nextNode Node
  var nextNodeId int

  for i := 0; i < len(nodes); i++ {
    // Generate a random number
    r := rand.Float64()
    cum := 0.0

    // Init the variables used to evaluate nodes candidates
    grades := make([]float64, len(options))
    totalGrade := 0.0

    // Assign grades to nodes
    for j, node := range options {
      origin, destination := currentNode.id, node.id
      grade := math.Pow(self.pheromone[origin][destination], self.a) * (1.0 / math.Pow(float64(self.dists[origin][destination]), self.b))
      grades[j] = grade
      totalGrade += grade
    }

    // Calculate probability of nodes and eventually select them as next node visited
    for j := 0; j < len(options); j++ {
      cum += grades[j] / totalGrade
      if cum >= r {
        nextNode = options[j]
        nextNodeId = j
        break
      }
    }

    // Update current node, new route, and list of options
    currentNode = nextNode
    newRoute[i] = nextNode
    options = append(options[:nextNodeId], options[nextNodeId + 1:]...)
  }

  // Returns new route
  return newRoute
}

// This method update the pheromone on the new best path found
func (self *AntColonyOptimization) updatePheromone (bestRoute Route){
  var origin, destination int
  for i := 0; i < len(bestRoute) - 1; i++ {
    origin = bestRoute[i].id; destination = bestRoute[i + 1].id
    self.pheromone[origin][destination] += self.Q / float64(self.dists[origin][destination])
  }
  last := len(bestRoute) - 1
  self.pheromone[0][bestRoute[0].id] += self.Q / float64(self.dists[0][bestRoute[0].id])
  self.pheromone[bestRoute[last].id][0] += self.Q / float64(self.dists[bestRoute[last].id][0])
}


// Evaporate the pheromone
func (self *AntColonyOptimization) evaporatePheromone () {
  var size int = len(self.dists)
  for i := 0; i < size; i++ {
    for j := 0; j < size; j++ {
      self.pheromone[i][j] *= self.ro
    }
  }
}



// Expose the history of the algorithm
func (self *AntColonyOptimization) History () []Solution {
  return self.history
}



// Expose the best solution of the algorithm
func (self *AntColonyOptimization) Best () Solution {
  return self.best
}



// Expose the computational time of the algorithm
func (self *AntColonyOptimization) Time () time.Duration {
  return self.computationalTime
}



// Plot the evolution of the best solution (horrible)
func (self *AntColonyOptimization) Plot () {
  p := plot.New()

  p.Title.Text = "Evolution"
  p.X.Label.Text = "Iterations"
  p.Y.Label.Text = "Cost"

  history := make(plotter.XYs, len(self.history))
  for i := 0; i < len(history); i++ {
    history[i].X = float64(i)
    history[i].Y = float64(self.history[i].Cost)
  }

  p.Add(plotter.NewGrid())

  // Make a line plotter with points and set its style.
  lpLine, _, err := plotter.NewLinePoints(history)
  if err != nil {
    panic(err)
  }
  lpLine.Color = color.RGBA{G: 0, A: 255, B: 255}

  // Add the plotters to the plot, with a legend
  // entry for each
  p.Add(lpLine)

  // Save the plot to a PNG file.
  if err := p.Save(4*vg.Inch, 4*vg.Inch, "./points.png"); err != nil {
    panic(err)
  }
}