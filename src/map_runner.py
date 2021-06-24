import sys
from multiprocessing import Pool
from time import process_time, time
from typing import Optional, Tuple, List

from func_timeout import func_timeout, FunctionTimedOut
from mapfmclient import Problem

from src.map_generation.map_parser import MapParser
from src.solver.algorithm_descriptor import AlgorithmDescriptor, Algorithm
from src.solver.solver import Solver
from src.util.path import Path
from src.util.statistic_tracker import StatisticTracker


class BenchmarkQueue:
    """
    Queues map sets for benchmarking
    """

    __author__ = 'ivardb'

    def __init__(self, name):
        """
        Creates a BenchmarkQueue instance
        :param name:    Filename of the file with queued map set names
        """
        self.name = name
        with open(name, 'a'):
            pass

    def get_next(self):
        """
        Gets the next queue entry
        :return:    Name of the next map set
        """
        with open(self.name, 'r') as f:
            return f.readline().strip()

    def completed(self):
        """
        Removes the head of the queue
        """
        with open(self.name, 'r') as f_in:
            data = f_in.read().splitlines(True)
        with open(self.name, 'w') as f_out:
            f_out.writelines(data[1:])


class Dummy:
    """
    Dummy object for running a the solver on a single problem.
    """

    __author__ = 'ivardb'

    def __init__(self, time_out, end_time):
        """
        Creates the Dummy object
        :param time_out:    The amount of time that the solver is allowed to use to solve the instance
        :param end_time:    Time after which benchmarking must be ceased
        """
        self.timeout = time_out
        self.end_time = end_time

    def __call__(self, problem: Tuple[str, Problem]) -> Tuple[str, Optional[Tuple[float, int]]]:
        """
        Runs the benchmark
        :param problem:     Tuple of map name and MAPFM problem
        :return:            Tuple of map name and optional tuple of runtime and amount of evaluated goal assignments
        """
        return problem[0], test(problem[1], self.timeout, self.end_time)


class MapRunner:
    """
    Runs the solver multiple map sets.
    """

    __author__ = 'ivardb'

    def __init__(self, map_root: str):
        """
        Creates the MapRunner object.
        :param map_root:    Root folder of the benchmark maps
        """
        self.map_root = map_root
        self.map_parser = MapParser(map_root)

    def test_queue(self, time_out: float, benchmark_queue: BenchmarkQueue, output):
        """

        :param time_out:
        :param benchmark_queue:
        :param output:
        """
        task = benchmark_queue.get_next()
        while task is not None and task != "":
            print(task)
            res = self.test_generated(time_out, task)
            with open(output, 'a') as f:
                for r in res:
                    if r[1] is not None:
                        f.write(f"{task}, {r[0]}, {r[1][0]}, {r[1][1]}\n")
                    else:
                        f.write(f'{task}, {r[0]}, {None}, {None}\n')
                benchmark_queue.completed()
                task = benchmark_queue.get_next()

    def test_generated(self, time_out: float, folder: str):
        """
        Runs the solver on all problem instances in the folder
        :param time_out:    Time out for the solver
        :param folder:      Folder containing files with problem instances
        :return:            Results
        """
        problems = self.map_parser.parse_batch(folder)

        with Pool(processes=processes) as p:
            res = p.map(Dummy(time_out, end_time), problems)
        print()
        return res


def test(problem: Problem, time_out: float, end_time: float) -> Optional[Tuple[float, int]]:
    """
    Runs the solver on a problem instance.
    :param problem:     MAPFM problem instance
    :param time_out:    Time out for the solver
    :param end_time:    Time after which benchmarking should be ceased
    :return:            Tuple of runtime and amount of evaluated goal assignments if solved within timeout
    """
    if time() > end_time:
        raise Exception('Out of time!')
    start_time = process_time()
    solution = timeout(problem, time_out)
    print('.', end='', flush=True)
    if solution is not None:
        _, stat_tracker = solution
        return process_time() - start_time, stat_tracker.assignment_evaluation
    else:
        return None


def timeout(current_problem: Problem, time_out) -> Optional[Tuple[List[Path], StatisticTracker]]:
    """
    Runs the solver on a problem instance.
    :param current_problem:     MAPFM problem instance
    :param time_out:            Time out for the solver
    :return:                    Tuple of solution and statistic tracker
    """
    try:
        sol, stat_tracker = func_timeout(time_out, solve, args=[current_problem])
    except FunctionTimedOut:
        return None
    except Exception as e:
        print(f"An error occurred while running: {e}")
        return None
    return sol, stat_tracker


def solve(starting_problem: Problem) -> Tuple[Optional[List[Path]], StatisticTracker]:
    """
    Solves the given MAPFM problem instance.
    :param starting_problem:    MAPFM problem instance
    :return:                    Tuple with solution if found and statistic tracker
    """
    solver = Solver(starting_problem,
                    AlgorithmDescriptor(Algorithm.HeuristicMatching, independence_detection=True))
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
