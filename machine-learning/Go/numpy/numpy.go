package numpy
/*
This package emulates the numpy Python package. It has been created
to collect all functions for working with matricies and vectors.
Written by Mattia Neroni in July 2020
Authors contact : mattia.neroni@unipr.it
*/


func Transpose (m [][]float64) [][]float64 {
	/*
		
	This function transpose a matrix.
	*/
	rows := len(m[0])
	cols := len(m)

	new_m := make([][]float64, rows)
	for i := 0; i < rows; i++ {
		new_m[i] = make([]float64, cols)
		for j := 0; j < cols; j++ {
			new_m[i][j] = m[j][i]
		}
	}

	return new_m
}







func Dot_matrix (x [][]float64, y [][]float64) [][]float64 {
	/*
		
		This function multiply (row x column) two matrices.
		
	*/
	rows := len(x)
	cols := len(y[0])
	new_m := make([][]float64, rows)
	for i := 0; i < rows; i++ {
		new_m[i] = make([]float64, cols)
		for j := 0; j < cols; j++ {
			var value float64 = 0
			for w := 0; w < len(x[0]); w++ {
				value += x[i][w] * y[w][j]
			}
			new_m[i][j] = value
		}
	}
	return new_m
}






func Dot_array (x []float64, y []float64) float64 {
	/*
	
	This function multiply (row x column) two arrays.
	
	*/
	var value float64 = 0
	for i := 0; i < len(x); i++ {value += x[i] * y[i]}
	return value
}
