from typing import List

from src.util.agent import Agent
from src.util.coordinate import Coordinate
from src.util.path import Path


class CAT:
    __author__ = 'ivardb'

    def __init__(self, agents: List[Agent], w: int, h: int, active=True):
        """
        Create a Collision Avoidance Table.
        :param agents:  All possible agents
        :param w:       The width
        :param h:       The height
        :param active:  Can be used to disable the table and always return 0
        """
        self.active = active
        self.agents = agents
        self.cat = [[list() for _ in range(w)] for _ in range(h)]
        self.length = dict()

    def remove_cat(self, path: Path):
        """
        Removes the collisions of the given path.
        :param path:    The path
        """
        if not self.active:
            return
        if path is None:
            return
        for i, coord in enumerate(path.path):
            self.cat[coord[1]][coord[0]].remove((path.identifier, i))

    def add_cat(self, path: Path):
        """
        Adds the path to the table.
        :param path:    The path
        """
        if not self.active:
            return
        for i, coord in enumerate(path.path):
            self.cat[coord[1]][coord[0]].append((path.identifier, i))
        self.length[path.identifier] = len(path)

    def get_cat(self, ignored_paths: List[int], coord: Coordinate, time: int) -> int:
        """
        Gets the number of collisions at the coordinates.
        Ignores the ids in the ignored_paths
        :param ignored_paths:   The ids to ignore
        :param coord:           The location to check for conflicts
        :param time:            The time for which to check
        :return:                The number of found conflicts
        """
        collision = 0
        if self.active:
            for key, value in self.length.items():
                if time > value:
                    if (key, value) in self.cat[coord.y][coord.x]:
                        collision += 1
            for agent in self.agents:
                if agent.identifier in ignored_paths:
                    continue
                if (agent.identifier, time) in self.cat[coord.y][coord.x]:
                    collision += 1
        return collision

    @staticmethod
    def empty():
        """
        Creates an inactive Collision Avoidance Table.
        :return: An inactive CAT
        """
        return CAT([], 0, 0, active=False)
