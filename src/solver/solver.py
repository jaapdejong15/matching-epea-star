from typing import List

from mapfmclient import Problem

from src.solver.algorithm_descriptor import Algorithm, AlgorithmDescriptor
from src.solver.matching_solver.exhaustive_matching_solver import ExhaustiveMatchingSolver
from src.solver.matching_solver.heuristic_matching_solver import HeuristicMatchingSolver
from src.util.path import Path


class Solver:

    def __init__(self, problem: Problem, algorithm: AlgorithmDescriptor):
        if algorithm.algorithm is Algorithm.ExhaustiveMatching:
            self.solver = ExhaustiveMatchingSolver(problem)

        elif algorithm.algorithm is Algorithm.ExhaustiveMatchingSorting:
            self.solver = ExhaustiveMatchingSolver(problem, num_stored_problems=float('inf'), sorting=True)

        elif algorithm.algorithm is Algorithm.HeuristicMatching:
            self.solver = HeuristicMatchingSolver(problem, independence_detection=algorithm.id)

    def solve(self) -> List[Path]:
        return self.solver.solve()