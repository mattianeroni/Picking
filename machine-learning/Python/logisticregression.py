"""
LOGISTIC REGRESSION
This is an implementation of the logistic regression.
It is written in pure Python 3 to be maintainable, portable, and easy to provide to third parties.
For errors and gradient descent an easy way of implementation has been provided, however, they
might be overwritten implementing new algorithms and procedures.

Written by Mattia Neroni in July 2020.
Author's contact : mattianeroni@yahoo.it

"""



"""
Imports from Python 3 standard libraries.
"""
#from typing import List, Tuple, cast

import numpy # type: ignore
import math
import statistics
import random
import array
import matplotlib.pyplot as plt









def prepare_test (X, y, test_size = 0.3):
    """
    Given a set of input data, and a set of output data, this method split them
    according to the size defined.
    Part of the data is placed in the test dataset, the remaining part in the 
    training dataset.
    :param X: <list<list>>The matrix of input data
    :param y: <list> The correct outputs
    :param test_size: <float> The percentage of the total data, which is kept for the tests
    :return: <tuple> Input data to use in the tests, Input data to use in the training,
                     correct outputs for the tests, correct outputs for the training.
    """
    data_test, data_train, y_test, y_train = [], [], [], []

    for data, answer in zip (X, y):
        r = random.random()
        if r < test_size:
            data_test.append (data)
            y_test.append (answer)
        else:
            data_train.append (data)
            y_train.append (answer)

    return numpy.array(data_test), numpy.array(data_train), numpy.array(y_test), numpy.array(y_train)











class LogisticRegression:
    """
    This is the logistic regression class. 
    Before being used, it must be instantiated.
    """
    def __init__ (self, learning_rate = 0.01, num_iter = 30_000, verbose = False):
        """
        Initialize.
        :param learning_rate: <float> The learning rate of the regression
        :param num_iter: <int> The number of iterations used in the training
        :param verbose: <bool> If True, during the training, the regression prints all 
                        the results to show the improvement.
        :attr weights: The weights (i.e. thetas) on the entering edges.
        """
        self.lr = learning_rate
        self.num_iter = num_iter
        self.verbose = verbose

        self.weights = None





    @staticmethod
    def _sigmoid (x, weights):
        """
        This method, given an array of inputs and the array of the weights, 
        returns the response of the regression by adopting a sigmoid
        function.
        :param x: <array> Array of inputs
        :param weights: <array> Array of weights in the respective entering edges.
        :return: <float> The prediction of the regression.
        """
        z = numpy.dot(x, weights)
        return 1 / (1 + numpy.exp(-z))




    
    

    def prediction (self, x):
        """
        This method is used for the prevision of a single element by using the current weights.
        :param x: <list> The input data necessary for the prevision.
        :return: The response (i.e. 0 or 1).
        """
        return round (self._sigmoid (x, self.weights))


    
    
    
    
    @staticmethod
    def _fuzzy_prediction (X, weights):
        """
        This method makes the predictions used for training. It takes a long
        set of inputs, and, by using the sigmoid function, it returns the 
        probabilities associated to each output.
        
        :param X: <list<list>> The matrix of inputs
        :param weights: <list> The weights on the edges
        :return: <list> The array of the predictions
        
        """
        return 1 / (1 + numpy.exp(- numpy.dot (weights, X.T)))
    
    
    
    
    



    @staticmethod
    def _get_loss (h, y):
        """
        Once a prediction has been made, this method evaluates its quality.
        Several different indexes might be used to evaluate the prediction, but in this 
        implementation we calculate it as the average error on all the responses.
        Alternatively, it might be used:
            - MAPE
            - MSE
            - MAE
            - etc...
        Since the logistic regression can be used only for classification, given h
        the actual response, and y the expected response, each error is calculated as:
            1) -log(h),     if y = 1
            2) -log(1 - h), if y = 0
        """
        return (-y * numpy.log(h + 1e-5) - (1 - y) * numpy.log(1 - h + 1e-5)).mean()






    @staticmethod
    def _get_gradient (X, h, y):
        """
        This method calculates the gradient, which is the partial derivative of the 
        of the total error made by the prediction.
        :param X: The matrix of the input data.
        :param h: The array of the predictions made.
        :param y: The array of the results the prediction was supposed to provide.
        :result: The intensity and the directions according to which each weight is going to be changed.
        """
        errors_with_sign = h - y
        return numpy.dot(numpy.transpose(X), errors_with_sign) / len(y)



    
    
    
    @staticmethod
    def _add_intercept (X):
        """
        This method adds an array of ones in front of each array of inputs
        and, in this way, it allows the use of the intercept, which makes the
        predictions more accurate.
        
        :param X: The set of inputs
        :return: The set of inputs with the value corresponding to the intercept
        
        """
        intercept = numpy.ones((X.shape[0], 1))
        return numpy.concatenate((intercept, X), axis=1)



    
    

    def fit (self, X, y):
        """
        In this method is written the training procedure based on the Gradient Descendent 
        algorithm.
        :param X: The matrix of the input data.
        :param y: The expected predictions.
        """
        history = array.array('d',[0.0 for _ in range(self.num_iter // 1000)])
        self.weights = numpy.random.rand(len(X[0]) + 1)
        X = self._add_intercept (X)

        for i in range(self.num_iter):
            h = self._fuzzy_prediction (X, self.weights)
            gradient = self._get_gradient (X, h, y)
            self.weights = numpy.asarray(self.weights) - self.lr * gradient

            if self.verbose is True and i % 1000 == 0:
                loss = self._get_loss(h, y)
                print (f"Iteration {i} -> Loss {loss}")
                history[i // 1000] = loss
                
        if self.verbose is True:
            plt.plot(history)
            plt.show()







    def test (self, X, y):
        """
        This method test the regression on a dataset with the current weights and 
        finally returns the percentage error and the answers provided by the 
        regression.
        :param X: The matrix of the input data
        :param y: The correct answers
        :return: <tuple> The percentage error and the previsions made by the regression.
        """
        previsions = array.array('i', [-1 for _ in range(len(y))])
        error_num : int = 0
            
        for i, (x, answer) in enumerate(zip (X, y)):
            
            x = numpy.insert (x, 0, 1)
            p = self.prediction (x)
            previsions[i] = p

            if p != answer:
                error_num += 1

        return round(100 * error_num / len(y), 2), previsions
