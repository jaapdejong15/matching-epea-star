from __future__ import annotations

import itertools
from heapq import heappush, heappop, heappushpop
from typing import List, Iterator, Tuple, Optional

from mapfmclient import MarkedLocation

from src.solver.epeastar.epeastar import EPEAStar
from src.solver.epeastar.heuristic import Heuristic
from src.solver.epeastar.independence_detection import IDSolver
from src.solver.epeastar.mapf_problem import MAPFProblem
from src.solver.epeastar.osf import OSF
from src.util.agent import Agent
from src.util.coordinate import Coordinate
from src.util.grid import Grid
from src.util.group import Group
from src.util.matching import Matching
from src.util.path import Path

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
                 grid: Grid,
                 heuristic: Heuristic,
                 osf: OSF,
                 group: Group,
                 starts: List[MarkedLocation],
                 goals: List[MarkedLocation],
                 num_stored_problems: int = 0,
                 sorting: bool = False,
                 independence_detection: bool = True):
        """
        Constructs the ExhaustiveMatchingSolver object
        TODO: Fix parameter descriptions
        """
        self.num_stored_problems = num_stored_problems
        self.sorting = sorting
        self.independence_detection = independence_detection

        # Convert starting positions to agents
        self.colored_agents: List[Agent] = [Agent(Coordinate(starts[i].x, starts[i].y), starts[i].color, i) for i in group]
        self.colored_goals = goals
        self.goals = [MarkedLocation(i, g.x, g.y) for i, g in enumerate(goals)]
        #self.goals = goals
        # Find all matches
        goal_ids = []
        # Find goal ids for every agent
        for agent in self.colored_agents:
            ids = []
            for i, goal in enumerate(self.colored_goals):
                if agent.color == goal.color:
                    ids.append(i)
            # TODO: Sort by individual heuristic?
            goal_ids.append(ids)

        self.matches: Iterator[Tuple[int, ...]] = filter(lambda x: len(set(x)) == len(self.colored_agents), itertools.product(*goal_ids))

        self.problem = MAPFProblem(grid, self.goals, osf, heuristic)

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
        # TODO: Shuffling makes sure that we have a representative sample of all matchings. Otherwise with a lot of samples
        # and a limited PQ size, the matching of the first team will be the same in the entire PQ
        #if len(self.matches) > self.num_stored_problems:
        #    shuffle(self.matches)

        min_cost = float('inf')
        min_solution = None

        # Fill the priority queue
        match_pq = self.fill_pq(self.matches)

        # Evaluate the best matchings while keeping the PQ filled
        for match in self.matches:
            match: Tuple[int]

            # Retrieve best matching from PQ and add new matching
            # TODO: Don't push on queue if initial heuristic is greater than best known cost
            next_matching = heappushpop(match_pq, Matching(match, self.get_initial_heuristic(match)))


            # If the initial heuristic is not able to improve the cost, the entire PQ will not be able to,
            # since this is the matching with the lowest initial heuristic in the PQ
            if next_matching.initial_heuristic >= min_cost:
                # Reset and fill match_pq:
                match_pq = self.fill_pq(self.matches)

            solution = self.calculate_solution(next_matching.agent_ids, min_cost)
            if solution is not None:
                paths, cost = solution
                if cost < min_cost:
                    min_cost = cost
                    min_solution = paths

        # Go through leftover matches in the PQ
        while len(match_pq) > 0:
            match: Matching = heappop(match_pq)

            # At this point all matches are in the PQ.
            # If the match with the best initial heuristic doesn't improve the cost then nothing will.
            if match.initial_heuristic >= min_cost:
                return sorted(min_solution)

            solution = self.calculate_solution(match.agent_ids, min_cost)
            if solution is not None:
                paths, cost = solution
                if cost < min_cost:
                    min_cost = cost
                    min_solution = paths

        return sorted(min_solution)

    def fill_pq(self, matching_iterator):
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
            solution = self.calculate_solution(match, min_cost)

            # If the solver did not terminate early, update minimum solution and cost
            if solution is not None:
                paths, cost = solution
                if cost < min_cost:
                    min_cost = cost
                    min_solution = paths
        return sorted(min_solution)

    def calculate_solution(self, match: Tuple[int], min_cost: int) -> Optional[Tuple[List[Path], int]]:
        agents = []
        for i, j in enumerate(match):
            agents.append(Agent(self.colored_agents[j].coord, i, j))

        if self.independence_detection:
            solver = IDSolver(self.problem, agents, min_cost)
        else:
            solver = EPEAStar(self.problem, agents, min_cost)

        return solver.solve()

    def get_initial_heuristic(self, matching: Tuple[int]):
        res = 0
        for i, j in enumerate(matching):
            # Include the cost of the starting position since that is also done in the real cost
            res += 1 + self.problem.heuristic.heuristic[self.goals[i].color][self.colored_agents[j].coord.y][self.colored_agents[j].coord.x]
        return res
