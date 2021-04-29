from src.util.coordinate import Coordinate


class Agent:
    def __init__(self, coord: Coordinate, color, identifier, waiting_cost=0):
        self.coord = coord
        self.color = color
        self.identifier = identifier
        self.waiting_cost = waiting_cost  # Counter for potential costs if agent moves of its goal

    def __eq__(self, other):
        return self.coord == other.coord and self.color == other.color

    def __hash__(self):
        return tuple.__hash__((self.coord, self.color))
