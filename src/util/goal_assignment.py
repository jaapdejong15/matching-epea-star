from __future__ import annotations


class GoalAssignment:
    """
    Represents a goal assignment.
    """

    __slots__ = 'initial_heuristic', 'agent_ids'

    def __init__(self, agent_ids, initial_heuristic):
        """
        Creates a matching from the grid.
        :param agent_ids:           Sorted list of agent identifiers corresponding to the goal assignment
        :param initial_heuristic:   Initial heuristic value of the goal assignment
        """
        self.agent_ids = agent_ids
        self.initial_heuristic = initial_heuristic

    def __lt__(self, other: GoalAssignment) -> bool:
        """
        Allows goal assignments to be sorted/heapified by their initial heuristic
        :param other:   Goal assignment to compare with
        :return:        True if this goal assignment has a lower initial heuristic
        """
        return self.initial_heuristic < other.initial_heuristic
