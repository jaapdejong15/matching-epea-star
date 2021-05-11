from typing import List

from src.solver.agent import Agent


class State:
    __slots__ = 'agents'

    def __init__(self, agents: List[Agent]):
        self.agents = tuple(agents)

    def __eq__(self, other):
        return self.agents == other.agents

    def __hash__(self):
        return hash(self.agents)

    def __repr__(self):
        return self.agents.__repr__()
