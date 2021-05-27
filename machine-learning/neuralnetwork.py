import random
import numpy as np
import matplotlib.pyplot as plt


class NeuralNetwork:


    def __init__ (self, learning_rate = 0.05, layers=(3,4,2)):
        self.lr = learning_rate
        self.weights = np.array([np.random.rand(layers[i], layers[i+1]) for i in range(len(layers)-1)])
        self.layers = np.asarray([np.zeros(i) for i in layers])
    
    

    

    def _sigmoid (self, x):
        return np.exp(x) / (np.exp(x) + 1)
    
    
    
    

    def _sigmoid_derivative (self, x):
        return self._sigmoid(x) * (1 - self._sigmoid (x))


    
    
    
    
    def _feedforward (self, x):
        self.layers[0] = np.asarray(x)
        for i, (layer, w)  in enumerate(zip(self.layers[1:], self.weights)):
            self.layers[i+1] = self._sigmoid(np.dot(self.layers[i], w))
        return np.where (self.layers[-1] == max (self.layers[-1]))[0][0], self.layers[-1]
    
    
    
    
    
    
    
    def _backpropagation (self, x, y):
        _, y_pred = self._feedforward (x)
        d = None
        deltas = []
        for i in range(len(self.weights)-1, -1, -1):
            if d is None:
                d = (y - y_pred) * self._sigmoid_derivative(y_pred)
                deltas.append(np.multiply(d, self.layers[i][:, np.newaxis]))
            else:
                d = np.dot(self.weights[i+1], d) * self._sigmoid_derivative(self.layers[i+1])
                deltas.append(np.multiply(d, self.layers[i][:, np.newaxis]))
                
        self.weights += self.lr * np.asarray(deltas[::-1])
        return np.sum((y - y_pred)**2) / len(y)
    
  
    
    
    
    def test (self, X, y):
        errors = 0
        for x, answer in zip (X, y):
            res, _ = self._feedforward (x)
            if res != answer:
                errors += 1
        return errors
    
    
    
    
    
    
    def train (self, X, Y, iter=1000, verbose=False):
        losses = []
        for _ in range(iter):
            iter_losses = []
            for x, y in zip (X,Y):
                loss = self._backpropagation (x, y)
                iter_losses.append(loss)
            losses.append(np.average(iter_losses))
        if verbose is True:
            plt.plot(losses)
            plt.show()
            
            
   
