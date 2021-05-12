from typing import List, Tuple, Dict

from src.solver.agent import Agent
from src.solver.node import Node
from src.solver.operator_finder import OperatorFinder
from src.solver.pdb import SingleColorPDB, PDB
from src.solver.state import State
from src.util.coordinate import Direction
from src.util.grid import Grid


class MAPFProblem:

    def __init__(self, grid: Grid):
        """
        Creates an instance of MAPFProblem.
        :param grid:    2d grid with starting locations and goals
        """
        self.grid = grid
        self.osf: Dict[int, Tuple[List[int], PDB]] = dict()
        for color in self.grid.colors:
            pdb = SingleColorPDB(color, grid)
            for agent in filter(lambda a: a.color == color, self.grid.agents):
                self.osf[agent.identifier] = ([agent.identifier], pdb)

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
        return all(self.on_goal(agent) for agent in state.agents)

    def expand(self, node: Node) -> Tuple[List[Node], int]:
        """
        Expands an A* search tree node.
        :param node:    parent node
        :returns:       List of child nodes and the next Δf value for the parent node
        """
        v = node.delta_f
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

        child_state = State(agents)
        return Node(child_state, costs, self.heuristic(child_state), parent=parent)

    def get_children(self, parent: Node, v: int) -> Tuple[List[Node], int]:
        """
        Uses the operator selection function (OSF) to get all relevant children from the parent node.
        :param parent:  Parent node
        :param v:       The Δf value.
        :returns:       List of child nodes and next Δf value for the parent node
        """
        operator_finder = OperatorFinder(v, [(pdb[0], pdb[1].get(parent)) for pdb in self.osf.values()])
        operator_finder.find_operators(0, [None] * len(self.grid.agents), 0)
        children = [self.get_child(parent, operator) for operator in operator_finder.operators]
        return children, operator_finder.next_target_value

    def merge_pdbs(self):

