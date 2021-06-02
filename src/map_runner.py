import sys
from multiprocessing import Pool
from time import process_time, time

from typing import Optional


from func_timeout import func_timeout, FunctionTimedOut
from mapfmclient import Problem, Solution

from src.map_generation.map_parser import MapParser
from src.solver.algorithm_descriptor import AlgorithmDescriptor, Algorithm
from src.solver.solver import Solver


class BenchmarkQueue:

    def __init__(self, name):
        self.name = name
        with open(name, 'a'):
            pass

    def get_next(self):
        with open(self.name, 'r') as f:
            return f.readline().strip()

    def completed(self):
        with open(self.name, 'r') as f_in:
            data = f_in.read().splitlines(True)
        with open(self.name, 'w') as f_out:
            f_out.writelines(data[1:])

    def add(self, data):
        with open(self.name, 'a') as f:
            f.write(data + "\n")


class Dummy:

    def __init__(self, time_out, end_time):
        self.timeout = time_out
        self.end_time = end_time

    def __call__(self, object):
        return object[0], test(object[1], self.timeout, self.end_time)


class MapRunner:

    def __init__(self, map_root):
        self.map_root = map_root
        self.map_parser = MapParser(map_root)

    def test_queue(self, time_out, benchmark_queue: BenchmarkQueue, output):
        task = benchmark_queue.get_next()
        while task is not None and task != "":
            print(task)
            res = self.test_generated(time_out, task)
            with open(output, 'a') as f:
                for r in res:
                    f.write(f"{task}, {r[0]}, {r[1]}\n")
                benchmark_queue.completed()
                task = benchmark_queue.get_next()

    def test_generated(self, time_out, folder):
        problems = self.map_parser.parse_batch(folder)

        with Pool(processes=processes) as p:
            res = p.map(Dummy(time_out, end_time), problems)
        print()
        return res


def test(problem: Problem, time_out, end_time):
    if time() > end_time:
        raise Exception('Out of time!')
    start_time = process_time()
    solution = timeout(problem, time_out)
    print('.', end='', flush=True)
    if solution is not None:
        return process_time() - start_time
    else:
        return None


def timeout(current_problem: Problem, time_out) -> Optional[Solution]:
    try:
        sol = func_timeout(time_out, solve, args=[current_problem])
    except FunctionTimedOut:
        sol = None
    except Exception as e:
        print(f"An error occurred while running: {e}")
        return None
    return sol


def solve(starting_problem: Problem):
    solver = Solver(starting_problem,
                    AlgorithmDescriptor(Algorithm.ExhaustiveMatchingSorting, independence_detection=True))
    return solver.solve()


if __name__ == "__main__":
    start_time = time()
    run_minutes = float(sys.argv[1])
    end_time = time() + (run_minutes * 60)
    processes = int(sys.argv[2])
    map_root = "maps"
    queue = BenchmarkQueue("queue.txt")
    runner = MapRunner(map_root)
    runner.test_queue(120, queue, "results.txt")

