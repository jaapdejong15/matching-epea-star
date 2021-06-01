from __future__ import annotations

class Matching:
    """
    Represents a matching. Contains a MAPF-grid and an initial heuristic
    """

    __slots__ = 'initial_heuristic', 'agent_ids'

    def __init__(self, agent_ids, initial_heuristic):
        """
        Creates a matching from the grid
        :param grid:    Grid
        """
        self.agent_ids = agent_ids
        self.initial_heuristic = initial_heuristic

    def __lt__(self, other: Matching) -> bool:
        """
        Allows matchings to be sorted/heapified by their initial heuristic
        :param other:   Matching to compare with
        :return:        True if this matching has a lower initial heuristic
        """
        return self.initial_heuristic < other.initial_heuristic
