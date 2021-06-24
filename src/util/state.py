from typing import List

from src.util.agent import Agent


class State:
    """
    A state in the MAPF(M) problem consists of the agent positions.
    """

    __slots__ = 'agents'

    def __init__(self, agents: List[Agent]):
        self.agents = tuple(agents)

    def __eq__(self, other):
        return self.agents == other.agents

    def __hash__(self):
        return hash(self.agents)

    def __repr__(self):
        return self.agents.__repr__()
