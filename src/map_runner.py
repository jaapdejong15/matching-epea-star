from time import process_time
from multiprocessing import Pool
from typing import Optional

import numpy
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

    def __init__(self, time_out):
        self.timeout = time_out

    def __call__(self, object):
        return test(object, self.timeout)


class MapRunner:

    def __init__(self, map_root):
        self.map_root = map_root
        self.map_parser = MapParser(map_root)

    def test_queue(self, time_out, benchmark_queue: BenchmarkQueue, output):
        task = benchmark_queue.get_next()
        while task is not None and task != "":
            with open(output, 'a') as f:
                res, mean, std = self.test_generated(time_out, task)
                f.write(f"{task}: Completed: {res}, Average Time: {mean}, Standard Deviation: {std}\n")
                print(f"{task}: {res} with average {mean}s and deviaton: {std}\n")
                benchmark_queue.completed()
                task = benchmark_queue.get_next()

    def test_generated(self, time_out, folder):
        problems = self.map_parser.parse_batch(folder)

        with Pool(processes=4) as p:
            res = p.map(Dummy(time_out), problems)
        print()

        solved = 0
        times = []
        for s, t in res:
            solved += s
            if t is not None:
                times.append(t)
        mean = numpy.mean(times)
        std = numpy.std(times)
        return solved/len(problems), round(mean, 3), round(std, 5)


def test(problem: Problem, time_out):
    start_time = process_time()
    solution = timeout(problem, time_out)
    print('.', end='')
    if solution is not None:
        return 1, (process_time() - start_time)
    else:
        return 0, None


def timeout(current_problem: Problem, time_out) -> Optional[Solution]:
    try:
        sol = func_timeout(time_out, solve, args=[current_problem])

    except FunctionTimedOut:
        sol = None
    #except Exception as e:
    #    print(f"An error occurred while running: {e}")
    #    return None
    return sol


def solve(starting_problem: Problem):
    solver = Solver(starting_problem,
                    AlgorithmDescriptor(Algorithm.HeuristicMatching, independence_detection=True))
    return solver.solve()


if __name__ == "__main__":
    map_root = "../maps"
    queue = BenchmarkQueue("queue.txt")
    runner = MapRunner(map_root)
    runner.test_queue(30, queue, "results.txt")