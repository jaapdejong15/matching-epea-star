from typing import Optional, List, Tuple

from mapfmclient import Problem

from src.solver.epeastar.epeastar import EPEAStar
from src.solver.epeastar.heuristic import Heuristic
from src.solver.epeastar.independence_detection import IDSolver
from src.solver.epeastar.mapf_problem import MAPFProblem
from src.solver.epeastar.osf import OSF
from src.util.agent import Agent
from src.util.coordinate import Coordinate
from src.util.grid import Grid
from src.util.path import Path
from src.util.statistic_tracker import StatisticTracker


class HeuristicMatchingSolver:
    """
    Solves a problem using heuristic matching.
    With heuristic matching, the A* heuristic for an individual agent is the distance to the closest goal of the
    same color.
    """

    def __init__(self, problem: Problem, independence_detection=True):
        """
        Constructs a HeuristicMatchingSolver instance
        :param problem:                The MAPFM problem that has to be solved
        :param independence_detection: Whether Independence Detection (ID) should be used
        """
        self.stat_tracker = StatisticTracker()
        self.problem = problem
        self.independence_detection = independence_detection
        agents = [Agent(Coordinate(s.x, s.y), s.color, i) for i, s in enumerate(problem.starts)]
        self.grid = Grid(problem.width, problem.height, problem.grid)

        heuristic = Heuristic(self.grid, problem.goals)
        osf = OSF(heuristic, self.grid)
        mapf_problem = MAPFProblem(self.grid, problem.goals, osf, heuristic)
        if self.independence_detection:
            self.solver = IDSolver(mapf_problem, agents, None, self.stat_tracker)
        else:
            self.solver = EPEAStar(mapf_problem, agents, [], self.stat_tracker)

    def solve(self) -> Tuple[Optional[List[Path]], StatisticTracker]:
        """
        Solves the problem with which the solver instance was instantiated
        :return:    Solution if it was found
        """
        return self.solver.solve()[0], self.stat_tracker
