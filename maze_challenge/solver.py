from abc import ABC, abstractmethod
from typing import Dict, List, Set, Tuple

# Define how to move in each direction
DIRECTION_VECTORS = {
    "NORTH": (-1, 0),
    "SOUTH": (1, 0),
    "EAST": (0, 1),
    "WEST": (0, -1),
}

# Get the reverse of a direction for backtracking
REVERSE_DIRECTION = {
    "NORTH": "SOUTH",
    "SOUTH": "NORTH",
    "EAST": "WEST",
    "WEST": "EAST",
}


class Solver(ABC):
    """Base class for all solvers. Enforces interface consistency."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    @abstractmethod
    def choose_move(
        self,
        position: Tuple[int, int],
        cherry_position: Tuple[int, int],
        possible_moves: Dict[str, Tuple[int, int]],
    ) -> str:
        """
        Given the current position and possible directions, return a move as a string:
        One of: "N", "S", "E", "W"
        """
        pass
