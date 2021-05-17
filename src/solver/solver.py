from typing import List

from mapfmclient import Problem

from src.solver.algorithm_descriptor import Algorithm, AlgorithmDescriptor
from src.solver.matching_solver.exhaustive_matching_solver import ExhaustiveMatchingSolver
from src.solver.matching_solver.heuristic_matching_solver import HeuristicMatchingSolver
from src.util.path import Path


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
            self.solver = ExhaustiveMatchingSolver(problem)

        elif algorithm.algorithm is Algorithm.ExhaustiveMatchingSorting:
            self.solver = ExhaustiveMatchingSolver(problem, num_stored_problems=10000, sorting=True)

        elif algorithm.algorithm is Algorithm.HeuristicMatching:
            self.solver = HeuristicMatchingSolver(problem, independence_detection=algorithm.id)

    def solve(self) -> List[Path]:
        """
        Runs the algorithm to solve the MAPFM problem
        :return:    A path for every agent
        """
        return self.solver.solve()
