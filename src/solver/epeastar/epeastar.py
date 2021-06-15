from __future__ import annotations

from heapq import heappush, heappop
from typing import List, Optional, Tuple

from src.solver.epeastar.mapf_problem import MAPFProblem
from src.util.agent import Agent
from src.util.cat import CAT
from src.util.node import Node
from src.util.path import Path
from src.util.state import State
from src.util.statistic_tracker import StatisticTracker


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

    def __init__(self,
                 problem: MAPFProblem,
                 agents: List[Agent],
                 cats: List[CAT],
                 stat_tracker: StatisticTracker,
                 max_cost=float('inf')):
        """
        Constructs an EPEAStar instance.
        :param problem:     The MAPFProblem that should be solved
        :param agents:      The moving agents
        :param max_cost:    The maximum cost of the solution. Stop the solver if exceeded.
        """
        self.problem = problem
        initial_state = State(agents)
        self.cats = cats
        self.initial_node = Node(initial_state, len(agents), self.problem.get_heuristic(initial_state), 0, 0)
        self.stat_tracker = stat_tracker
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

        ignored_paths = [agent.identifier for agent in self.initial_node.state.agents]

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
            child_states, next_value = self.problem.expand(node)
            nodes_expanded += 1
            for child_state, cost in child_states:
                if child_state not in seen and child_state != node.state:
                    # Create Node
                    heuristic = self.problem.get_heuristic(child_state)
                    time = node.time + 1
                    collisions = 0
                    for agent in child_state.agents:
                        collisions += sum(cat.get_cat(ignored_paths, agent.coord, time) for cat in self.cats)
                    child_node = Node(child_state, cost, heuristic, collisions, time, parent=node)

                    seen.add(child_state)
                    heappush(frontier, child_node)

            # Check if the node can be expanded again
            if next_value == float('inf'):
                fully_expanded.add(node.state)
            elif next_value < self.max_cost:
                node.delta_f = next_value
                node.value = node.cost + node.heuristic + node.delta_f
                heappush(frontier, node)
        return None
