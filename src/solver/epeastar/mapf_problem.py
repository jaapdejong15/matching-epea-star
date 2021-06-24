import itertools
from typing import List, Tuple

from mapfmclient import MarkedLocation

from src.solver.epeastar.heuristic import Heuristic
from src.solver.epeastar.operator_finder import OperatorFinder
from src.solver.epeastar.pdb_generator import PDB
from src.util.agent import Agent
from src.util.direction import Direction
from src.util.node import Node
from src.util.state import State


class MAPFProblem:
    """
    Contains methods that are used by the EPEA* solver that are specific to the MAPF(M) problem.
    """

    def __init__(self, goals: List[MarkedLocation], pdb: PDB, heuristic: Heuristic):
        """
        Creates an instance of MAPFProblem.
        :param goals:       List of goals
        :param pdb:         Precomputed pattern database
        param heuristic:    Precomputed heuristic values
        """
        self.osf = pdb
        self.goals = goals
        self.heuristic = heuristic

    def on_goal(self, agent: Agent) -> bool:
        """
        Checks if an agent is on a goal of the correct color.
        :param agent:   Agent to check if it is on its goal
        :returns:        True if the agent is on a goal, False otherwise
        """
        for goal in self.goals:
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

    def expand(self, node: Node) -> Tuple[List[Tuple[State, int]], int]:
        """
        Expands an A* search tree node.
        :param node:    parent node
        :returns:       List of child nodes and the next Δf value for the parent node
        """
        v = node.delta_f
        children, next_value = self.get_children(node, v)

        # Check constraints
        selected_children = []
        for child_state, cost in children:
            coords = set()
            edge_conflict = False
            vertex_conflict = False
            for i, agent in enumerate(child_state.agents):
                # Check vertex conflict
                if agent.coord in coords:
                    vertex_conflict = True
                    break
                coords.add(agent.coord)

                # Check edge conflicts
                for j in range(i + 1, len(node.state.agents)):
                    if child_state.agents[i].coord == node.state.agents[j].coord and child_state.agents[j].coord == \
                            node.state.agents[i].coord:
                        edge_conflict = True
                        break
                if edge_conflict:
                    break
            if not vertex_conflict and not edge_conflict:
                selected_children.append((child_state, cost))
        return selected_children, next_value

    def get_heuristic(self, state: State) -> int:
        """
        Calculates the heuristic for the given state state
        :param state:   state to calculate the heuristic for
        :returns:       heuristic value for the state
        """
        total = 0
        for agent in state.agents:
            total += self.heuristic.heuristic[agent.color][agent.coord.y][agent.coord.x]
        return total

    def get_child(self, parent: Node, operator: Tuple[Direction, ...]) -> Tuple[State, int]:
        """
        Applies an operator to a parent node to create a child node
        :param parent:      The parent node
        :param operator:    Tuple of Directions of length |agents|
        :returns:           The child node with the additional cost
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
        return child_state, costs

    def get_children(self, parent: Node, v: int) -> Tuple[List[Tuple[State, int]], int]:
        """
        Uses the operator selection function (OSF) to get all relevant children from the parent node.
        :param parent:  Parent node
        :param v:       The Δf value.
        :returns:       List of child states together with their costs and next Δf value for the parent node
        """
        operator_finder = OperatorFinder(v, [self.osf.pdb[agent.color][agent.coord.y][agent.coord.x] for agent in
                                             parent.state.agents])
        operator_finder.find_operators(0, [], 0)

        expanded_operators = []
        for operator in operator_finder.operators:
            expanded_operators += list(itertools.product(*operator))

        children = [self.get_child(parent, operator) for operator in expanded_operators]
        return children, operator_finder.next_target_value
