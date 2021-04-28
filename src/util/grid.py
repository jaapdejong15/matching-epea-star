from src.util.coordinate import Coordinate, Direction
from typing import List
from mapfmclient import MarkedLocation
from src.astar.agent import Agent

class Grid:
    def __init__(self, width: int, height: int, grid: List[List[int]], agents: List[Agent], goals: List[MarkedLocation], calculate_heuristic=False):
        self.width = width
        self.height = height
        self.grid = grid
        self.agents = agents
        self.goals = goals
        self.calculate_heuristic = calculate_heuristic
        self.heuristic = {}
        if calculate_heuristic:
            self.__compute_heuristic()

    def __compute_heuristic(self):
        colors = {}
        for goal in self.goals:
            if colors.get(goal.color):
                colors[goal.color].append(goal)
            else:
                colors[goal.color] = [goal]

        for key in colors.keys():
            color_heuristic = []
            for y in range(self.height):
                row = []
                for x in range(self.width):
                    h = float('inf')
                    for goal in colors[key]:
                        # Minimum manhattan distance
                        h = min(h, abs(x-goal.x) + abs(y-goal.y))
                    row.append(h)
                color_heuristic.append(row)
            self.heuristic[key] = color_heuristic

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