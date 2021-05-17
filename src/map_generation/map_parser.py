import os.path
from typing import List

from mapfmclient import MarkedLocation, Problem


class MapParser:

    def __init__(self, root_folder: str):
        self.root_folder = root_folder

    def parse_map(self, name: str) -> Problem:
        with open(os.path.join(self.root_folder, name)) as file:
            # Read map width
            width_line = file.readline()
            width = int(width_line.split(' ')[1])

            # Read map height
            height_line = file.readline()
            height = int(height_line.split(' ')[1])

            # Read map
            grid = []
            for _ in range(height):
                grid.append([1 if char == '@' else 0 for char in file.readline()])

            # Read number of agents
            num_agents = int(file.readline())

            starts: List[MarkedLocation] = []

            # Read starting positions
            for _ in range(num_agents):
                line = file.readline().split(' ')
                starts.append(MarkedLocation(int(line[2]), int(line[0]), int(line[1])))

            # Empty line
            file.readline()

            # Read goal positions
            goals: List[MarkedLocation] = []
            for _ in range(num_agents):
                line = file.readline().split(' ')
                goals.append(MarkedLocation(int(line[2]), int(line[0]), int(line[1])))

            return Problem(grid, width, height, starts, goals)

    def parse_batch(self, folder: str) -> List[Problem]:
        paths = os.listdir(os.path.join(self.root_folder, folder))
        problems = []
        for file in paths:
            problems.append(self.parse_map(f'{folder}/{file}'))
        return problems
