from __future__ import annotations

from src.astar.state import State


class Node:

    def __init__(self, state: State, cost: int, heuristic: int, parent=None):
        self.state = state
        self.cost = cost  # f(n)
        self.heuristic = heuristic  # h(n)
        self.value = cost + heuristic  # F(n) - Stored value. Will be larger than cost + heuristic when the node is collapsed
        self.parent = parent

    def __eq__(self, other: Node):
        return self.value == other.value

    def __lt__(self, other: Node):
        return (self.value, self.heuristic) < (other.value, other.heuristic)
