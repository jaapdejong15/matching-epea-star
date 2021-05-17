import subprocess

from mapfmclient import Solution, MapfBenchmarker, Problem, ProgressiveDescriptor, BenchmarkDescriptor

from src.map_generation.map_generator import generate_map
from src.solver.exhaustive_matching_solver import ExhaustiveMatchingSolver
from src.visualizer import visualize

problem_cache_size = 100

def solve(problem: Problem) -> Solution:
    solver = ExhaustiveMatchingSolver(problem, problem_cache_size)
    return Solution.from_paths(solver.solve())


def get_version(is_debug, current_version) -> str:
    if not is_debug:
        return current_version
    git_hash = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
    return f"{git_hash}"

def run_online_benchmarker():
    version = '0.2.3'
    debug = True
    api_token = open('../apitoken.txt', 'r').read().strip()
    progressive_descriptor = ProgressiveDescriptor(
        min_agents=5,
        max_agents=5,
        num_teams=2
    )
    benchmarker = MapfBenchmarker(api_token, BenchmarkDescriptor(1, progressive_descriptor), f"EPEA* (exhaustive matching)", get_version(debug, version), debug,
                                  solver=solve,
                                  cores=1)
    benchmarker.run()

def run_maps():
    problem = generate_map(20, 20, [2, 2], open_factor=0.55, max_neighbors=2, min_goal_distance=0.5, max_goal_distance=1)
    solver = ExhaustiveMatchingSolver(problem)
    visualize(solver.grid, Solution.from_paths(solver.solve()))

if __name__ == '__main__':
    run_online_benchmarker()
