package logisticregression
/*
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

LOGISTIC REGRESSION

This is the implementation of a logistic regression which uses the Gradient Descent
algorithm in the training. The use of Go speeds up the training, which in Python 3 results
very slow, without drammatically reducing the development time.



Written by Mattia Neroni in July 2020

Authors contact : mattia.neroni@unipr.it

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
*/

import (
	"./numpy"
	"math"
)

type LogisticRegression struct {
	/*

	This is the logistic regression class.
	
	:param lr: The learning rate
	:param thetas: The weight assigned to the entering edges

	*/
	lr float64
	thetas []float64
}




func New_LogisticRegression (learning_rate float64) LogisticRegression {
	/*
	
	This is the constructor method for the logistic regression.
	The learning rate must be passed when the regression is instatiated,
	while the thetas are automatically defined when the training starts 
	(see Fit method).
	
	*/
	reg := LogisticRegression{}
	reg.lr = learning_rate
	return reg
}




func sigmoid (x float64) float64 {
	/*
	The sigmoid function.
	*/
	return 1 / (1 + math.Exp(-x))
}





func (self *LogisticRegression) Predict (x []float64) int {
	/*
	
	This method makes the prediction of a single input, which
	is provided to the logistic regression as an array of
	float numbers.
	
	*/
	z := numpy.Dot_array(x, self.thetas)
	return int(math.Round(sigmoid (z)))
}



func (self *LogisticRegression) fuzzy_predict (x []float64) float64 {
	/*
	
	This method is very similar to the Predict, but, while the
	Predict returns a respose, this one provides the probability 
	for which that respose has been given.
	This might be useful to understand the precision of the prediction.
	
	*/
	return sigmoid (numpy.Dot_array(x, self.thetas))
}






func (self *LogisticRegression) gradient_descent (X [][]float64, h []float64, y []int) []float64 {
	/*

	This method is the Gradient Descent algorithm, which, according to the errors
	in the previsions, defines how to update the thetas. The updates do not depend
	only on the gradient but on the learning rate too.

	*/
	errors := make([]float64, len(y))
	for i := 0; i < len(y); i++ {
		errors[i] = h[i] - float64(y[i])
	}

	gradient := make([]float64, len(X[0]))
	X_T := numpy.Transpose (X)
	for i := 0; i < len(X[0]); i++ {
		gradient[i] = numpy.Dot_array(X_T[i], errors) / float64(len(y))
	}

	return gradient
}







func (self *LogisticRegression) Test (X [][]float64, y []int) (int, int, []int) {
	/*

	This method tests the logistic regression over a set of inputs
	and it returns:
	- the number of errors
	- the total number of predictions
	- the resposes' array

	*/
	var errors int = 0
	predictions := make([]int, len(y))

	for i, data := range(X) {
		h := self.Predict (data)
		predictions[i] = h
		if h != y[i] {
			errors += 1
		}
	}

	return errors, len(y), predictions
}







func (self *LogisticRegression) Fit (X [][]float64, y []int, num_iter ...int) []float64 {
	/*

	This method trains the logistic regression over a set of inputs
	and it returns the thetas for which the regression has been 
	optimised.

	*/
	var max_iter int = 0
	if len(num_iter) == 0 {
		max_iter = 30000
	} else {
		max_iter = num_iter[0]
	}

	
	self.thetas = make([]float64, len(X[0]))
	for i := 0; i < len(X[0]); i++ {
		self.thetas[i] = 0
	}


	h := make([]float64, len(y))
	gradient := make([]float64, len(X[0]))

	for i := 0; i < max_iter; i++ {

		// makes the prevision
		for data := 0; data < len(y); data++ {
			h[data] = self.fuzzy_predict (X[data])
		}

		// calculate the gradient
		gradient = self.gradient_descent (X, h, y)

		// updates thetas
		for index := 0; index < len(self.thetas); index++ {
			self.thetas[index] = self.thetas[index] - self.lr * gradient[index]
		}
	}
	

	return self.thetas
}



