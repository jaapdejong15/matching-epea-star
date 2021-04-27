import itertools

from mapfmclient import Problem, Solution, MarkedLocation
from typing import List, Optional, Tuple
from src.astar.agent import Agent
from src.util.coordinate import Coordinate, Direction
from heapq import heappush, heappop

class State:
    def __init__(self, agents: List[Agent]):
        self.agents = tuple(agents)

    def __eq__(self, other):
        return self.agents == other.agents

    def __hash__(self):
        return hash(self.agents)

class Node:

    def __init__(self, state: State, cost: int, heuristic: int, parent = None):
        self.state = state
        self.cost = cost
        self.heuristic = heuristic
        self.parent = parent

    def __eq__(self, other):
        return self.cost + self.heuristic == other.cost + other.heuristic

    def __lt__(self, other):
        return self.cost + self.heuristic < other.cost + other.heuristic

class Grid:
    def __init__(self, width: int, height: int, grid: List[List[int]]):
        self.width = width
        self.height = height
        self.grid = grid

    def __is_wall(self, pos: Coordinate) -> bool:
        return self.grid[pos.y][pos.x] == 1

    def traversable(self, pos: Coordinate) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height and not self.__is_wall(pos)

    def get_neighbors(self, pos: Coordinate) -> List[Coordinate]:
        neighbors = []
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            neighbor = pos.move(direction)
            if self.traversable(neighbor):
                neighbors.append(neighbor)
        return neighbors

class MatchingProblem:

    def __init__(self, original: Problem):
        self.agents = [Agent(Coordinate(s.x, s.y), s.color) for s in original.starts]
        self.grid = Grid(original.width, original.height, original.grid)
        self.goals = original.goals

    def on_goal(self, agent: Agent) -> bool:
        for goal in self.goals:
            if goal.x == agent.coord.x and goal.y == agent.coord.y and goal.color == agent.color:
                return True
        return False

    def heuristic(self, state: State) -> int:
        # Sum of distance to closest goal of same color for each agent
        heuristic = 0
        for agent in state.agents:
            goal_distance = float('inf')
            for goal in self.goals:
                if goal.color == agent.color:
                    goal_distance = min(goal_distance, abs(agent.coord.x - goal.x) + abs(agent.coord.y - goal.y))
            heuristic += goal_distance
        return heuristic

    def is_solved(self, state) -> bool:
        return all(self.on_goal(agent) for agent in state.agents)

    # TODO: Expand states instead of nodes
    def expand(self, state: State) -> List[Tuple[State, int]]:
        agents_moves = []
        for agent in state.agents:
            agent_moves = [(Agent(neighbor, agent.color), 1 + agent.waiting_cost) for neighbor in self.grid.get_neighbors(agent.coord)]
            if self.on_goal(agent):
                agent_moves.append((Agent(agent.coord, agent.color, agent.waiting_cost + 1), 0))
            else:
                agent_moves.append((Agent(agent.coord, agent.color), 1 + agent.waiting_cost))
            agents_moves.append(agent_moves)

        possible_moves = itertools.product(*agents_moves)

        # Check constraints
        states = []
        for move in possible_moves:
            coords = set()
            edge_conflict = False
            vertex_conflict = False
            for i, (agent, cost) in enumerate(move):
                # Check vertex conflict
                if agent.coord in coords:
                    vertex_conflict = True
                    break
                coords.add(agent.coord)

                # Check edge conflicts
                for j in range(i + 1, len(state.agents)):
                    if move[i][0].coord == state.agents[j].coord and move[j][0].coord == state.agents[i].coord:
                        edge_conflict = True
                        break
                if edge_conflict:
                    break

            if (not vertex_conflict) and (not edge_conflict):
                agents = []
                added_cost = 0
                for agent, agent_cost in move:
                    agents.append(agent)
                    added_cost += agent_cost
                move = State(agents)
                states.append((move, added_cost))
        return states


def get_path(node: Node) -> List[Node]:
    path = []
    while node is not None:
        path.append(node)
        node = node.parent
    path.reverse()
    return path

def convert_path(nodes: List[Node]):
    paths = []
    for i, agent in enumerate(nodes[0].state.agents):
        path = []
        for node in nodes:
            path.append((node.state.agents[i].coord.x, node.state.agents[i].coord.y))
        paths.append(path)
    return Solution.from_paths(paths)

class AStar:

    def __init__(self, problem: Problem):
        self.problem = MatchingProblem(problem)
        initial_state = State(self.problem.agents)
        self.initial_node = Node(initial_state, len(self.problem.agents), self.problem.heuristic(initial_state))

    def solve(self) -> Optional[Solution]:
        frontier = []
        seen = set() # Avoid doing the same nodes over and over again
        heappush(frontier, self.initial_node)

        while frontier:
            node = heappop(frontier)
            if node.state in seen:
                continue
            seen.add(node.state)
            if self.problem.is_solved(node.state):
                return convert_path(get_path(node))

            children = self.problem.expand(node.state)
            for (state, added_cost) in children:
                if state not in seen:
                    child_node = Node(state, node.cost + added_cost, self.problem.heuristic(state), parent=node)
                    heappush(frontier, child_node)
        return None
