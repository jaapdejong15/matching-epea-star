from mapfmclient import Problem

from src.solver.agent import Agent
from src.problem.mapf_problem import MAPFProblem
from src.util.coordinate import Coordinate
from src.util.grid import Grid


# Takes the first matching it can find
class StandardProblem(MAPFProblem):

    def __init__(self, original: Problem):
        agents = [Agent(Coordinate(s.x, s.y), s.color, i) for i, s in enumerate(original.starts)]
        original_goals = original.goals
        goals = []
        for agent in agents:
            for goal in original.goals:
                if agent.color == goal.color:
                    goals.append(goal)
                    original_goals.remove(goal)
                    break

        grid = Grid(original.width, original.height, original.grid, agents, goals)
        super().__init__(grid)
