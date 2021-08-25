import os
import random
from collections import deque
from numbers import Number
from random import randint, uniform
from typing import List, Tuple

from mapfmclient import Problem, MarkedLocation

from src.util.coordinate import Coordinate
from src.util.direction import Direction


def map_printer(grid: List[List[int]]):
    print('██' * (len(grid[0]) + 2))
    for y in range(len(grid)):
        print('██' + ''.join(['  ' if pos == 0 else '██' for pos in grid[y]]) + '██')
    print('██' * (len(grid[0]) + 2))


def generate_map(width: int,
                 height: int,
                 num_agents: List[int],
                 open_factor: float = 0.75,
                 max_neighbors: int = 1,
                 min_goal_distance: float = 0.5,
                 max_goal_distance: float = 1

                 ) -> Problem:
    while True:
        grid = generate_maze(width, height, open_factor=open_factor, max_neighbors=max_neighbors)
        count_traversable = 0
        for y in range(height):
            count_traversable += width - sum(grid[y])
        if count_traversable < (open_factor * width * height * 0.25 * max_neighbors) or num_3neighbors(grid) < sum(
                num_agents):
            print("Not enough traversable cells or not solvable, running again!")
        else:
            starts, goals = generate_agent_positions(grid, width, height, num_agents, min_goal_distance,
                                                     max_goal_distance)
            start_locations: List[MarkedLocation] = []
            goal_locations: List[MarkedLocation] = []

            i = 0
            for color, team_size in enumerate(num_agents):
                for _ in range(team_size):
                    start_locations.append(MarkedLocation(color, starts[i].x, starts[i].y))
                    goal_locations.append(MarkedLocation(color, goals[i].x, goals[i].y))
                    i += 1
            random.shuffle(goal_locations)
            return Problem(width=width, height=height, grid=grid, starts=start_locations, goals=goal_locations)


def generate_agent_positions(grid: List[List[int]],
                             width: int,
                             height: int,
                             num_agents: List[int],
                             min_distance: float,
                             max_distance: float) -> Tuple[List[Coordinate], List[Coordinate]]:
    agent_positions = []
    goal_positions = []

    # Find a random position for each agent
    for x in range(sum(num_agents)):
        start_x = randint(0, width - 1)
        start_y = randint(0, height - 1)
        while grid[start_y][start_x] != 0 or Coordinate(start_x, start_y) in agent_positions:
            start_x = randint(0, width - 1)
            start_y = randint(0, height - 1)

        agent_positions.append(Coordinate(start_x, start_y))

    for agent in agent_positions:
        queue = deque()
        queue.append((agent, 0))
        distances, m = compute_heuristic(queue, grid)
        possible_locations = []
        while len(possible_locations) == 0:
            distance = random.randint(int(m * min_distance), int(m * max_distance))
            for y, row in enumerate(distances):
                for x, value in enumerate(row):
                    if value == distance \
                            and Coordinate(x, y) not in goal_positions \
                            and Coordinate(x, y) not in agent_positions:
                        possible_locations.append(Coordinate(x, y))
        goal_positions.append(random.choice(possible_locations))
    return agent_positions, goal_positions


def num_3neighbors(grid: List[List[int]]) -> int:
    height = len(grid)
    width = len(grid[0])
    res = 0
    for y in range(height):
        for x in range(width):
            count = 0
            for neighbor in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
                ndx, ndy = neighbor.value
                neighbor_x = x + ndx
                neighbor_y = y + ndy
                if 0 <= neighbor_x < width and 0 <= neighbor_y < height and grid[neighbor_y][neighbor_x] == 0:
                    count += 1
            if count == 3:
                res += 1
    return res


def compute_heuristic(queue: deque, grid: List[List[int]]) -> Tuple[List[List[Number]], int]:
    visited = set()
    heuristic = [[float('inf') for _ in range(len(grid[0]))] for _ in range(len(grid))]
    m = 0
    while len(queue) > 0:
        coord, dist = queue.popleft()
        m = max(dist, m)
        if coord in visited:
            continue
        visited.add(coord)

        # Already has a better distance
        if heuristic[coord.y][coord.x] != float("inf"):
            continue
        heuristic[coord.y][coord.x] = dist

        for neighbor in get_neighbors(grid, coord):
            if neighbor not in visited:
                queue.append((neighbor, dist + 1))
    return heuristic, m


def get_neighbors(grid: List[List[int]], coords: Coordinate):
    res = list()
    for d in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
        new_coord = coords.move(d)
        if 0 <= new_coord.y < len(grid) and 0 <= new_coord.x < len(grid[0]) and grid[new_coord.y][new_coord.x] == 0:
            res.append(new_coord)
    return res


def generate_maze(width: int, height: int, open_factor: float, max_neighbors: int) -> List[List[int]]:
    grid: List[List[int]] = []
    for x in range(height):
        grid.append([1] * width)

    start_x = randint(0, width - 1)
    start_y = randint(0, height - 1)

    grid[start_y][start_x] = 0

    frontier = [Coordinate(start_x, start_y)]

    num_open = 1
    while frontier:
        pos = frontier.pop()
        for d in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            if uniform(0, 1) < open_factor:
                dx, dy = d.value
                new_x = pos.x + dx
                new_y = pos.y + dy

                # Check if not out of bounds and if not already opened
                if 0 <= new_x < width and 0 <= new_y < height and grid[new_y][new_x] != 0:
                    # Check number of EXS-open.txt neighbors
                    count = 0
                    for neighbor in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
                        ndx, ndy = neighbor.value
                        neighbor_x = new_x + ndx
                        neighbor_y = new_y + ndy
                        if 0 <= neighbor_x < width and 0 <= neighbor_y < height and grid[neighbor_y][neighbor_x] == 0:
                            count += 1
                    if count <= max_neighbors:
                        grid[new_y][new_x] = 0
                        num_open += 1

                        frontier.append(Coordinate(new_x, new_y))
    print(f'Obstacle density: {num_open / (width * height)}')
    return grid


def store_map(name: str, folder: str, problem: Problem):
    if not os.path.exists(f'../../maps/{folder}'):
        os.mkdir(f'../../maps/{folder}')
    with open(f'../../maps/{folder}/{name}.map', 'w') as f:
        f.write(f'width {problem.width}\n')
        f.write(f'height {problem.height}\n')

        # Grid
        for row in problem.grid:
            f.write(''.join(map(lambda x: '.' if x == 0 else '@', row)) + "\n")

        # Number of agents
        f.write(f'{len(problem.starts)}\n')
        # Starts
        for start in problem.starts:
            f.write(f'{start.x} {start.y} {start.color}\n')
        f.write('\n')

        for goal in problem.goals:
            f.write(f'{goal.x} {goal.y} {goal.color}\n')


def generate_batch(name: str,
                   folder: str,
                   amount: int,
                   width: int,
                   height: int,
                   num_agents: List[int],
                   open_factor: float = 1,
                   max_neighbors: int = 4,
                   min_goal_distance: float = 0,
                   max_goal_distance: float = 1
                   ) -> None:
    for i in range(amount):
        problem = generate_map(width, height, num_agents,
                               open_factor=open_factor,
                               max_neighbors=max_neighbors,
                               min_goal_distance=min_goal_distance,
                               max_goal_distance=max_goal_distance)
        filename = f'{name}-{i}'
        store_map(filename, folder, problem)


if __name__ == '__main__':
    generate_batch('test', 'test', amount=4, width=4, height=4, num_agents=[4])
    # for i in range(1):
    #     generate_batch(f'OBSTACLES-20x20-A{i}_T1', f'OBSTACLES-20x20-A{i}_T1',
    #                    amount=50,
    #                    width=20,
    #                    height=20,
    #                    num_agents=[i]
    #                    )
