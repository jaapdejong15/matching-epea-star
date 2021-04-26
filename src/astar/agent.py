from src.util.coordinate import Direction, Coordinate

class Agent:
    def __init__(self, coord : Coordinate, color, waiting_cost=0):
        self.coord = coord
        self.color = color
        self.waiting_cost = waiting_cost # Counter for potential costs if agent moves of its goal

    def move(self, direction : Direction):
        return self.coord.move(direction)

    def __eq__(self, other):
        return self.coord == other.coord and self.color == other.color

    def __hash__(self):
        return tuple.__hash__((self.coord, self.color))