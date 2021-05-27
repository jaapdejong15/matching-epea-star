from src.util.coordinate import Coordinate


class Agent:
    __slots__ = 'coord', 'color', 'identifier', 'waiting_cost'

    def __init__(self, coord: Coordinate, color, identifier, waiting_cost=0):
        self.coord = coord
        self.color = color
        self.identifier = identifier
        self.waiting_cost = waiting_cost  # Counter for potential costs if agent moves of its goal

    def __eq__(self, other):
        return self.coord == other.coord and self.color == other.color

    def __lt__(self, other):
        return self.identifier < other.identifier

    def __hash__(self):
        return tuple.__hash__((self.coord, self.color))

    def __repr__(self):
        return f"Agent {self.identifier} with color {self.color} at {self.coord.__repr__()} "
