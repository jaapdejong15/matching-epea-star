from enum import Enum


class Algorithm(Enum):
    ExhaustiveMatching='EPEA* (exhaustive matching)'
    ExhaustiveMatchingSorting='EPEA* (exhaustive matching with sorting)'
    HeuristicMatching='EPEA* (heuristic matching)'

class AlgorithmDescriptor:
    def __init__(self, algorithm: Algorithm, independence_detection: bool):
        self.algorithm = algorithm
        self.id = independence_detection

    def get_name(self):
        return f"{self.algorithm.value}{' with ID'if self.id else ''}"


