from heapq import heappush, heappop
from typing import List, Dict, Any

from mapfmclient import MarkedLocation

from src.util.agent import Agent
from src.util.coordinate import Coordinate, Direction


class BFSNode:
    def __init__(self, pos: Coordinate, cost: int):
        self.pos = pos
        self.cost = cost

    def __eq__(self, other):
        return self.pos == other.pos and self.cost == other.cost

    def __lt__(self, other):
        return self.cost < other.cost


class Grid:
    __slots__ = 'width', 'height', 'grid', 'agents', 'goals', 'colors', 'heuristic'

    def __init__(self, width: int, height: int, grid: List[List[int]], agents: List[Agent],
                 goals: List[MarkedLocation]):
        """
        Constructs a Grid instance
        :param width:   Width of the 2d grid
        :param height:  Height of the 2d grid
        :param grid:    2d int list that contains the grid. 1=wall, 0=open space
        :param agents:  List of agents
        :param goals:   List of goals
        """
        self.width = width
        self.height = height
        self.grid = grid
        self.agents = agents
        self.goals = goals
        self.colors: Dict[int, List[MarkedLocation]] = self.__get_colors()
        self.heuristic: Dict[int, List[List[Any]]] = {}
        self.__compute_sic_heuristic()

    def __compute_md_heuristic(self):
        """
        Computes the Manhattan Distance Heuristic for every color and location
        """
        for key in self.colors.keys():
            color_heuristic = []
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    h = float('inf')
                    for goal in self.colors[key]:
                        # Minimum manhattan distance
                        h = min(h, abs(x - goal.x) + abs(y - goal.y))
                    row.append(h)
                color_heuristic.append(row)
            self.heuristic[key] = color_heuristic

    def __compute_sic_heuristic(self) -> None:
        """
        Computes the Sum of Individual Costs (SIC) heuristic
        """
        for color, goals in self.colors.items():
            self.heuristic[color] = [[float('inf')] * self.width for _ in range(self.height)]
            assert len(self.heuristic[color][0]) == self.width
            assert len(self.heuristic[color]) == self.height

            seen = set()
            frontier: List[BFSNode] = []
            for goal in goals:
                heappush(frontier, BFSNode(Coordinate(goal.x, goal.y), 0))
                seen.add(Coordinate(goal.x, goal.y))

            while frontier:
                node = heappop(frontier)
                self.heuristic[color][node.pos.y][node.pos.x] = node.cost
                neighbors = self.get_neighbors(node.pos)
                for neighbor in neighbors:
                    if neighbor not in seen:
                        seen.add(neighbor)
                        heappush(frontier, BFSNode(neighbor, node.cost + 1))

    def __is_wall(self, x: int, y: int) -> bool:
        """
        Checks if there is a wall at the given coordinates
        :param x:   x coordinate
        :param y:   y coordinate
        :return:    True if there is a wall, False otherwise
        """
        return self.grid[y][x] == 1

    def traversable(self, pos: Coordinate) -> bool:
        """
        Checks if the position at the given coordinates is traversable by an agent.
        :param pos:     Agent position coordinates
        :return:        True if position is traversable, false otherwise
        """
        return self.traversable_coords(pos.x, pos.y)

    def traversable_coords(self, x: int, y: int) -> bool:
        """
        Checks if the position at the given coordinates is traversable by an agent.
        :param x:       Agent position x-coordinate
        :param y:       Agent position y-coordinate
        :return:        True if position is traversable, false otherwise
        """
        return 0 <= x < self.width and 0 <= y < self.height and not self.__is_wall(x, y)

    def get_neighbors(self, pos: Coordinate) -> List[Coordinate]:
        """
        Creates a list of traversable neighbors of a position
        :param pos:     Position coordinates
        :return:        List of neighbor coordinates
        """
        neighbors = []
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            neighbor = pos.move(direction)
            if self.traversable(neighbor):
                neighbors.append(neighbor)
        return neighbors

    def __get_colors(self) -> Dict[int, List[MarkedLocation]]:
        """
        Creates a dictionary with a list of goals for each color
        :return: Dictionary with list of goals for each color
        """
        colors = dict()
        for goal in self.goals:
            if colors.get(goal.color):
                colors[goal.color].append(goal)
            else:
                colors[goal.color] = [goal]
        return colors
