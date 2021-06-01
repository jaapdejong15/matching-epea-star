from __future__ import annotations

from src.util.state import State


class Node:
    """
    A* tree search node
    """

    __slots__ = 'state', 'cost', 'heuristic', 'collisions', 'value', 'delta_f', 'parent', 'time'

    def __init__(self, state: State, cost: int, heuristic: int, collisions: int, time: int, delta_f=0, parent=None):
        """
        Constructs a Node instance
        :param state:       The state that is associated with this node
        :param cost:        The cost of reaching this node f(n)
        :param heuristic:   The heuristic h(n) (estimate of cost to reach the goal)
        :param delta_f:     Δf(n) value. Default value is zero, but this will be increased when the node is expanded.
        :param parent:      Parent node. Used when finding the path in the final solution
        """
        self.state: State = state
        self.cost: int = cost
        self.heuristic: int = heuristic
        self.collisions: int = collisions
        self.value: int = cost + heuristic  # F(n) - Stored value. Will be larger than cost + heuristic when the node is collapsed
        self.time: int = time
        self.delta_f = delta_f
        self.parent: Node = parent

    def __lt__(self, other: Node):
        """
        Compares this node with another node
        :param other:   Other node
        :returns:        True if the other node is less than this node, otherwise false
        """
        return (self.value, self.collisions, self.heuristic) < (other.value, other.collisions, other.heuristic)
