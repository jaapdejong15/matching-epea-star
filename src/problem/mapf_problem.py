import time
from typing import List, Tuple, NewType, Dict

from src.astar.agent import Agent
from src.astar.node import Node
from src.astar.operator_finder import OperatorFinder
from src.astar.state import State
from src.util.coordinate import Direction
from src.util.grid import Grid

OSFRow = NewType('OSFRow', Tuple[Direction, int])
OSFTable = NewType('OSFTable', List[OSFRow])

class MAPFProblem:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.osf: Dict[int, List[List[OSFTable]]] = dict()
        self.t = 0

        for color in grid.colors.keys():
            self.calculate_single_color_osf(color)

    def on_goal(self, agent: Agent) -> bool:
        for goal in self.grid.goals:
            if goal.x == agent.coord.x and goal.y == agent.coord.y and goal.color == agent.color:
                return True
        return False

    def is_solved(self, state) -> bool:
        solved = all(self.on_goal(agent) for agent in state.agents)
        if solved:
            print(f"Operator selection took {self.t*1000} ms")
        return solved

    def expand(self, node: Node, v) -> Tuple[List[Node], int]:
        children, next_value = self.get_children(node, v)

        # Check constraints
        selected_children = []
        for child in children:
            coords = set()
            edge_conflict = False
            vertex_conflict = False
            for i, agent in enumerate(child.state.agents):
                # Check vertex conflict
                if agent.coord in coords:
                    vertex_conflict = True
                    break
                coords.add(agent.coord)

                # Check edge conflicts
                for j in range(i + 1, len(node.state.agents)):
                    if child.state.agents[i].coord == node.state.agents[j].coord and child.state.agents[j].coord == node.state.agents[i].coord:
                        edge_conflict = True
                        break
                if edge_conflict:
                    break
            if not vertex_conflict and not edge_conflict:
                selected_children.append(child)
        return selected_children, next_value

    def heuristic(self, state):
        total = 0
        for agent in state.agents:
            total += self.grid.heuristic[agent.color][agent.coord.y][agent.coord.x]
        return total

    """
    Applies an operator to a parent node to create a child node
    :param parent: The parent node
    :param operator: Tuple of Directions of length #agents
    :returns: The child node
    """
    def get_child(self, parent: Node, operator: Tuple[Direction, ...]) -> Node:
        t1 = time.perf_counter()
        assert len(operator) == len(parent.state.agents)

        agents = []
        costs = parent.cost
        for i, agent in enumerate(parent.state.agents):
            waiting_costs = 0
            if self.on_goal(agent):
                if operator[i] is not Direction.WAIT:
                    costs += agent.waiting_cost + 1
                else:
                    waiting_costs = agent.waiting_cost + 1
            else:
                costs += 1
            agents.append(Agent(agent.coord.move(operator[i]), agent.color, agent.identifier, waiting_cost=waiting_costs))

        self.t += time.perf_counter() - t1
        child_state = State(agents)
        return Node(child_state, costs, self.heuristic(child_state), parent=parent)

    def get_children(self, parent: Node, v: int) -> Tuple[List[Node], int]:
        operator_finder = OperatorFinder(v, [self.osf[agent.color][agent.coord.y][agent.coord.x] for agent in parent.state.agents])

        operator_finder.find_operators(0, [], 0)

        children = [self.get_child(parent, operator) for operator in operator_finder.operators]

        return children, operator_finder.next_target_value

    def calculate_single_color_osf(self, color: int) -> None:
        heuristic = self.grid.heuristic[color]
        single_color_osf: List[List[OSFTable]] = []
        for y in range(self.grid.height):
            osf_grid_row = []
            for x in range(self.grid.width):
                h = heuristic[y][x]
                if h != float('inf'):
                    osf_table = self.generate_osf_table(x, y, h, color)
                    osf_grid_row.append(osf_table)
                else:
                    osf_grid_row.append(OSFTable([]))
            assert len(osf_grid_row) == self.grid.width
            single_color_osf.append(osf_grid_row)

        assert len(single_color_osf) == self.grid.height
        self.osf[color] = single_color_osf

    def generate_osf_table(self, x:int, y:int, heuristic: int, color: int) -> OSFTable:
        osf_table: List[OSFRow] = []
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            dx, dy = direction.value
            new_x: int = x+dx
            new_y: int = y+dy
            if self.grid.traversable_coords(new_x, new_y):
                delta_f: int = 1 + self.grid.heuristic[color][new_y][new_x] - heuristic
                osf_table.append(OSFRow((direction, delta_f)))

        osf_table.append(OSFRow((Direction.WAIT, 1)))
        osf_table.sort(key=(lambda row : row[1]))
        return OSFTable(osf_table)






