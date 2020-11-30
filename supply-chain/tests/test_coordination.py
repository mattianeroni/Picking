from supply_chain import Agent, Mediator  # !!! This is not working, the current file must be taken outside
                                          # the supply-chain folder.

if __name__ == '__main__':
    agent1 = Agent(lambda x: 1/4 * x**2, Ti=1000, alpha=0.996)
    agent2 = Agent(lambda x: 1/2 * (x - 100)**2, Ti=1000, alpha=0.996)
    #agent1.plot_func()
    #agent2.plot_func()
    m = Mediator(agent1, agent2, max_iter=1000, learning_rate=0.2)
    m ()
    print(m.best)
    print(m.accepted)
    plt.plot(m.history, "r")
    #plt.plot(m.history1, "g")
    #plt.plot(m.history2, "b")
    plt.show()
