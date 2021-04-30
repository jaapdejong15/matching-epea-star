from mapfmclient import Problem

from src.astar.agent import Agent
from src.problem.mapf_problem import MAPFProblem
from src.util.coordinate import Coordinate
from src.util.grid import Grid


class MatchingProblem(MAPFProblem):

    def __init__(self, original: Problem, compute_heuristic=False):
        agents = [Agent(Coordinate(s.x, s.y), s.color, i) for i, s in enumerate(original.starts)]
        goals = original.goals
        grid = Grid(original.width, original.height, original.grid, agents, goals, compute_heuristic)
        super().__init__(grid)
