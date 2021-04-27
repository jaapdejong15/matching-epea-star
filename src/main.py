from mapfmclient import Solution, MapfBenchmarker
from src.astar.astar import PEAStar, Problem
import subprocess

def solve(problem: Problem) -> Solution:
    peastar = PEAStar(problem)
    return peastar.solve()


def get_version(debug, version) -> str:
    if not debug:
        return version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"

if __name__ == '__main__':
    version = '0.0.1'
    debug=True
    api_token = open('../apitoken.txt', 'r').read().strip()
    benchmarker = MapfBenchmarker(api_token, 6, "PEA*", get_version(debug, version), debug, solver=solve, cores=1)
    benchmarker.run()



