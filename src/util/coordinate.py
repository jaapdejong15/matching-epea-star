from enum import Enum

class Direction (Enum):
    # (dx, dy)
    NORTH = (0, 1)
    EAST = (1,0)
    SOUTH = (0, -1)
    WEST = (-1, 0)
    WAIT = (0,0)

class Coordinate:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, d : Direction):
        dx, dy = d.value
        return Coordinate(self.x + dx, self.y + dy)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return tuple.__hash__((self.x, self.y))
