from __future__ import annotations

from heapq import heappush, heappop
from typing import List, Optional, Tuple

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
    return paths


class PEAStar:
    """
    :param problem: The problem instance that will be solved
    :param memory_constant: Determines the amount of memory savings in exchange for runtime. Also called C.
                 C = 0: Maximum memory savings
                 C = infinity: No memory savings, normal A*
    """

    def __init__(self, problem: MAPFProblem, memory_constant: int = 0):
        self.problem = problem
        self.memory_constant = memory_constant
        initial_state = State(self.problem.agents)
        self.initial_node = Node(initial_state, len(self.problem.agents), self.problem.heuristic(initial_state))

    def solve(self) -> Optional[List[Path]]:
        frontier = []
        """
        TODO: Replace seen and fully_expanded by dict and expand if:
          - 
        """
        seen = set()  # Avoid re-adding states that already have been expanded at least once
        fully_expanded = set()  # Avoid evaluating states that have been fully expanded already
        heappush(frontier, self.initial_node)

        while frontier:
            node = heappop(frontier)
            if node.state in fully_expanded:
                continue
            if self.problem.is_solved(node.state):
                return convert_path(get_path(node))

            children = self.problem.expand(node.state)
            child_not_added = False
            min_value = float('inf')  # Lowest cost of the unopened children, used as new value for parent node
            for (state, added_cost) in children:
                if state not in seen and state != node.state:
                    heuristic = self.problem.heuristic(state)
                    child_cost = node.cost + added_cost
                    child_value = child_cost + heuristic  # child cost

                    # For an admissible heuristic, the child value cannot be lower than the parent value
                    if child_value <= node.value + self.memory_constant:
                        child_node = Node(state, child_cost, heuristic, parent=node)
                        heappush(frontier, child_node)
                    else:
                        child_not_added = True
                        min_value = min(min_value, child_value)

            # If a child was not added
            if child_not_added:
                # Set node value to the lowest value of the unopened children and put in frontier
                node.value = min_value
                heappush(frontier, node)
            else:
                fully_expanded.add(node.state)
            seen.add(node.state)
        return None
