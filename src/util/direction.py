from enum import Enum


class Direction(Enum):
    # (dx, dy)
    NORTH = (0, 1)
    EAST = (1, 0)
    SOUTH = (0, -1)
    WEST = (-1, 0)
    WAIT = (0, 0)
