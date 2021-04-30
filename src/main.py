import subprocess

from mapfmclient import Solution, MapfBenchmarker, Problem

from src.astar.astar import EPEAStar

# TODO: Base C of a formula if not given, e.g. C=#agents
from src.problem.standard_problem import StandardProblem

def solve(problem: Problem) -> Solution:
    solver = EPEAStar(StandardProblem(problem))
    return Solution.from_paths(solver.solve())

def get_version(is_debug, current_version) -> str:
    if not is_debug:
        return current_version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"


if __name__ == '__main__':
    version = '0.1.0'
    debug = True
    api_token = open('../apitoken.txt', 'r').read().strip()
    benchmarker = MapfBenchmarker(api_token, 14, f"EPEA*", get_version(debug, version), debug, solver=solve,
                                  cores=1)
    benchmarker.run()
