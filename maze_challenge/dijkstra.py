from heapq import heappop, heappush
from typing import Dict, List, Optional, Tuple

from labyrinth.grid import Graph
from labyrinth.maze import Cell, Direction, Maze


def manhattan_distance(cell1: Cell, cell2: Cell) -> int:
    """Calculate the Manhattan distance between two coordinates."""
    coord1 = cell1.coordinates
    coord2 = cell2.coordinates
    return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])


class ComparableCell:
    """A cell that can be compared based on its coordinates."""

    def __init__(self, cell: Cell, goal: Cell) -> None:
        self.cell = cell
        self.goal = goal

    def __lt__(self, other: "ComparableCell") -> bool:
        return manhattan_distance(self.cell, self.goal) < manhattan_distance(
            other.cell, other.goal
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ComparableCell) and self.cell == other.cell

    def __hash__(self) -> int:
        return hash(self.cell.coordinates)

    def __repr__(self) -> str:
        return f"ComparableCell({self.cell.coordinates})"


def dijkstra(maze: Maze, start: Cell, goal: Cell) -> Tuple[List[Cell], int]:
    """Find the shortest path in a maze using Dijkstra's algorithm, respecting walls."""

    wrapped_start = ComparableCell(start, goal)
    wrapped_goal = ComparableCell(goal, goal)

    heap = [(0, wrapped_start)]
    came_from: Dict[ComparableCell, Optional[ComparableCell]] = {wrapped_start: None}
    cost_so_far: Dict[ComparableCell, int] = {wrapped_start: 0}
    visited = set()

    while heap:
        current_cost, current = heappop(heap)
        if current in visited:
            continue
        visited.add(current)

        if current == wrapped_goal:
            break

        for direction in current.cell.open_walls:
            neighbor_cell = maze.neighbor(current.cell, direction)
            if neighbor_cell is None:
                continue
            neighbor = ComparableCell(neighbor_cell, goal)
            new_cost = current_cost + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                heappush(heap, (new_cost, neighbor))

    if wrapped_goal not in came_from:
        return [], float("inf")

    # Reconstruct path
    path_list = []
    current = wrapped_goal
    while current != wrapped_start:
        path_list.append(current.cell)
        current = came_from[current]
    path_list.append(start)
    path_list.reverse()

    return path_list, cost_so_far[wrapped_goal]
