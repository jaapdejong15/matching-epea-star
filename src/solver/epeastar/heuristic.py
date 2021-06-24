from heapq import heappush, heappop
from typing import Dict, List, Any

from mapfmclient import MarkedLocation

from src.util.coordinate import Coordinate
from src.util.grid import Grid


class Heuristic:
    """
    Contains the precomputed heuristic function. Values are computed when instance is constructed.
    """

    def __init__(self, grid: Grid, goals: List[MarkedLocation]):
        """
        Creates and calculates a precomputed Heuristic function
        :param grid:    2D grid of the problem instance
        :param goals:   List of goals
        """
        self.grouped_goals = self.__group_by_color(goals)
        self.heuristic: Dict[int, List[List[Any]]] = {}
        self.__compute_sic_heuristic(grid)

    def __getitem__(self, item):
        return self.heuristic[item]

    def __compute_sic_heuristic(self, grid: Grid) -> None:
        """
        Computes the Sum of Individual Costs (SIC) heuristic for each color by performing a bread-first search from all
        goals of the color.
        :param grid:    2D grid of the problem instance
        """
        for color, goals in self.grouped_goals.items():
            self.heuristic[color] = [[float('inf')] * grid.width for _ in range(grid.height)]
            assert len(self.heuristic[color][0]) == grid.width
            assert len(self.heuristic[color]) == grid.height

            seen = set()
            frontier: List[BFSNode] = []
            for goal in goals:
                heappush(frontier, BFSNode(Coordinate(goal.x, goal.y), 0))
                seen.add(Coordinate(goal.x, goal.y))

            while frontier:
                node = heappop(frontier)
                self.heuristic[color][node.pos.y][node.pos.x] = node.cost
                neighbors = grid.get_neighbors(node.pos)
                for neighbor in neighbors:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        heappush(frontier, BFSNode(neighbor, node.cost + 1))

    @staticmethod
    def __group_by_color(goals: List[MarkedLocation]) -> Dict[int, List[MarkedLocation]]:
        """
        Groups all goals by color
        :param goals:   List of goals
        :return:        Dictionary with a list of goals for each color as key
        """
        grouped = dict()
        for goal in goals:
            if grouped.get(goal.color):
                grouped[goal.color].append(goal)
            else:
                grouped[goal.color] = [goal]
        return grouped


class BFSNode:
    """
    Node used for breadth-first search for precomputing the heuristic
    """

    __slots__ = 'pos', 'cost'

    def __init__(self, pos: Coordinate, cost: int):
        """
        Constructs a BFSNode instance
        :param pos:     Position coordinate
        :param cost:    Cost of reaching the position
        """
        self.pos = pos
        self.cost = cost

    def __eq__(self, other):
        """
        Returns whether this node equals the other node
        :param other:   Node to compare with
        :return:        True if equal, False otherwise
        """
        return self.pos == other.pos and self.cost == other.cost

    def __lt__(self, other):
        """
        Returns whether this node has a lower cost than the other node. This allows nodes to be sorted on cost.
        :param other:   Other node
        :return:        True if this node has a lower cost than the other node, False otherwise
        """
        return self.cost < other.cost
