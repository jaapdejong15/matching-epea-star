from __future__ import annotations

from copy import copy
from heapq import heappush, heappop, heappushpop
from random import shuffle
from typing import List, Iterator

from mapfmclient import Problem, MarkedLocation

from src.solver.epeastar.epeastar import EPEAStar
from src.solver.epeastar.independence_detection import IDSolver
from src.util.agent import Agent
from src.util.coordinate import Coordinate
from src.util.grid import Grid
from src.util.path import Path


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


class ExhaustiveMatchingSolver:
    """
    Solves an algorithm using exhaustive matching. There are two versions.
    In both versions, all matchings are generated.

    In normal exhaustive matching, the matchings are evaluated in their normal order.
    The solver keeps track of the lowest cost and the underlying MAPF solvers terminate immediately
    once that cost is exceeded.

    In sorted exhaustive matchings, the solver first generates a grid and calculates the initial heuristic of the
    matching. The matchings are then heapified and evaluated one by one.
    This forces the solver to use the most promising matchings first, which will likely result in a lower minimum cost
    earlier in the process. As a result, the runtime of the underlying solvers for later algorithms is decreased because
    they can stop earlier
    """

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
            return self.sorting_solve()
        else:
            return self.default_solve()

    def sorting_solve(self) -> List[Path]:
        """
        Creates grids for a certain number of problems and solves the problems one by one to find the best solution
        :return:    A path for every agent
        """
        # Shuffling makes sure that we have a representative sample of all matchings. Otherwise with a lot of samples
        # and a limited PQ size, the matching of the first team will be the same in the entire PQ
        if len(self.matches) > self.num_stored_problems:
            shuffle(self.matches)
        match_iterator = iter(self.matches)

        min_cost = float('inf')
        min_solution = None

        # Fill the priority queue
        match_pq = self.fill_pq(match_iterator)

        # Evaluate the best matchings while keeping the PQ filled
        for match in match_iterator:
            grid = Grid(self.grid.width, self.grid.height, self.grid.grid, self.grid.agents, match)

            # Retrieve best matching from PQ and add new matching
            next_matching = heappushpop(match_pq, Matching(grid))

            # If the initial heuristic is not able to improve the cost, the entire PQ will not be able to,
            # since this is the matching with the lowest initial heuristic in the PQ
            if next_matching.initial_heuristic >= min_cost:
                # Reset and fill match_pq:
                match_pq = self.fill_pq(match_iterator)

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

            # At this point all matches are in the PQ.
            # If the match with the best initial heuristic doesn't improve the cost then nothing will.
            if next_matching.initial_heuristic >= min_cost:
                return min_solution

            # Solve problem
            id_solver = IDSolver(next_matching.grid, min_cost)
            solution = id_solver.solve()
            if solution is not None:
                paths, cost = solution
                if cost < min_cost:
                    min_cost = cost
                    min_solution = paths
        return min_solution

    def fill_pq(self, matching_iterator: Iterator[List[MarkedLocation]]):
        """
        Fills a priority queue with matchings
        :param matching_iterator:   Iterator for matchings
        :return:                    Heapified list of matchings, sorted on initial heuristic
        """
        match_pq = []
        for _ in range(self.num_stored_problems):
            match = next(matching_iterator, None)
            if match is not None:
                grid = Grid(self.grid.width, self.grid.height, self.grid.grid, self.grid.agents, match)
                heappush(match_pq, Matching(grid))
            else:
                break
        return match_pq

    def default_solve(self) -> List[Path]:
        """
        Solves the problem by going through all matching in the normal way
        :return:    A path for every agent
        """
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

            # If the solver did not terminate early, update minimum solution and cost
            if solution is not None:
                paths, cost = solution
                if cost < min_cost:
                    min_cost = cost
                    min_solution = paths
        return min_solution
