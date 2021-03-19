package aco


import (
  "math/rand"
  "math"
)


// A node of the graph
type Node struct {
  id, x, y int
}


// A Travelling Salesman Problem (TSP)
type TSP struct {
  space int       // The size of the space where the nodes are
  nodes Route     // The nodes of the problem (the first node is always the depot)
}


// Constructor for the TSP problem
func NewTSP (space, nodes int) *TSP {
  nodesList := make ([]Node, nodes)
  for i := 0; i < nodes; i++ {
    nodesList[i] = Node{i, rand.Intn(space), rand.Intn(space)}
  }
  return &TSP{space, nodesList}
}


// This function returns the matrix of distances between nodes
func (self *TSP) DistanceMatrix () [][]int {
  mat := make([][]int, len(self.nodes))
  for i, n := range self.nodes {
    mat[i] = make([]int, len(self.nodes))
    for j, m := range self.nodes {
      mat[i][j] = euclidean (n, m)
    }
  }
  return mat
}


// This function returns the euclidean distance between two nodes
func euclidean (n, m Node) int {
  return int(math.Sqrt(math.Pow(float64(n.x - m.x), 2.0)  +   math.Pow(float64(n.y - m.y), 2.0)))
}
