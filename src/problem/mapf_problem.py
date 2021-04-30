import itertools
from typing import List, Tuple, NewType, Dict

from src.astar.agent import Agent
from src.astar.node import Node
from src.astar.state import State
from src.util.coordinate import Direction
from src.util.grid import Grid

OSFRow = NewType('OSFRow', Tuple[Direction, int])
OSFTable = NewType('OSFTable', List[OSFRow])

class MAPFProblem:
    def __init__(self, grid: Grid):
        self.grid = grid
        self.osf: Dict[int, List[List[OSFTable]]] = dict()
        for color in grid.colors.keys():
            self.calculate_single_color_osf(color)

    def on_goal(self, agent: Agent) -> bool:
        for goal in self.grid.goals:
            if goal.x == agent.coord.x and goal.y == agent.coord.y and goal.color == agent.color:
                return True
        return False

    def is_solved(self, state) -> bool:
        return all(self.on_goal(agent) for agent in state.agents)

    def expand(self, node: Node, v) -> Tuple[List[Node], int]:
        agents_moves = []
        # for agent in state.agents:
        #     agent_moves = [(Agent(neighbor, agent.color, i), 1 + agent.waiting_cost) for i, neighbor in
        #                    enumerate(self.grid.get_neighbors(agent.coord))]
        #     if self.on_goal(agent):
        #         agent_moves.append(
        #             (Agent(agent.coord, agent.color, agent.identifier, waiting_cost=agent.waiting_cost + 1), 0))
        #     else:
        #         agent_moves.append((Agent(agent.coord, agent.color, agent.identifier), 1 + agent.waiting_cost))
        #     agents_moves.append(agent_moves)

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


    def get_child(self, parent: Node, operator: Tuple[Direction, ...]) -> Node:
        assert len(operator) == len(parent.state.agents)
        agents = []
        costs = parent.cost
        for i, agent in enumerate(parent.state.agents):
            waiting_costs = 0
            if self.on_goal(agent):
                if operator[i][0] is not Direction.WAIT:
                    costs += agent.waiting_cost + 1
                else:
                    waiting_costs = agent.waiting_cost + 1
            else:
                costs += 1
            agents.append(Agent(agent.coord.move(operator[i][0]), agent.color, agent.identifier, waiting_cost=waiting_costs))

        child_state = State(agents)
        return Node(child_state, costs, self.heuristic(child_state), parent=parent)

    def get_children(self, parent: Node, v: int) -> Tuple[List[Node], int]:
        # TODO: Cache results? Create algorithm to obtain applicable operators more efficiently than filtering cartesian product?
        operators = itertools.product(*[self.osf[agent.color][agent.coord.y][agent.coord.x] for agent in parent.state.agents])
        selected_children = []
        next_value = float('inf')
        i = 0
        for operator in operators:
            i += 1
            value = sum(map((lambda x : x[1]), operator))
            # print(f"Generated operator with direction {operator[0][0].name}. Value={value} and v={v}")
            if value == v:
                selected_children.append(self.get_child(parent, operator))
            elif value > v:
                next_value = min(value, next_value)
        return selected_children, next_value

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






