from labyrinth.grid import Graph
from labyrinth.maze import Cell, Direction, Maze


def dijkstra(maze: Maze, start: Cell, goal: Cell) -> Tuple[Graph, int]:
    """Find the shortest path in a maze using Dijkstra's algorithm."""

    graph = maze._grid.graph  # Access the underlying graph representation of the maze

    # Find the shortest path using Dijkstra's algorithm
    path, cost = dijkstra(graph, start, goal)

    return path, cost
