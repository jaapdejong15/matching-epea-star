from typing import List, Tuple


class Path:
    def __init__(self, path: List[Tuple[int, int]], cost: int, identifier: int):
        self.path = path
        self.cost = cost
        self.identifier = identifier

    def __getitem__(self, item):
        return self.path[item]

    def __len__(self):
        return len(self.path)
