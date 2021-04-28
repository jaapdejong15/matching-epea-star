from mapfmclient import Problem

from src.astar.agent import Agent
from src.util.coordinate import Coordinate
from src.util.grid import Grid
from src.problem.mapf_problem import MAPFProblem

class MatchingProblem(MAPFProblem):

    def __init__(self, original: Problem, compute_heuristic=False):
        agents = [Agent(Coordinate(s.x, s.y), s.color) for s in original.starts]
        goals = original.goals
        grid = Grid(original.width, original.height, original.grid, agents, goals, compute_heuristic)
        super().__init__(agents, grid, goals)
