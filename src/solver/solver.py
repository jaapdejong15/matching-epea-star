from typing import List, Tuple, Optional

from mapfmclient import Problem

from src.solver.algorithm_descriptor import Algorithm, AlgorithmDescriptor
from src.solver.matching_solver.heuristic_matching_solver import HeuristicMatchingSolver
from src.solver.matching_solver.matching_id_solver import MatchingIDSolver
from src.util.path import Path
from src.util.statistic_tracker import StatisticTracker


class Solver:
    """
    Solves a MAPFM problem using the algorithm described at construction
    """

    def __init__(self, problem: Problem, algorithm: AlgorithmDescriptor):
        """
        Constructs a Solver instance
        :param problem:     Problem that the solver should solve
        :param algorithm:   Description of the algorithm that should be used to solve the problem
        """
        if algorithm.algorithm is Algorithm.ExhaustiveMatching:
            self.solver = MatchingIDSolver(problem,
                                           sorting=False,
                                           independence_detection=algorithm.id,
                                           matching_id=False)
        elif algorithm.algorithm is Algorithm.ExhaustiveMatchingSorting:
            self.solver = MatchingIDSolver(problem,
                                           num_goal_assignments=10000000,
                                           sorting=True,
                                           independence_detection=algorithm.id,
                                           matching_id=False)
        elif algorithm.algorithm is Algorithm.ExhaustiveMatchingSortingID:
            self.solver = MatchingIDSolver(problem,
                                           num_goal_assignments=10000000,
                                           sorting=True,
                                           independence_detection=algorithm.id,
                                           matching_id=True)

        elif algorithm.algorithm is Algorithm.HeuristicMatching:
            self.solver = HeuristicMatchingSolver(problem, independence_detection=algorithm.id)

    def solve(self) -> Tuple[Optional[List[Path]], StatisticTracker]:
        """
        Runs the algorithm to solve the MAPFM problem
        :return:    A path for every agent
        """
        return self.solver.solve()
