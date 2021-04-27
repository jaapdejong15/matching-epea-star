from src.util.coordinate import Coordinate, Direction
from typing import List

class Grid:
    def __init__(self, width: int, height: int, grid: List[List[int]]):
        self.width = width
        self.height = height
        self.grid = grid

    def __is_wall(self, pos: Coordinate) -> bool:
        return self.grid[pos.y][pos.x] == 1

    def traversable(self, pos: Coordinate) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height and not self.__is_wall(pos)

    def get_neighbors(self, pos: Coordinate) -> List[Coordinate]:
        neighbors = []
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            neighbor = pos.move(direction)
            if self.traversable(neighbor):
                neighbors.append(neighbor)
        return neighbors