import subprocess

from mapfmclient import Solution, MapfBenchmarker

from src.astar.astar import PEAStar, Problem

C = 0
pre_compute_heuristics = True


def solve(problem: Problem) -> Solution:
    peastar = PEAStar(problem, memory_constant=C, pre_compute_heuristics=pre_compute_heuristics)
    return peastar.solve()


def get_version(debug, version) -> str:
    if not debug:
        return version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"


if __name__ == '__main__':
    version = '0.0.3'
    debug = True
    api_token = open('../apitoken.txt', 'r').read().strip()
    benchmarker = MapfBenchmarker(api_token, 10, f"PEA* (C={C})", get_version(debug, version), debug, solver=solve,
                                  cores=1)
    benchmarker.run()
