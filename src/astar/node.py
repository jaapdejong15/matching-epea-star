from __future__ import annotations

from typing import Tuple

from src.astar.agent import Agent
from src.astar.state import State
from src.util.coordinate import Direction


class Node:

    def __init__(self, state: State, cost: int, heuristic: int, delta_f=0, parent=None):
        self.state: State = state
        self.cost: int = cost  # f(n)
        self.heuristic: int = heuristic  # h(n)
        self.value: int = cost + heuristic  # F(n) - Stored value. Will be larger than cost + heuristic when the node is collapsed
        self.delta_f = delta_f
        self.parent: Node = parent

    def __eq__(self, other: Node):
        return self.value == other.value

    def __lt__(self, other: Node):
        return (self.value, self.heuristic) < (other.value, other.heuristic)
