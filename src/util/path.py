from __future__ import annotations

from typing import List, Tuple


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


class Path:
    __slots__ = 'path', 'identifier'

    def __init__(self, path: List[Tuple[int, int]], identifier: int):
        self.path = path
        self.identifier: int = identifier

    def __getitem__(self, item):
        return self.path[item]

    def __len__(self):
        return len(self.path)

    def __lt__(self, other: Path):
        return self.identifier < other.identifier

    def conflicts(self, other: Path):
        """
        Checks if two paths have either an edge conflict or a vertex conflict
        :param other:   The other path to check conflicts with
        :return:        True if paths are conflicting, False otherwise
        """
        n = len(self)
        m = len(other)
        i = 1
        while i < n and i < m:
            # Vertex conflict
            if self[i] == other[i]:
                return True
            # Edge conflict
            if self[i] == other[i - 1] and self[i - 1] == other[i]:
                return True
            i += 1
        while i < n:
            if self[i] == other[-1]:
                return True
            i += 1
        while i < m:
            if self[-1] == other[i]:
                return True
            i += 1
        return False

    def get_cost(self):
        """
        Calculates the individual cost of a path
        The cost of staying on the goal at the end of the path is subtracted.
        :return:    Cost
        """
        cost = len(self)
        last = self[-1]
        i = 2
        if i > len(self):
            return cost
        while self[-i] == last:
            cost -= 1
            i += 1
            if i > len(self):
                break
        return cost
