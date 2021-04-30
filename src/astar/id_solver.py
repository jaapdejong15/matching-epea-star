from typing import List

from mapfmclient import Problem, Solution, MarkedLocation

from src.astar.agent import Agent
from src.astar.astar import PEAStar
from src.problem.mapf_problem import MAPFProblem
from src.util.coordinate import Coordinate
from src.util.grid import Grid
from src.util.path import Path


def check_conflicts(path1: Path, path2: Path) -> bool:
    n = len(path1)
    m = len(path2)
    i = 1
    while i < n and i < m:
        # Vertex conflict
        if path1[i] == path2[i]:
            return True
        # Edge conflict
        if path1[i] == path2[i - 1] and path1[i - 1] == path2[i]:
            return True
        i += 1
    while i < n:
        if path1[i] == path2[-1]:
            return True
        i += 1
    while i < m:
        if path1[-1] == path2[i]:
            return True
        i += 1
    return False


def find_conflict(paths: List[Path]):
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            if check_conflicts(paths[i], paths[j]):
                return paths[i].identifier, paths[j].identifier
    return None


class IDSolver:

    def __init__(self, original: Problem, memory_constant=0):
        self.memory_constant = memory_constant
        self.paths: List[Path] = []
        agents = [Agent(Coordinate(s.x, s.y), s.color, i) for i, s in enumerate(original.starts)]
        original_goals = original.goals
        goals: List[MarkedLocation] = []
        for agent in agents:
            for goal in original.goals:
                if agent.color == goal.color:
                    goals.append(goal)
                    original_goals.remove(goal)
                    break

        self.grid = Grid(original.width, original.height, original.grid, agents, goals)

    def solve(self) -> Solution:
        self.paths = []
        groups = [[agent] for agent in self.grid.agents]

        # Solve for every group
        for group in groups:
            self.grid.agents = group
            problem = MAPFProblem(self.grid)
            solver = PEAStar(problem, memory_constant=self.memory_constant)
            agent_path = solver.solve()
            if agent_path is None:
                raise Exception(f"Agent {group[0].identifier} has no path!")
            else:
                assert len(agent_path) == 1
                self.paths.append(agent_path[0])

        conflict = find_conflict(self.paths)
        while conflict is not None:
            a, b = conflict
            groups = self.merge_groups(groups, a, b)
            conflict = find_conflict(self.paths)
        return Solution.from_paths(self.paths)

    def merge_groups(self, groups: List[List[Agent]], agent_a_id: int, agent_b_id: int) -> List[List[Agent]]:
        group_a = None
        group_b = None
        for i, group in enumerate(groups):
            for agent in group:
                if agent.identifier == agent_a_id:
                    group_a = group
                    break
                if agent.identifier == agent_b_id:
                    group_b = group
                    break
        assert group_a is not None
        assert group_b is not None

        # Combine groups a and b
        group_a.extend(group_b)
        print(f"Conflict for agents groups {agent_a_id} and {agent_b_id}, combining groups: {str([x.identifier for x in group_a])}")
        groups.remove(group_b)

        # Try to solve new group
        self.grid.agents = group_a
        problem = MAPFProblem(self.grid)
        solver = PEAStar(problem, memory_constant=self.memory_constant)
        group_paths = solver.solve()

        for agent, path in zip(group_a, group_paths):
            self.paths[agent.identifier] = path

        if group_paths is None:
            raise Exception("There is an impossible combination of agents")
        return groups