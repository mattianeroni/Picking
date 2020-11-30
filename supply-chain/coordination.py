
# Imports from Python 3 standard library
import matplotlib.pyplot as plt
import random
import numpy as np
import array


class Agent (object):
    """
    An instance of this class represents an agent.
    """
    def __init__ (self, func, Ti, alpha):
        """
        Initialize.

        :param func: The cost function.
        :param Ti: The starting temperature.
        :param alpha: The cooling parameter. The smaller is alpha, the faster the acceptance probability
                        decreases.
        :attr best: <tuple> The best solution found so far and its cost.

        """
        self.func = func
        self.alpha = alpha
        self.temperature = Ti
        self.best = (None, float("inf"))


    def accept (self, x):
        """
        This method returns TRUE if the agent accepts a certain solution,
        and FALSE otherwise.
        For the acceptance criterion the Boltzman rule is used:

            f(x) = 1,                     if cost(x) < cost(best)
            f(x) = e^((best - cost) / T), if cost(x) >= cost(best)

        where T is the current temperature and best the best solution accepted
        so far.

        :param x: The solution proposed by the mediator.
        :param temperature: The current temperature.
        :return: True is the solution is accepted, False otherwise
        """
        return (cost := self.func(x)) < (best := self.best[1]) or random.random() < np.exp((best - cost) / self.temperature), cost


    def cooling (self):
        """
        This is the cooling schedule of the agent.
        :return: The temperature after cooling.
        """
        self.temperature *= self.alpha
        return self.temperature



    def plot_func (self, r=range(-200, 200)):
        """
        Plot the graph of the func.
        :param r: The range where to show the funtion
        :return: None
        """
        y = [self.func (i) for i in r]
        plt.plot(r, y)
        plt.show()




class Mediator (object):
    """
    An instance of this class represents the mediator.
    """
    def __init__ (self, agent1, agent2, max_iter, learning_rate, space=(-1000, 1000)):
        """
        Initialize.

        :param agent1: The first agent
        :param agent2: The second agent
        :param max_iter: The number of iterations
        :param learning_rate: A parameter that describe how far is the new generation
                                generated at each step from the current one
        :param space: The explorable range of solutions

        :attr best: The best solution.
        :attr accepted: The number of solutions generated accepted by
                        both the agents
        :attr history: The history of best solution (for mediator point of view)
        :attr history1: The history of best solutions for first agent point of view
        :attr history2: The history of best solutions for second agent point of view
        """
        self.agent1 = agent1
        self.agent2 = agent2
        self.max_iter = max_iter
        self.lr = learning_rate
        self.space = space

        self.best = (None, float('inf'))
        self.history = array.array('f', [])
        self.history1 = array.array('f', [])
        self.history2 = array.array('f', [])
        self.accepted = 0


    def info (self):
        """
        This method prints some useful informations concerning the Mediator and the Agents
        according to the parameters defined by the user.
        :return: None
        """
        print(f"Final temperature of Agent1 is going to be {agent1.temperature * (agent1.alpha ** self.max_iter)}")
        print(f"Final temperature of Agent2 is going to be {agent2.temperature * (agent2.alpha ** self.max_iter)}")



    def newsolution (self, current, best, lr):
        """
        This method generates a new solution.

        :param current: <tuple> The current solution and its cost
        :param best: <tuple> The best solution and its cost
        :param lr: The learning rate
        :param m: The minimum position explorable so far
        :param M: The maximumposition explorable so far
        :return: The new solution
        """
        if current[1] == float("inf") or best[1] - current[1] < 1e-10:
            m, M = self.space
            return random.randint(m,M)
        else:
            gradient = best[0] - current[0]
            return current[0] + int(gradient * lr)





    def __call__(self):
        """
        The execution of the algorithm.
        :return: None
        """
        history = array.array("f", [-1 for _ in range(self.max_iter)])
        history1 = array.array("f", [-1 for _ in range(self.max_iter)])
        history2 = array.array("f", [-1 for _ in range(self.max_iter)])
        accepted = 0

        a1, a2 = self.agent1, self.agent2
        best = (None, float("inf"))
        current = best

        newsolution = self.newsolution
        lr = self.lr

        for i in range(self.max_iter):
            s = newsolution (current, best, lr)
            resp1, c1 = a1.accept(s)
            resp2, c2 = a2.accept(s)
            current = (s, c1 + c2)

            if resp1 is True and resp2 is True:
                accepted += 1
                if (tc := c1 + c2) < best[1]:
                    best = (s, tc)
                    a1.best = best; a2.best = best

            a1.cooling(); a2.cooling()

            history[i] = best[1]
            history1[i] = c1
            history2[i] = c2

        self.history, self.history1, self.history2 = history, history1, history2
        self.accepted = accepted
        self.best = best
