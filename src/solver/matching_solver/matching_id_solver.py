from typing import List, Optional, Iterator, Tuple

from mapfmclient import Problem, MarkedLocation

from src.solver.epeastar.heuristic import Heuristic
from src.solver.epeastar.pdb_generator import PDB
from src.solver.matching_solver.exhaustive_matching_solver import ExhaustiveMatchingSolver
from src.util.agent import Agent
from src.util.cat import CAT
from src.util.grid import Grid
from src.util.group import Group, Groups
from src.util.path import Path
from src.util.statistic_tracker import StatisticTracker


class MatchingIDSolver:

    def __init__(self,
                 problem: Problem,
                 num_goal_assignments: int = 10000000,
                 sorting: bool = False,
                 independence_detection: bool = True,
                 matching_id: bool = True):
        """
        Solves MAPFM problems
        :param problem:                 The MAPFM problem to solve
        :param num_goal_assignments:    The amount of goal assignments that should be stored at once
        :param sorting:                 Indicates whether goal assignments should be evaluated in order of
                                        initial heuristic
        :param independence_detection:  Indicates whether EPEA* should use independence detection
        :param matching_id:             Indicates whether exhaustive matching should use independence detection
        """
        self.num_stored_problems = num_goal_assignments
        self.sorting = sorting
        self.independence_detection = independence_detection
        self.matching_id = matching_id
        self.grid = Grid(problem.width, problem.height, problem.grid)
        self.starts = problem.starts
        self.goals = problem.goals
        self.heuristic = Heuristic(self.grid, [MarkedLocation(i, ml.x, ml.y) for i, ml in enumerate(problem.goals)])
        self.osf = PDB(self.heuristic, self.grid)

    def solve(self) -> Optional[Tuple[List[Path], StatisticTracker]]:
        """
        Solves the problem with which the solver was instantiated
        :return:    List of paths in the solution and statistic tracker
        """
        if self.matching_id:
            return self.id_solve()
        else:
            return self.standard_solve()

    def standard_solve(self) -> Optional[Tuple[List[Path], StatisticTracker]]:
        """
        Solves the problem without using matching independence detection.
        :return:    List of paths in the solution and statistic tracker
        """
        stat_tracker = StatisticTracker()
        solver = self.create_solver(Group(list(range(len(self.starts)))), stat_tracker)
        return solver.solve(), stat_tracker

    def id_solve(self) -> Optional[Tuple[List[Path], StatisticTracker]]:
        """
        Solves the problem using matching independence detection.
        :return:    List of paths in the solution and statistic tracker
        """
        stat_tracker = StatisticTracker()
        max_team = max(map(lambda x: x.color, self.starts))
        teams = [list() for _ in range(max_team + 1)]
        for i, start in enumerate(self.starts):
            teams[start.color].append(i)
        teams = list(map(Group, filter(lambda x: len(x) > 0, teams)))
        group_path_set = GroupPathSet(self.grid.width, self.grid.height, list(range(len(self.starts))), teams,
                                      enable_cat=True)

        for group in group_path_set.groups:
            solver = self.create_solver(group, stat_tracker)
            paths = solver.solve()
            if paths is None:
                return None
            group_path_set.update(paths)
        conflict = group_path_set.find_conflict()
        while conflict is not None:
            a, b = conflict
            new_group = group_path_set.groups.combine_agents(a, b)
            solver = self.create_solver(new_group, stat_tracker)
            paths = solver.solve()
            if paths is None:
                return None
            group_path_set.update(paths)
            conflict = group_path_set.find_conflict()
        return group_path_set.paths, stat_tracker

    def create_solver(self, group, stat_tracker) -> ExhaustiveMatchingSolver:
        """
        Creates an exhaustive matching solver for each group.
        :param group:           List of agents for which the solver needs to be made
        :param stat_tracker:    Statistic tracker
        :return:                Exhaustive matching solver
        """
        return ExhaustiveMatchingSolver(
            self.grid,
            self.heuristic,
            self.osf,
            group,
            self.starts,
            self.goals,
            stat_tracker=stat_tracker,
            num_stored_problems=self.num_stored_problems,
            sorting=self.sorting,
            independence_detection=self.independence_detection
        )


class GroupPathSet:

    def __init__(self, w: int, h: int, agents: List[Agent], teams: List[Group], enable_cat: bool):
        """
        Create a path set used to track the paths for MatchingID.
        :param w:           The width of the grid
        :param h:           The height of the grid
        :param teams:       The teams
        :param enable_cat:  If CAT should be used
        """
        self.groups = Groups(teams)
        self.remove_one_groups()
        self.paths: List[Optional[Path]] = [None for _ in range(len(agents))]
        self.cat = CAT(agents, w, h) if enable_cat else CAT.empty()

    def update(self, new_paths: Iterator[Path]):
        """
        Update the stored paths with the new paths.
        :param new_paths:   The new paths
        """
        for path in new_paths:
            i = path.identifier
            self.cat.remove_cat(self.paths[i])
            self.paths[i] = path
            self.cat.add_cat(path)

    def find_conflict(self) -> Optional[Tuple[int, int]]:
        """
        Finds a conflict among the stored paths.
        :return:    The first found conflict.
        """
        for i in range(len(self.paths)):
            for j in range(i + 1, len(self.paths)):
                if self.paths[i].conflicts(self.paths[j]):
                    return i, j
        return None

    def remove_one_groups(self):
        """
        Method to merge groups of size 1 as solving those separately never leads to a performance increase.
        """
        one_group_agents = list()
        for group in self.groups:
            if len(group) == 1:
                one_group_agents.append(group[0])
        for i in range(1, len(one_group_agents)):
            self.groups.combine_agents(one_group_agents[0], one_group_agents[i])
