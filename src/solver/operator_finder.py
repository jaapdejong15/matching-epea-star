from copy import copy
from typing import List, Tuple

from src.solver.pdb import PDBTable
from src.util.coordinate import Direction


class OperatorFinder:
    """
    Implements a more efficient way of selecting operators. The speed of this algorithm is crucial for the performance of
    EPEA* since it is executed in every node.
    TODO: Store max_values with node or PDB to avoid recalculating?
    """

    __slots__ = 'operators', 'target_sum', 'pdb_tables', 'next_target_value', 'min_values', 'max_values'

    def __init__(self, target_sum: int, pdb_tables: List[Tuple[List[int], PDBTable]]):
        """
        Constructs an OperatorFinder instance
        :param target_sum:      Target value to reach
        :param pdb_tables:      List of operators with their delta value for each agent
        """
        self.operators = []
        self.target_sum = target_sum
        self.pdb_tables = pdb_tables
        self.next_target_value = float('inf')

        # Calculate values of choosing minimum or maximum values in all next PDBs for each PDB
        # PDBs have to be sorted on value for this to work
        self.min_values = []
        self.max_values = []
        s_min = 0
        s_max = 0
        for operators in reversed(pdb_tables):
            self.min_values.append(s_min)
            self.max_values.append(s_max)
            s_min += operators[0][1]
            s_max += operators[-1][1]
        self.min_values.reverse()
        self.max_values.reverse()

    def find_operators(self, current_table: int, previous_operators, previous_sum) -> None:
        """
        Finds all combinations of operators where the sum of delta values is equal to self.target_sum.
        Results are stored in self.operators
        :param current_table:       Index of the table for which operators are being evaluated (recursive tree depth)
        :param previous_operators:  Operators that were picked for agents with a lower index
        :param previous_sum:        Sum of delta values for all previous operators
        :return:                    Nothing
        """
        # For each operator of the current agent
        agents, table = self.pdb_tables[current_table]
        for i, row in enumerate(table):
            current_operators: List[Direction] = copy(previous_operators)

            # Assign all operators.
            for agent, move in zip(agents, row[0]):
                current_operators[agent] = move
            current_sum = previous_sum + row[1]

            # If taking the lowest possible values from this point will cause us to overshoot the target
            if current_sum + self.min_values[current_table] > self.target_sum:
                self.next_target_value = min(self.next_target_value, current_sum + self.min_values[current_table])
                return

            # If we are at the bottom of the recursive tree
            if current_table == len(self.pdb_tables) - 1:
                if current_sum == self.target_sum:
                    self.operators.append(current_operators)
                continue

            # If we cannot reach the target value by taking the highest possible value from this point
            if current_sum + self.max_values[current_table] < self.target_sum:
                continue

            self.find_operators(current_table + 1, current_operators, current_sum)
            assert self.next_target_value > self.target_sum
