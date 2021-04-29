from __future__ import annotations

from heapq import heappush, heappop
from typing import List, Optional

from mapfmclient import Problem, Solution

from src.astar.state import State
from src.problem.standard_problem import StandardProblem


class Node:

    def __init__(self, state: State, cost: int, heuristic: int, parent=None):
        self.state = state
        self.cost = cost  # f(n)
        self.heuristic = heuristic  # h(n)
        self.value = cost + heuristic  # F(n) - Stored value. Will be larger than cost + heuristic when the node is collapsed
        self.parent = parent

    def __eq__(self, other: Node):
        return self.value == other.value

    def __lt__(self, other: Node):
        return (self.value, self.heuristic) < (other.value, other.heuristic)


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


class PEAStar:
    """
    :param problem: The problem instance that will be solved
    :param memory_constant: Determines the amount of memory savings in exchange for runtime. Also called C.
                 C = 0: Maximum memory savings
                 C = infinity: No memory savings, normal A*
    """

    def __init__(self, problem: Problem, memory_constant: int = 0, pre_compute_heuristics=False):

        self.problem = StandardProblem(problem, compute_heuristic=pre_compute_heuristics)
        self.memory_constant = memory_constant
        initial_state = State(self.problem.agents)
        self.initial_node = Node(initial_state, len(self.problem.agents), self.problem.heuristic(initial_state))

    def solve(self) -> Optional[Solution]:
        frontier = []
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
