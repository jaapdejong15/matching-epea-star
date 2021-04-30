from copy import copy
from typing import List, Tuple

from src.util.coordinate import Direction

"""
Implements a more efficient way of selecting operators. The speed of this algorithm is crucial for the performance of
EPEA* since it is executed in every node.
"""
class OperatorFinder:
    def __init__(self, target_sum: int, agent_operators: List[List[Tuple[Direction, int]]]):
        self.operators = []
        self.target_sum = target_sum
        self.agent_operators = agent_operators
        self.next_target_value = float('inf')

    def find_operators(self, current_agent: int, previous_operators, previous_sum):
        # For each operator of the current agent
        for i, operator in enumerate(self.agent_operators[current_agent]):
            current_operators = copy(previous_operators)
            current_operators.append(operator[0])
            current_sum = previous_sum + operator[1]
            if current_sum > self.target_sum:
                self.next_target_value = min(self.next_target_value, current_sum)
                return # Since operators are sorted, there is no need to check the other operators
            if current_agent == len(self.agent_operators) - 1:
                if current_sum == self.target_sum:
                    self.operators.append(current_operators)
                continue
            self.find_operators(current_agent + 1, current_operators, current_sum)





