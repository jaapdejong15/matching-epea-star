from typing import List, Dict, Any

from mapfmclient import MarkedLocation

from src.astar.agent import Agent
from src.util.coordinate import Coordinate, Direction
from heapq import heappush, heappop

class BFSNode:
    def __init__(self, pos: Coordinate, cost: int):
        self.pos = pos
        self.cost = cost

    def __eq__(self, other):
        return self.pos == other.pos and self.cost == other.cost

    def __lt__(self, other):
        return self.cost < other.cost

class Grid:
    def __init__(self, width: int, height: int, grid: List[List[int]], agents: List[Agent], goals: List[MarkedLocation]):
        self.width = width
        self.height = height
        self.grid = grid
        self.agents = agents
        self.goals = goals
        self.colors: Dict[int, List[MarkedLocation]] = self.__get_colors()
        self.heuristic: Dict[int, List[List[Any]]] = {}
        self.__compute_sic_heuristic()

    """
    Computes the Manhattan Distance Heuristic
    """
    def __compute_md_heuristic(self):
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

    """
    Computes the Sum of Individual Costs (SIC) heuristic
    """
    def __compute_sic_heuristic(self):
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
        return self.grid[y][x] == 1

    def traversable(self, pos: Coordinate) -> bool:
        return self.traversable_coords(pos.x, pos.y)

    def traversable_coords(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height and not self.__is_wall(x,y)

    def get_neighbors(self, pos: Coordinate) -> List[Coordinate]:
        neighbors = []
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            neighbor = pos.move(direction)
            if self.traversable(neighbor):
                neighbors.append(neighbor)
        return neighbors

    def __get_colors(self) -> Dict[int, List[MarkedLocation]]:
        colors = dict()
        for goal in self.goals:
            if colors.get(goal.color):
                colors[goal.color].append(goal)
            else:
                colors[goal.color] = [goal]
        return colors