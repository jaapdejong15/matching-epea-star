import subprocess

from mapfmclient import Solution, MapfBenchmarker, Problem

from src.astar.id_solver import IDSolver

C = 0

def solve(problem: Problem) -> Solution:
    solver = IDSolver(problem, memory_constant=C)
    return solver.solve()


def get_version(debug, version) -> str:
    if not debug:
        return version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"


if __name__ == '__main__':
    version = '0.0.1'
    debug = True
    api_token = open('../apitoken.txt', 'r').read().strip()
    benchmarker = MapfBenchmarker(api_token, 13, f"PEA* + ID (C={C})", get_version(debug, version), debug, solver=solve,
                                  cores=1)
    benchmarker.run()
