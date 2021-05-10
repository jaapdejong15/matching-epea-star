from typing import List, Tuple


class Path:
    __slots__ = 'path', 'identifier'

    def __init__(self, path: List[Tuple[int, int]], identifier: int):
        self.path = path
        self.identifier: int = identifier

    def __getitem__(self, item):
        return self.path[item]

    def __len__(self):
        return len(self.path)
