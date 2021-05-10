from copy import copy
from typing import List, Tuple, Optional

from src.astar.agent import Agent
from src.astar.astar import EPEAStar
from src.problem.mapf_problem import MAPFProblem
from src.util.grid import Grid
from src.util.path import Path


def check_conflicts(path1: Path, path2: Path) -> bool:
    """
    Checks if two paths have either an edge conflict or a vertex conflict
    :param path1:   The first path
    :param path2:   The second path
    :return:        True if paths are conflicting, False otherwise
    """
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


def find_conflict(paths: List[Path]) -> Optional[Tuple[int, int]]:
    """

    :param paths:   Paths to check conflicts with
    :return:        Agent identifiers of first conflicting paths
    """
    for i in range(len(paths)):
        for j in range(i + 1, len(paths)):
            if check_conflicts(paths[i], paths[j]):
                return paths[i].identifier, paths[j].identifier
    return None


class IDSolver:
    """
    Solver that uses Independence Detection:
    First solve for all agents individually. If paths are conflicting, merge the agents and solve for the new group
    """

    def __init__(self, original: Grid, max_value):
        """
        Constructs an IDSolver instance
        :param original:        Original problem
        :param max_value:       Maximum allowed value of the solver. Stop the solver if the value is exceeded
        """
        self.paths = []
        self.grid = original
        self.cost = 0
        self.max_value = max_value

    def solve(self) -> Optional[Tuple[list, int]]:
        """
        Solves the original problem
        :return:    Solution with paths for every agent
        """
        agents = copy(self.grid.agents)

        groups = []

        # Solve for every group
        total_cost = 0
        for agent in agents:
            self.grid.agents = [agent]
            problem = MAPFProblem(self.grid)
            solver = EPEAStar(problem, self.max_value)
            agent_path, cost = solver.solve()
            total_cost += cost
            groups.append(([agent], cost))
            if agent_path is None:
                raise Exception(f"Agent {agents[0].identifier} has no path!")
            else:
                assert len(agent_path) == 1
                self.paths.append(agent_path[0])

        if total_cost >= self.max_value:
            return None

        self.cost = total_cost

        conflict = find_conflict(self.paths)
        while conflict is not None:
            a, b = conflict
            groups = self.merge_groups(groups, a, b)
            if groups is None:
                return None
            conflict = find_conflict(self.paths)
        return self.paths, self.cost

    def merge_groups(self, groups: List[Tuple[List[Agent], int]], agent_a_id: int, agent_b_id: int) \
            -> Optional[List[Tuple[List[Agent], int]]]:
        """
        Merge two groups with agents with conflicting paths
        :param groups:      List of all groups
        :param agent_a_id:  Identifier of the first conflicting agent
        :param agent_b_id:  Identifier of the second conflicting agent
        :return:            New list of groups
        """
        group_a = None
        group_b = None
        group_a_id = 0
        for i, group in enumerate(groups):
            for agent in group[0]:
                if agent.identifier == agent_a_id:
                    group_a = group
                    group_a_id = i
                    break
                if agent.identifier == agent_b_id:
                    group_b = group
                    break
        assert group_a is not None
        assert group_b is not None

        self.cost -= group_a[1] + group_b[1]

        # Combine groups a and b
        new_agents = group_a[0] + group_b[0]
        print(
            f"Conflict for agents groups {agent_a_id} and {agent_b_id}, combining groups: {str([x.identifier for x in new_agents])}")

        # Try to solve new group
        self.grid.agents = new_agents
        problem = MAPFProblem(self.grid)
        solver = EPEAStar(problem, self.max_value)

        solution = solver.solve()
        if solution is None:
            return None
        group_paths, cost = solution

        groups[group_a_id] = (new_agents, cost)
        groups.remove(group_b)

        self.cost += cost

        for agent, path in zip(new_agents, group_paths):
            self.paths[agent.identifier] = path
        return groups
