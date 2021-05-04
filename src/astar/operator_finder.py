from copy import copy
from typing import List, Tuple

from src.util.coordinate import Direction


class OperatorFinder:
    """
    Implements a more efficient way of selecting operators. The speed of this algorithm is crucial for the performance of
    EPEA* since it is executed in every node.
    """

    def __init__(self, target_sum: int, agent_operators: List[List[Tuple[Direction, int]]]):
        """
        Constructs an OperatorFinder instance
        :param target_sum:      Target value to reach
        :param agent_operators: List of operators with their delta value for each agent
        """
        self.operators = []
        self.target_sum = target_sum
        self.agent_operators = agent_operators
        self.next_target_value = float('inf')

    def find_operators(self, current_agent: int, previous_operators, previous_sum) -> None:
        """
        Finds all combinations of operators where the sum of delta values is equal to self.target_sum.
        Results are stored in self.operators
        :param current_agent:       Index of the agent for which operators are being evaluated (recursive tree depth)
        :param previous_operators:  Operators that were picked for agents with a lower index
        :param previous_sum:        Sum of delta values for all previous operators
        :return:                    Nothing
        """
        # For each operator of the current agent
        for i, operator in enumerate(self.agent_operators[current_agent]):
            current_operators = copy(previous_operators)
            current_operators.append(operator[0])
            current_sum = previous_sum + operator[1]
            if current_sum > self.target_sum:
                self.next_target_value = min(self.next_target_value, current_sum)
                # TODO: Are these target values obtainable? Shouldn't we check if we are at the last agent?
                return  # Since operators are sorted, there is no need to check the other operators
            if current_agent == len(self.agent_operators) - 1:
                if current_sum == self.target_sum:
                    self.operators.append(current_operators)
                continue
            self.find_operators(current_agent + 1, current_operators, current_sum)
