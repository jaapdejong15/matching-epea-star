from __future__ import annotations

from copy import copy
from typing import List

from heapq import heappush, heappop, heappushpop
from mapfmclient import Problem, MarkedLocation

from src.solver.epeastar.epeastar import EPEAStar
from src.util.agent import Agent
from src.solver.id_solver import IDSolver
from src.util.coordinate import Coordinate
from src.util.grid import Grid
from src.util.path import Path


class Matching:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.initial_heuristic = 0

        for agent in self.grid.agents:
            self.initial_heuristic += grid.heuristic[agent.color][agent.coord.y][agent.coord.x]

    def __lt__(self, other: Matching) -> bool:
        return self.initial_heuristic < other.initial_heuristic

class ExhaustiveMatchingSolver:

    def __init__(self,
                 original: Problem,
                 num_stored_problems: int = 0,
                 sorting: bool = False,
                 independence_detection: bool = True):
        """
        Constructs the ExhaustiveMatchingSolver object
        :param original:    Original problem that has to be solved.
        """
        self.num_stored_problems = num_stored_problems
        self.sorting = sorting
        self.independence_detection = independence_detection
        agents = [Agent(Coordinate(s.x, s.y), s.color, i) for i, s in enumerate(original.starts)]
        self.grid = Grid(original.width, original.height, original.grid, agents, original.goals)
        self.matches: List[List[MarkedLocation]] = []
        self.possible_matches([], 0)

        for agent in agents:
            agent.color = agent.identifier

    def possible_matches(self, previous_goals: List[MarkedLocation], current_agent: int) -> None:
        """
        Recursive function for finding all possible matches for agents and goals
        :param previous_goals:  Assigned goals for earlier recursions
        :param current_agent:   Current agent for this round of recursion
        :return:                Nothing
        """
        for goal in self.grid.goals:
            if goal.color == self.grid.agents[current_agent].color and not any(
                    filter(lambda g: g.x == goal.x and g.y == goal.y, previous_goals)):
                current_goals = copy(previous_goals)
                current_goals.append(MarkedLocation(self.grid.agents[current_agent].identifier, goal.x, goal.y))
                if current_agent == len(self.grid.agents) - 1:
                    self.matches.append(current_goals)
                    continue
                self.possible_matches(current_goals, current_agent + 1)

    def solve(self) -> List[Path]:
        """
        Finds an optimal solution to the problem provided in the constructor.
        :return:    List of paths of the optimal solution
        """
        if self.sorting:
            return self.sort_before_solve()
        else:
            return self.default_solve()


    def sort_before_solve(self) -> List[Path]:
        """
        Creates grids for a certain number of problems
        :return:
        """
        match_iterator = iter(self.matches)

        min_cost = float('inf')
        min_solution = None

        match_pq = []

        # Fill the priority queue
        for _ in range(self.num_stored_problems):
            match = next(match_iterator, None)
            if match is not None:
                grid = Grid(self.grid.width, self.grid.height, self.grid.grid, self.grid.agents, match)
                heappush(match_pq, Matching(grid))
            else:
                break

        # Evaluate the best matchings while keeping the PQ filled
        for match in match_iterator:
            grid = Grid(self.grid.width, self.grid.height, self.grid.grid, self.grid.agents, match)

            # Retrieve best matching from PQ and add new matching
            next_matching = heappushpop(match_pq, Matching(grid))

            # Solve problem
            if self.independence_detection:
                solver = IDSolver(next_matching.grid, min_cost)
            else:
                solver = EPEAStar(next_matching.grid, min_cost)
            solution = solver.solve()
            if solution is not None:
                paths, cost = solution
                if cost < min_cost:
                    min_cost = cost
                    min_solution = paths

        # Go through leftover matches in the PQ
        while len(match_pq) > 0:
            next_matching = heappop(match_pq)

            # Solve problem
            id_solver = IDSolver(next_matching.grid, min_cost)
            solution = id_solver.solve()
            if solution is not None:
                paths, cost = solution
                if cost < min_cost:
                    min_cost = cost
                    min_solution = paths
        return min_solution


    def default_solve(self):
        min_cost = float('inf')
        min_solution = None

        for match in self.matches:
           # TODO: Calculate goal heuristic only once
           grid = Grid(self.grid.width, self.grid.height, self.grid.grid, self.grid.agents, match)
           if self.independence_detection:
               solver = IDSolver(grid, min_cost)
           else:
               solver = EPEAStar(grid, min_cost)
           solution = solver.solve()
           if solution is not None:
               paths, cost = solution
               if cost < min_cost:
                   min_cost = cost
                   min_solution = paths
        return min_solution
