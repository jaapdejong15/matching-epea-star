class StatisticTracker:
    __slots__ = 'assignment_evaluation', 'max_group_size'

    def __init__(self):
        self.assignment_evaluation = 0
        self.max_group_size = 1

    def assignment_evaluated(self):
        self.assignment_evaluation += 1

    def group_merged(self, group_size: int):
        self.max_group_size = max(self.max_group_size, group_size)
