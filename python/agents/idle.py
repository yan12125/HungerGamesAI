from .agent import Agent

class IdleAgent(Agent):
    def __init__(self):
        super(IdleAgent, self).__init__()

    def once(self, state):
        pass
