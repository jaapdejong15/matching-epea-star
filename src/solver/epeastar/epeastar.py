from __future__ import annotations

from heapq import heappush, heappop
from typing import List, Optional, Tuple

from src.solver.epeastar.mapf_problem import MAPFProblem
from src.util.agent import Agent
from src.util.node import Node
from src.util.path import Path
from src.util.state import State


def get_path(node: Node) -> List[Node]:
    path = []
    while node is not None:
        path.append(node)
        node = node.parent
    path.reverse()
    return path


def convert_path(nodes: List[Node]) -> List[Path]:
    paths = []
    for i, agent in enumerate(nodes[0].state.agents):
        path = []
        for node in nodes:
            path.append((node.state.agents[i].coord.x, node.state.agents[i].coord.y))
        assert nodes[-1].cost <= len(nodes) * len(nodes[-1].state.agents)
        paths.append(Path(path, agent.identifier))
    return paths


class EPEAStar:

    def __init__(self, problem: MAPFProblem, agents: List[Agent], max_cost=float('inf')):
        """
        Constructs an EPEAStar instance.
        :param problem:     The MAPFProblem that should be solved
        :param agents:      The moving agents
        :param max_cost:    The maximum cost of the solution. Stop the solver if exceeded.
        """
        self.problem = problem
        initial_state = State(agents)
        self.initial_node = Node(initial_state, len(agents), self.problem.get_heuristic(initial_state))
        self.max_cost = max_cost

    def solve(self) -> Optional[Tuple[List[Path], int]]:
        """
        Solves the problem instance in self.problem
        :return: Path for every agent if a solution was found, otherwise None
        """
        frontier = []
        seen = set()  # Avoid re-adding states that already have been expanded at least once
        fully_expanded = set()  # Avoid evaluating states that have been fully expanded already
        heappush(frontier, self.initial_node)

        nodes_expanded = 0
        loop_counter = 0
        while frontier:
            node = heappop(frontier)
            if node.value >= self.max_cost:
                # Current solution will not improve existing solution
                return None

            # Don't evaluate node if its state is already fully expanded
            if node.state in fully_expanded:
                continue
            loop_counter += 1

            # Check if the current state is a solution to the problem
            if self.problem.is_solved(node.state):
                return convert_path(get_path(node)), node.cost

            # Expand the current node
            children, next_value = self.problem.expand(node)
            nodes_expanded += 1
            for child in children:
                if child.state not in seen and child.state != node.state:
                    seen.add(child.state)
                    heappush(frontier, child)

            # Check if the node can be expanded again
            if next_value == float('inf'):
                fully_expanded.add(node.state)
            elif next_value < self.max_cost:
                node.delta_f = next_value
                node.value = node.cost + node.heuristic + node.delta_f
                heappush(frontier, node)
        return None
