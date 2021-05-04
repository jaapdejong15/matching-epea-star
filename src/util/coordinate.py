from __future__ import annotations
from enum import Enum


class Direction(Enum):
    # (dx, dy)
    NORTH = (0, 1)
    EAST = (1, 0)
    SOUTH = (0, -1)
    WEST = (-1, 0)
    WAIT = (0, 0)

class Coordinate:
    __slots__ = ('x', 'y')

    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def move(self, d: Direction):
        dx, dy = d.value
        return Coordinate(self.x + dx, self.y + dy)

    def __eq__(self, other: Coordinate):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return tuple.__hash__((self.x, self.y))

    def __repr__(self):
        return f"({self.x}, {self.y})"
