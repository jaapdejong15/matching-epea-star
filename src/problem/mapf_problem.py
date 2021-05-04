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
        """
        Creates an instance of MAPFProblem.
        :param grid:    2d grid with starting locations and goals
        """
        self.grid = grid
        self.osf: Dict[int, List[List[OSFTable]]] = dict()
        self.t = 0

        for color in grid.colors.keys():
            self.calculate_single_color_osf(color)

    def on_goal(self, agent: Agent) -> bool:
        """
        Checks if an agent is on a goal of the correct color.
        :param agent:   Agent to check if it is on its goal
        :returns:        True if the agent is on a goal, False otherwise
        """
        for goal in self.grid.goals:
            if goal.x == agent.coord.x and goal.y == agent.coord.y and goal.color == agent.color:
                return True
        return False

    def is_solved(self, state: State) -> bool:
        """
        Checks if the given state is a valid solution to the problem.
        :param state:   State for which it should be checked
        :returns:       True if state is a solution, False otherwise
        """
        solved = all(self.on_goal(agent) for agent in state.agents)
        if solved:
            print(f"Operator selection took {self.t * 1000} ms")
        return solved

    def expand(self, node: Node, v: int) -> Tuple[List[Node], int]:
        """
        Expands an A* search tree node.
        :param node:    parent node
        :param v:       Δf value for which to expand TODO: Get delta_f directly from parent node
        :returns:       List of child nodes and the next Δf value for the parent node
        """
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
                    if child.state.agents[i].coord == node.state.agents[j].coord and child.state.agents[j].coord == \
                            node.state.agents[i].coord:
                        edge_conflict = True
                        break
                if edge_conflict:
                    break
            if not vertex_conflict and not edge_conflict:
                selected_children.append(child)
        return selected_children, next_value

    def heuristic(self, state: State) -> int:
        """
        Calculates the heuristic for the given state state
        :param state:   state to calculate the heuristic for
        :returns:       heuristic value for the state
        """
        total = 0
        for agent in state.agents:
            total += self.grid.heuristic[agent.color][agent.coord.y][agent.coord.x]
        return total

    def get_child(self, parent: Node, operator: Tuple[Direction, ...]) -> Node:
        """
        Applies an operator to a parent node to create a child node
        :param parent:      The parent node
        :param operator:    Tuple of Directions of length #agents
        :returns:           The child node
        """
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
            agents.append(
                Agent(agent.coord.move(operator[i]), agent.color, agent.identifier, waiting_cost=waiting_costs))

        self.t += time.perf_counter() - t1
        child_state = State(agents)
        return Node(child_state, costs, self.heuristic(child_state), parent=parent)

    def get_children(self, parent: Node, v: int) -> Tuple[List[Node], int]:
        """
        Uses the operator selection function (OSF) to get all relevant children from the parent node.
        :param parent:  Parent node
        :param v:       The Δf value.
        :returns:       List of child nodes and next Δf value for the parent node
        """
        operator_finder = OperatorFinder(v, [self.osf[agent.color][agent.coord.y][agent.coord.x] for agent in
                                             parent.state.agents])

        operator_finder.find_operators(0, [], 0)

        children = [self.get_child(parent, operator) for operator in operator_finder.operators]

        return children, operator_finder.next_target_value

    def calculate_single_color_osf(self, color: int) -> None:
        """
        Precomputes the operator selection function (OSF) for individual agents.
        Results are stored in self.osf
        :param color: Color for which OSF components have to be computed
        """
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

    def generate_osf_table(self, x: int, y: int, heuristic: int, color: int) -> OSFTable:
        """
        Generates an operator selection function (OSF) table for a single color and vertex in the grid
        :param x:               x-coordinate of the vertex
        :param y:               y-coordinate of the vertex
        :param heuristic:       heuristic for the color at the given (x,y).
        :param color:           color for the OSF
        :returns:               OSF table with Δf values for each move, sorted on Δf
        """
        osf_table: List[OSFRow] = []
        for direction in [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]:
            dx, dy = direction.value
            new_x: int = x + dx
            new_y: int = y + dy
            if self.grid.traversable_coords(new_x, new_y):
                delta_f: int = 1 + self.grid.heuristic[color][new_y][new_x] - heuristic
                osf_table.append(OSFRow((direction, delta_f)))

        osf_table.append(OSFRow((Direction.WAIT, 1)))
        osf_table.sort(key=(lambda row: row[1]))
        return OSFTable(osf_table)
