from mapfmclient import Problem

from src.util.agent import Agent
from src.solver.epeastar.epeastar import EPEAStar
from src.solver.id_solver import IDSolver
from src.util.coordinate import Coordinate
from src.util.grid import Grid


class HeuristicMatchingSolver:
    def __init__(self, original: Problem, independence_detection=True):
        self.problem = original
        self.independence_detection = independence_detection
        agents = [Agent(Coordinate(s.x, s.y), s.color, i) for i, s in enumerate(original.starts)]
        self.grid = Grid(original.width, original.height, original.grid, agents, original.goals)

    def solve(self):
        if self.independence_detection:
            id_solver = IDSolver(self.grid)
            return id_solver.solve()[0]
        else:
            solver = EPEAStar(self.grid)
            return solver.solve()[0]