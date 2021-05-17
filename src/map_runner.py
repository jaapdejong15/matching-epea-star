import os
from datetime import datetime
from typing import Optional

from func_timeout import func_timeout, FunctionTimedOut
from mapfmclient import Problem, Solution

from src.map_generation.map_parser import MapParser
from src.solver.matching_solver.exhaustive_matching_solver import ExhaustiveMatchingSolver


class MapRunner:

    def __init__(self, map_root):
        self.map_root = map_root
        self.map_parser = MapParser(map_root)

    def timeout(self, current_problem: Problem, time) -> Optional[Solution]:
        try:
            sol = func_timeout(time, self.solve, args=(current_problem,))

        except FunctionTimedOut:
            sol = None
        except Exception as e:
            print(f"An error occurred while running: {e}")
            return None
        return sol

    def solve(self, starting_problem: Problem) -> Optional[Solution]:
        #print()
        problem = starting_problem
        solver = ExhaustiveMatchingSolver(problem)
        solution = solver.solve()
        if solution is None:
            print("Failed to find solution")
            return None
        return Solution.from_paths(solution)

    def test_generated(self, time, folder, cores=1):
        problems = self.map_parser.parse_batch(folder)
        solved = 0
        run = 0

        for i, problem in enumerate(problems):
            #print(f"Testing: {folder} Run: {i + 1}/{len(problems)}, Solved: {solved}/{run}")
            solution = self.timeout(problem, time)
            run += 1
            if solution is not None:
                #print("Solved")
                solved += 1
            #else:
            #    print("Failed")
        return solved/run


if __name__ == "__main__":
    map_root = "../maps"
    runner = MapRunner(map_root)
    now = datetime.now()
    for folder in (name for name in os.listdir(map_root) if os.path.isdir(os.path.join(map_root, name))):
        with open(f"../results/results-{now.strftime('%Y%m%d-%H%M%S')}.txt", "a") as f:
            res = runner.test_generated(30, folder)
            f.write(f"{folder}: {res}\n")
            print(f"{folder}: {res}")
