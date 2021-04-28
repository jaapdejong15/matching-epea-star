from mapfmclient import Problem

from src.astar.agent import Agent
from src.util.coordinate import Coordinate
from src.util.grid import Grid
from src.problem.mapf_problem import MAPFProblem

# Takes the first matching it can find
class StandardProblem(MAPFProblem):

    def __init__(self, original: Problem, compute_heuristic=False):
        agents = [Agent(Coordinate(s.x, s.y), s.color) for s in original.starts]
        original_goals = original.goals
        goals = []
        for agent in agents:
            for goal in original.goals:
                if agent.color == goal.color:
                    goals.append(goal)
                    original_goals.remove(goal)
                    break

        grid = Grid(original.width, original.height, original.grid, agents, goals, compute_heuristic)
        super().__init__(agents, grid, goals)
