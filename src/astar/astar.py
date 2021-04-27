from mapfmclient import Problem, Solution
from typing import List, Optional
from heapq import heappush, heappop

from src.astar.matching_problem import State, MatchingProblem

class Node:

    def __init__(self, state: State, cost: int, heuristic: int, parent = None):
        self.state = state
        self.cost = cost
        self.heuristic = heuristic
        self.value = cost + heuristic
        self.parent = parent

    def __eq__(self, other):
        return self.value == other.value

    def __lt__(self, other):
        return self.value < other.value

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

    def __init__(self, problem: Problem):
        self.problem = MatchingProblem(problem)
        initial_state = State(self.problem.agents)
        self.initial_node = Node(initial_state, len(self.problem.agents), self.problem.heuristic(initial_state))

    def solve(self) -> Optional[Solution]:
        frontier = []
        seen = set() # Avoid doing the same nodes over and over again
        heappush(frontier, self.initial_node)

        while frontier:
            node = heappop(frontier)
            if node.state in seen:
                continue
            seen.add(node.state)
            if self.problem.is_solved(node.state):
                return convert_path(get_path(node))

            children = self.problem.expand(node.state)
            child_not_added = False
            min_value = float('inf') # Lowest f(n) of the unopened children, set as new value for parent node
            for (state, added_cost) in children:
                if state not in seen:
                    heuristic = self.problem.heuristic(state)
                    child_cost = node.cost + added_cost
                    child_value = child_cost + heuristic # f(n_c)
                    if child_value == node.value: # For an admissible heuristic, the child value cannot be lower than the parent value
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

        return None
