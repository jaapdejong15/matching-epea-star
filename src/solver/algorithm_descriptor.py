from enum import Enum


class Algorithm(Enum):
    """
    Enum of the different EPEA*-algorithms for solving MAPFM
    """
    ExhaustiveMatching = 'EPEA* (exhaustive matching)'
    ExhaustiveMatchingSorting = 'EPEA* (exhaustive matching with sorting)'
    ExhaustiveMatchingSortingID = 'EPEA* (exhaustive matching with sorting and ID)'
    HeuristicMatching = 'EPEA* (heuristic matching)'


class AlgorithmDescriptor:
    """
    Descriptor for EPEA*-algorithms for solving MAPFM
    """

    def __init__(self, algorithm: Algorithm, independence_detection: bool):
        """
        Constructs an AlgorithmDescriptor instance
        :param algorithm:               The type of EPEA* algorithm
        :param independence_detection:  When set to true, ID will be used
        """
        self.algorithm = algorithm
        self.id = independence_detection

    def get_name(self):
        """
        Creates a textual description of the algorithm
        :return:    String with algorithm description
        """
        return f"{self.algorithm.value}{' with ID' if self.id else ''}"
