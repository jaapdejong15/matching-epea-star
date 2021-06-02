from typing import List, Optional, Iterator, Tuple

from src.solver.epeastar.heuristic import Heuristic
from src.util.agent import Agent
from src.util.path import Path
from src.util.cat import CAT


class PathSet:

    __author__ = 'ivardb'

    def __init__(self, agents: List[Agent], heuristic: Heuristic):
        """
        Create a PathSet to keep track of paths and calculate costs etc.
        :param agents:      The agents that are stored here.
        :param heuristic:   The heuristic function
        """
        self.agents = agents
        self.heuristic = heuristic
        self.mapping = dict((agent.identifier, i) for i, agent in enumerate(agents))
        self.paths: List[Optional[Path]] = [None for _ in range(len(agents))]
        self.costs: List[Optional[int]] = [None for _ in range(len(agents))]

        # Create CAT with the same dimensions as the heuristic function
        width = len(heuristic.heuristic[agents[0].color][0])
        height = len(heuristic.heuristic[agents[0].color])
        self.cat = CAT(agents, width, height, active=True)

    def update(self, new_paths: Iterator[Path]):
        """
        Updates the paths in the internal storage.
        Should always be used as the internal index is not the same as the id.
        :param new_paths: The new_paths
        """
        for path in new_paths:
            i = self.mapping[path.identifier]
            self.cat.remove_cat(self.paths[i])
            self.paths[i] = path
            self.cat.add_cat(path)
            self.costs[i] = path.get_cost()

    def get_remaining_cost(self, indexes: List[int], max_cost) -> int:
        """
        Calculates the remaining cost that can be spent on a set of paths without going over the max cost
        :param indexes:         The ids that still need to be solved
        :param max_cost:        The maximum cost that can't be overridden
        """
        return max_cost - sum(self.get_cost(agent.identifier) for agent in self.agents if agent.identifier not in indexes)

    def get_cost(self, agent_id):
        """
        Calculate the cost for the id.
        :param agent_id:    The id
        :return:            The cost
        """
        return self.costs[self.mapping[agent_id]] if self.costs[self.mapping[agent_id]] is not None else self.get_heuristic(agent_id)

    def get_heuristic(self, agent_id):
        """
        Get the heuristic for the id.
        This is the minimum cost a path for this agent will take based on the heuristic.
        :param agent_id:        The agent id
        :return:                The minimum heuristic cost
        """
        agent = next(agent for agent in self.agents if agent.identifier == agent_id)
        return self.heuristic.heuristic[agent.color][agent.coord.y][agent.coord.x]

    def find_conflict(self) -> Optional[Tuple[int, int]]:
        """
        Find conflicting paths
        :return:    ids of conflicting paths
        """
        for i in range(len(self.agents)):
            id_i = self.agents[i].identifier
            path_index_i = self.mapping[id_i]
            for j in range(i + 1, len(self.agents)):
                id_j = self.agents[j].identifier
                path_index_j = self.mapping[id_j]
                if self.paths[path_index_i].conflicts(self.paths[path_index_j]):
                    return id_i, id_j
        return None

    def __getitem__(self, agent_id):
        """
        Should always be used to get a path as internal index differs from id.
        :param agent_id:    The id to get the path for
        :return:            The path belonging to this id
        """
        return self.paths[self.mapping[agent_id]]