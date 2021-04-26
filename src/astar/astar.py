import itertools

from mapfmclient import Problem, Solution, MarkedLocation
from typing import List, Optional
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

    def __is_wall(self, pos: Coordinate):
        return self.grid[pos.y][pos.x]

    def traversable(self, pos: Coordinate):
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height and not self.__is_wall(pos)

    def get_neighbors(self, pos: Coordinate):
        neighbors = []
        for d in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            neighbor = pos.move(d)
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
        coords = set()
        for agent in state.agents:
            if agent.coord in coords:
                return False # Vertex conflict
            for ml in self.goals:
                if ml.x == agent.coord.x and ml.y == agent.coord.y and ml.color == agent.color:
                    break
            else:
                return False
        return True


    def expand(self, node: Node) -> List[Node]:
        agents_moves = []
        for agent in node.state.agents:
            # TODO: Add waiting cost?
            possible_moves = [(Agent(neighbor, agent.color), 1) for neighbor in self.grid.get_neighbors(agent.coord)]
            if self.on_goal(agent):
                possible_moves.append((Agent(agent.coord, agent.color, agent.waiting_cost + 1), 0))
            else:
                possible_moves.append((Agent(agent.coord, agent.color, 0), 1))
            agents_moves.append(possible_moves)

        possible_states = itertools.product(*agents_moves)

        # Check constraints
        nodes = []
        for state in possible_states:
            coords = set()
            edge_conflict = False
            vertex_conflict = False
            for i, (agent, cost) in enumerate(state):
                # Check vertex conflict
                if agent.coord in coords:
                    vertex_conflict = True
                    break
                coords.add(agent.coord)

                # Check edge conflicts
                for j, old_agent in enumerate(node.state.agents):
                    if i != j and agent.coord == old_agent.coord and state[j][0] == node.state.agents[i]:
                        edge_conflict = True
                        break
                if edge_conflict:
                    break

            if (not vertex_conflict) and (not edge_conflict):
                agents = []
                cost = node.cost
                for agent, added_cost in state:
                    agents.append(agent)
                    cost += added_cost
                state = State(agents)
                nodes.append(Node(state, cost, self.heuristic(state), parent=node))
        return nodes


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
        self.initial_node = Node(initial_state, 0, self.problem.heuristic(initial_state))

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

            children = self.problem.expand(node)
            for child in children:
                if child.state not in seen:
                    heappush(frontier, child)
        return None
