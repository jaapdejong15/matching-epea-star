import os
from datetime import datetime
from typing import Optional

from func_timeout import func_timeout, FunctionTimedOut
from mapfmclient import Problem, Solution

from src.map_generation.map_parser import MapParser
from src.solver.algorithm_descriptor import AlgorithmDescriptor, Algorithm
from src.solver.solver import Solver


def solve(starting_problem: Problem) -> Optional[Solution]:
    """
    Solves the given problem
    :param starting_problem:    Problem
    :return:                    Solution if it was found
    """
    problem = starting_problem
    algorithm = AlgorithmDescriptor(Algorithm.ExhaustiveMatchingSorting, independence_detection=True)
    solver = Solver(problem, algorithm)
    solution = solver.solve()
    if solution is None:
        print("Failed to find solution")
        return None
    return Solution.from_paths(solution)


class MapRunner:
    """
    Runs the algorithm on a batch of problems
    """

    def __init__(self, map_root):
        """
        Constructs a MapRunner instance
        :param map_root:    Root folder of the batch problem locations
        """
        self.map_root = map_root
        self.map_parser = MapParser(map_root)

    def timeout(self, current_problem: Problem, time) -> Optional[Solution]:
        """
        Tries to solve the problem within the timeout
        :param current_problem:     Problem
        :param time:                Timeout time
        :return:                    Solution if it was found
        """
        try:
            sol = func_timeout(time, solve, args=(current_problem,))

        except FunctionTimedOut:
            sol = None
        except Exception as e:
            print(f"An error occurred while running: {e}")
            return None
        return sol

    def test_generated(self, time, problem_folder) -> float:
        """
        Run the algorithm on a batch of problems
        :param time:            Timeout for the problems
        :param problem_folder:  Location of the problem batch
        :return:                Fraction of problems solved within timeout
        """
        problems = self.map_parser.parse_batch(problem_folder)
        solved = 0
        run = 0

        for i, problem in enumerate(problems):
            solution = self.timeout(problem, time)
            run += 1
            if solution is not None:
                solved += 1
        return solved / run


if __name__ == "__main__":
    map_root = "../maps"
    runner = MapRunner(map_root)
    now = datetime.now()
    for folder in (name for name in os.listdir(map_root) if os.path.isdir(os.path.join(map_root, name))):
        with open(f"../results/results-{now.strftime('%Y%m%d-%H%M%S')}.txt", "a") as f:
            res = runner.test_generated(30, folder)
            f.write(f"{folder}: {res}\n")
            print(f"{folder}: {res}")
