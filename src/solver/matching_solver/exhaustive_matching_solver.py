from __future__ import annotations

from copy import copy
from heapq import heappush, heappop, heappushpop
from random import shuffle
from typing import List, Iterator

from mapfmclient import Problem, MarkedLocation

from src.solver.epeastar.epeastar import EPEAStar
from src.solver.epeastar.heuristic import Heuristic
from src.solver.epeastar.independence_detection import IDSolver
from src.solver.epeastar.mapf_problem import MAPFProblem
from src.solver.epeastar.osf import OSF
from src.util.agent import Agent
from src.util.coordinate import Coordinate
from src.util.grid import Grid
from src.util.path import Path


class Matching:
    """
    Represents a matching. Contains a MAPF-grid and an initial heuristic
    """

    __slots__ = 'agents', 'initial_heuristic'

    def __init__(self, agents: List[Agent], initial_heuristic: int):
        """
        Creates a Matching instance
        :param agents:              Agents with the agent color representing the matching
        :param initial_heuristic:
        """
        self.agents = agents
        self.initial_heuristic = initial_heuristic

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
        :param original:            Original problem that has to be solved.
        :param num_stored_problems: The amount of problems that should be stored at once.
        """
        self.num_stored_problems = num_stored_problems
        self.sorting = sorting
        self.independence_detection = independence_detection

        # Convert starting positions to agents
        self.colored_agents = [Agent(Coordinate(s.x, s.y), s.color, i) for i, s in enumerate(original.starts)]
        self.colored_goals = original.goals
        self.goals = [MarkedLocation(i, g.x, g.y) for i, g in enumerate(original.goals)]

        # Find all matches
        self.matches: List[List[Agent]] = []
        self.possible_matches([], 0)

        grid = Grid(original.width, original.height, original.grid)
        heuristic = Heuristic(grid, self.goals)
        osf = OSF(heuristic, grid)

        self.problem = MAPFProblem(grid, self.goals, osf, heuristic)

    def possible_matches(self, previous_agents: List[Agent], current_agent: int) -> None:
        """
        Recursive function for finding all possible matches for agents and goals
        :param previous_agents:  Assigned agents for earlier recursions
        :param current_agent:   Current agent for this round of recursion
        :return:                Nothing
        """
        for agent in self.colored_agents:
            if agent.color == self.colored_goals[current_agent].color and not any(
                    filter(lambda a: a.identifier == agent.identifier, previous_agents)):
                current_agents = copy(previous_agents)
                current_agents.append(Agent(copy(agent.coord),
                                            self.goals[current_agent].color,
                                            agent.identifier))
                if current_agent == len(self.colored_agents) - 1:
                    self.matches.append(sorted(current_agents))
                    continue
                self.possible_matches(current_agents, current_agent + 1)

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
            # Retrieve best matching from PQ and add new matching
            # TODO: Don't push on queue if initial heuristic is greater than best known cost
            next_matching = heappushpop(match_pq, Matching(match, self.get_initial_heuristic(match)))


            # If the initial heuristic is not able to improve the cost, the entire PQ will not be able to,
            # since this is the matching with the lowest initial heuristic in the PQ
            if next_matching.initial_heuristic >= min_cost:
                # Reset and fill match_pq:
                match_pq = self.fill_pq(match_iterator)

            # Solve problem
            if self.independence_detection:
                solver = IDSolver(self.problem, match, min_cost)
            else:
                solver = EPEAStar(self.problem, match, min_cost)
            solution = solver.solve()
            if solution is not None:
                paths, cost = solution
                if cost < min_cost:
                    min_cost = cost
                    min_solution = paths

        # Go through leftover matches in the PQ
        while len(match_pq) > 0:
            match = heappop(match_pq)

            # At this point all matches are in the PQ.
            # If the match with the best initial heuristic doesn't improve the cost then nothing will.
            if match.initial_heuristic >= min_cost:
                return min_solution

            # Solve problem
            if self.independence_detection:
                solver = IDSolver(self.problem, match.agents, min_cost)
            else:
                solver = EPEAStar(self.problem, match.agents, min_cost)
            solution = solver.solve()
            if solution is not None:
                paths, cost = solution
                if cost < min_cost:
                    min_cost = cost
                    min_solution = paths

        return min_solution

    def fill_pq(self, matching_iterator: Iterator[List[Agent]]):
        """
        Fills a priority queue with matchings
        :param matching_iterator:   Iterator for matchings
        :return:                    Heapified list of matchings, sorted on initial heuristic
        """
        match_pq = []
        for _ in range(self.num_stored_problems):
            match = next(matching_iterator, None)
            if match is not None:
                heappush(match_pq, Matching(match, self.get_initial_heuristic(match)))
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

            if self.independence_detection:
                solver = IDSolver(self.problem, match, min_cost)
            else:
                solver = EPEAStar(self.problem, match, min_cost)

            solution = solver.solve()

            # If the solver did not terminate early, update minimum solution and cost
            if solution is not None:
                paths, cost = solution
                if cost < min_cost:
                    min_cost = cost
                    min_solution = paths
        return min_solution

    def get_initial_heuristic(self, matching: List[Agent]):
        res = 0
        for ml in matching:
            # Include the cost of the starting position since that is also done in the real cost
            res += 1 + self.problem.heuristic.heuristic[ml.color][ml.coord.y][ml.coord.x]
        return res
