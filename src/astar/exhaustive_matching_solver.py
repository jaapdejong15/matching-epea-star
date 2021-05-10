from copy import copy
from typing import List

from mapfmclient import Problem, MarkedLocation

from src.astar.agent import Agent
from src.astar.id_solver import IDSolver
from src.util.coordinate import Coordinate
from src.util.grid import Grid
from src.util.path import Path


class ExhaustiveMatchingSolver:

    def __init__(self, original: Problem):
        agents = [Agent(Coordinate(s.x, s.y), s.color, i) for i, s in enumerate(original.starts)]
        self.grid = Grid(original.width, original.height, original.grid, agents, original.goals)
        self.matches: List[List[MarkedLocation]] = []
        self.possible_matches([], 0)
        for agent in agents:
            agent.color = agent.identifier
        print([[f"({goal.x}, {goal.y}): {goal.color}" for goal in match] for match in self.matches])

    def possible_matches(self, previous_goals: List[MarkedLocation], current_agent: int):
        for goal in self.grid.goals:
            if goal.color == self.grid.agents[current_agent].color and not any(filter(lambda g: g.x == goal.x and g.y == goal.y, previous_goals)):
                current_goals = copy(previous_goals)
                current_goals.append(MarkedLocation(self.grid.agents[current_agent].identifier, goal.x, goal.y))
                if current_agent == len(self.grid.agents) - 1:
                    self.matches.append(current_goals)
                    continue
                self.possible_matches(current_goals, current_agent + 1)

    def solve(self):
        min_cost = float('inf')
        min_solution = None
        print(f'Num matches: {len(self.matches)}')
        for match in self.matches:
            print(f"Trying match {[(ml.x, ml.y) for ml in match]}")
            #TODO: Calculate goal heuristic only once
            grid = Grid(self.grid.width, self.grid.height, self.grid.grid, self.grid.agents, match)
            idsolver = IDSolver(grid)
            paths: List[Path] = idsolver.solve()
            cost = sum(path.cost for path in paths)
            if cost < min_cost:
                min_cost = cost
                min_solution = paths
        print(f"Cost = {min_cost}")
        return min_solution




