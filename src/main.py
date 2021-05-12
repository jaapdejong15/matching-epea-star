import subprocess

from mapfmclient import Solution, MapfBenchmarker, Problem

from src.solver.exhaustive_matching_solver import ExhaustiveMatchingSolver


def solve(problem: Problem) -> Solution:
    solver = ExhaustiveMatchingSolver(problem)
    return Solution.from_paths(solver.solve())


def get_version(is_debug, current_version) -> str:
    if not is_debug:
        return current_version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"


if __name__ == '__main__':
    version = '1.0.0'
    debug = True
    api_token = open('../apitoken.txt', 'r').read().strip()
    benchmarker = MapfBenchmarker(api_token, 11, f"EPEA* (exhaustive matching) ", get_version(debug, version), debug,
                                  solver=solve,
                                  cores=1)
    benchmarker.run()
