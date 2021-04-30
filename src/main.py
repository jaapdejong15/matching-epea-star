import subprocess

from mapfmclient import Solution, MapfBenchmarker, Problem

from src.astar.id_solver import IDSolver

# TODO: Base C of a formula if not given, e.g. C=#agents
C = 0


def solve(problem: Problem) -> Solution:
    solver = IDSolver(problem, memory_constant=C)
    return solver.solve()


def get_version(is_debug, current_version) -> str:
    if not is_debug:
        return current_version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"


if __name__ == '__main__':
    version = '0.0.2'
    debug = True
    api_token = open('../apitoken.txt', 'r').read().strip()
    benchmarker = MapfBenchmarker(api_token, 4, f"PEA* + ID (C={C})", get_version(debug, version), debug, solver=solve,
                                  cores=1)
    benchmarker.run()
