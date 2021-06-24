from __future__ import annotations

from typing import Iterator


class Group:
    __author__ = "ivardb"

    __slots__ = "agent_ids"

    def __init__(self, agent_ids: Iterator[int]):
        """
        Create a group from the agent_ids
        :param agent_ids: The agent_ids
        """
        self.agent_ids = tuple(agent_ids)

    def combine(self, other) -> Group:
        """
        Combine this group with another one.
        :param other: The other group
        :return: The new group
        """
        i = 0
        j = 0
        n = len(self.agent_ids)
        m = len(other.agent_ids)
        new_ids = []
        while i < n and j < m:
            if self.agent_ids[i] < other.agent_ids[j]:
                new_ids.append(self.agent_ids[i])
                i += 1
            else:
                new_ids.append(other.agent_ids[j])
                j += 1
        while i < n:
            new_ids.append(self.agent_ids[i])
            i += 1
        while j < m:
            new_ids.append(other.agent_ids[j])
            j += 1
        return Group(new_ids)

    def __str__(self):
        return self.agent_ids.__str__()

    def __len__(self):
        return self.agent_ids.__len__()

    def __getitem__(self, item):
        return self.agent_ids.__getitem__(item)

    def __iter__(self):
        return self.agent_ids.__iter__()


class Groups:

    def __init__(self, groups):
        """
        Create a set of groups.
        :param groups: The groups
        """
        self.groups = groups
        self.group_map = dict()
        for group in groups:
            for agent in group.agent_ids:
                self.group_map[agent] = group

    def __iter__(self):
        return self.groups.__iter__()

    def __next__(self):
        return self.groups.__next__()

    def combine_agents(self, a, b) -> Group:
        """
        Combine the groups to which the agents belong.
        :param a: An agent to combine
        :param b: An agent to combine
        :return: The new combined group
        """
        group_a = self.group_map[a]
        group_b = self.group_map[b]
        group = group_a.combine(group_b)
        self.groups.remove(group_a)
        self.groups.remove(group_b)
        self.groups.append(group)
        for agent in group.agent_ids:
            self.group_map[agent] = group
        return group
