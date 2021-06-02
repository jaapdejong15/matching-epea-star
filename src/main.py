import subprocess

from mapfmclient import Solution, MapfBenchmarker, Problem, ProgressiveDescriptor, BenchmarkDescriptor

from src.solver.algorithm_descriptor import AlgorithmDescriptor, Algorithm
from src.solver.solver import Solver


def solve(problem: Problem, algorithm: AlgorithmDescriptor) -> Solution:
    solver = Solver(problem, algorithm)
    return Solution.from_paths(solver.solve())


def get_version(is_debug, current_version) -> str:
    if not is_debug:
        return current_version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"


def run_online_benchmarker():
    version = '1.0.1'
    debug = True
    api_token = open('../apitoken.txt', 'r').read().strip()
    progressive_descriptor = ProgressiveDescriptor(
        min_agents=20,
        max_agents=20,
        num_teams=10
    )
    algorithm_descriptor = AlgorithmDescriptor(Algorithm.ExhaustiveMatchingSortingID,
                                               independence_detection=True)
    benchmarker = MapfBenchmarker(api_token, BenchmarkDescriptor(1, progressive_descriptor), algorithm_descriptor.get_name(),
                                  get_version(debug, version), debug,
                                  solver=lambda problem: solve(problem, algorithm_descriptor),
                                  cores=1)
    benchmarker.run()

if __name__ == '__main__':
    run_online_benchmarker()
