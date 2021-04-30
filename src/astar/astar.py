from __future__ import annotations

from heapq import heappush, heappop
from typing import List, Optional

from src.astar.node import Node
from src.astar.state import State
from src.problem.mapf_problem import MAPFProblem
from src.util.path import Path


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
        paths.append(Path(path, agent.identifier))
    print(f"Path: {[path.path for path in paths]}")
    return paths


class EPEAStar:
    """
    :param problem: The problem instance that will be solved
    """

    def __init__(self, problem: MAPFProblem):
        self.problem = problem
        initial_state = State(self.problem.grid.agents)
        self.initial_node = Node(initial_state, len(self.problem.grid.agents), self.problem.heuristic(initial_state))

    def solve(self) -> Optional[List[Path]]:
        frontier = []
        """
        TODO: Replace seen and fully_expanded by dict and expand if:
          - 
        """
        seen = set()  # Avoid re-adding states that already have been expanded at least once
        fully_expanded = set()  # Avoid evaluating states that have been fully expanded already
        heappush(frontier, self.initial_node)

        counter = 0
        while frontier:
            node = heappop(frontier)
            if node.state in fully_expanded:
                continue
            if self.problem.is_solved(node.state):
                print(f"Solved! Frontier size: {len(frontier)}, Cost: {node.cost}")
                return convert_path(get_path(node))

            counter += 1
            if counter % 1000 == 0:
                print(f"Iteration: {counter}, frontier size: {len(frontier)}")

            children, next_value = self.problem.expand(node, node.delta_f)
            for child in children:
                if child.state not in seen and child.state != node.state:
                    heappush(frontier, child)

            if next_value == float('inf'):
                fully_expanded.add(node.state)
            else:
                node.delta_f = next_value
                node.value = node.cost + node.heuristic + node.delta_f
                heappush(frontier, node)
            seen.add(node.state)
        return None
