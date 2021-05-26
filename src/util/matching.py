from __future__ import annotations

from src.util.grid import Grid


class Matching:
    """
    Represents a matching. Contains a MAPF-grid and an initial heuristic
    """

    __slots__ = 'grid', 'initial_heuristic'

    def __init__(self, grid: Grid):
        """
        Creates a matching from the grid
        :param grid:    Grid
        """
        self.grid = grid
        self.initial_heuristic = 0

        for agent in self.grid.agents:
            self.initial_heuristic += grid.heuristic[agent.color][agent.coord.y][agent.coord.x]

    def __lt__(self, other: Matching) -> bool:
        """
        Allows matchings to be sorted/heapified by their initial heuristic
        :param other:   Matching to compare with
        :return:        True if this matching has a lower initial heuristic
        """
        return self.initial_heuristic < other.initial_heuristic
