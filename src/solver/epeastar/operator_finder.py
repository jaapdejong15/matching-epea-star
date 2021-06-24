from copy import copy
from typing import List

from src.solver.epeastar.pdb_generator import PDBTable
from src.util.direction import Direction


class OperatorFinder:
    """
    Implements a more efficient way of selecting operators. The speed of this algorithm is crucial for the performance
    of EPEA* since every node expansion an OperatorFinder is constructed and find_operators is executed.
    find_operators .
    """

    __slots__ = 'operators', 'target_sum', 'agent_operators', 'next_target_value', 'min_values', 'max_values'

    def __init__(self, target_sum: int, agent_operators: List[PDBTable]):
        """
        Constructs an OperatorFinder instance
        :param target_sum:      Target value to reach
        :param agent_operators: Pattern database table for each agent
        """
        self.operators: List[List[List[Direction]]] = []
        self.target_sum = target_sum
        self.agent_operators = agent_operators
        self.next_target_value = float('inf')
        self.min_values = []
        self.max_values = []
        s_min = 0
        s_max = 0
        for operators in reversed(agent_operators):
            self.min_values.append(s_min)
            self.max_values.append(s_max)
            s_min += operators[0][1]
            s_max += operators[-1][1]
        self.min_values.reverse()
        self.max_values.reverse()

    def find_operators(self,
                       current_agent: int,
                       previous_operators: List[List[Direction]],
                       previous_sum: int) -> None:
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

            # If the minimum possible value is larger than the target value, return and update the next target value
            if current_sum + self.min_values[current_agent] > self.target_sum:
                self.next_target_value = min(self.next_target_value, current_sum + self.min_values[current_agent])
                return

            # If this is the bottom of the recursive tree, check if the target sum is reached
            if current_agent == len(self.agent_operators) - 1:
                if current_sum == self.target_sum:
                    self.operators.append(current_operators)
                continue

            # If the maximum possible value is smaller than the target value, do not go deeper in recursion
            if current_sum + self.max_values[current_agent] < self.target_sum:
                continue

            # Find assignments for remaining agents
            self.find_operators(current_agent + 1, current_operators, current_sum)
            assert self.next_target_value > self.target_sum
