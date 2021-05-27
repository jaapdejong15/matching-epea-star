from typing import List

from src.util.coordinate import Coordinate
from src.util.direction import Direction


class Grid:
    __slots__ = 'width', 'height', 'grid', 'agents', 'goals', 'colors', 'heuristic'

    def __init__(self, width: int, height: int, grid: List[List[int]]):
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

