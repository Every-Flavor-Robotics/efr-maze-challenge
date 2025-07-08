import os
import platform

from labyrinth.generate import KruskalsGenerator
from labyrinth.maze import Cell, Direction, Maze

from dijkstra import (  # Assuming dijkstra.py is in the same directory
    dijkstra,
    manhattan_distance,
)


def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")


class MazeInterface:
    def __init__(self, width: int, height: int, silent: bool = False):
        self.width = width
        self.height = height

        # Whether to print messages or not
        self.silent = silent

        self.maze = self._generate()

        self.shortest_path, _ = dijkstra(
            self.maze, self.maze.start_cell, self.maze.end_cell
        )

        # Position of the agent in the maze
        self.agent_position = self.maze.start_cell

        self.visited_cells = set()
        self.visited_cells.add(self.agent_position.coordinates)

        self.num_moves = 0
        self.goal_reached = False

    def _generate(self):
        """Generate a maze with the specified dimensions."""
        return Maze(self.width, self.height, generator=KruskalsGenerator())

    def get_position(self):
        """Get the current position of the agent in the maze."""
        return self.agent_position.coordinates

    def get_possible_moves(self):
        moves = self.agent_position.open_walls

        return {
            "NORTH": Direction.N in moves,
            "SOUTH": Direction.S in moves,
            "EAST": Direction.E in moves,
            "WEST": Direction.W in moves,
        }

    def completed(self):
        """Check if the agent has reached the goal."""
        return self.goal_reached

    def move(self, direction: str):
        """Move the agent in the specified direction if possible."""

        # Map from string to Direction enum
        direction_map = {
            "NORTH": Direction.N,
            "SOUTH": Direction.S,
            "EAST": Direction.E,
            "WEST": Direction.W,
        }
        if direction not in direction_map:
            raise ValueError(f"Invalid direction: {direction}")

        direction = direction_map[direction]

        moved = False
        if direction in self.agent_position.open_walls:
            self.agent_position = self.maze.neighbor(self.agent_position, direction)
            moved = True
            self.visited_cells.add(self.agent_position.coordinates)

            if self.agent_position == self.maze.end_cell:
                self.goal_reached = True
                if not self.silent:
                    print("move(): Goal reached!")
        else:
            if not self.silent:
                print(
                    f"move(): Cannot move {direction.name}, wall is blocking the way."
                )

        # Only count moves if the goal is not reached
        if not self.goal_reached:
            self.num_moves += 1

        return moved

    def _draw_sprite(self, cell, cell_width):
        """Return a string representation of the cell for drawing."""
        if cell == self.agent_position:
            return " 🤖 "
        elif cell == self.maze.start_cell:
            return " 🏁 "
        elif cell == self.maze.end_cell:
            return " 🏆 "
        elif cell.coordinates in self.visited_cells:
            return " 🔸 "
        else:
            return " " * cell_width

    def draw(self):
        """Print the maze in a human-readable format, ALSO prints the agent's position."""

        clear_screen()

        cell_width = 4
        maze_str = "+" + ((("-" * cell_width) + "+") * self.width) + "\n"
        for row in range(self.height):
            maze_str += "|"
            for column in range(self.width):
                cell = self.maze[row, column]
                maze_str += self._draw_sprite(cell, cell_width)
                maze_str += " " if Direction.E in cell.open_walls else "|"
            maze_str += "\n+"
            for column in range(self.width):
                maze_str += (
                    " " if Direction.S in self.maze[row, column].open_walls else "-"
                ) * cell_width
                maze_str += "+"
            maze_str += "\n"

            # Stylized stats display
            stats = f"""
        🧭  Maze Stats
        ──────────────
        🎯 Current Score: {self._compute_score()}
        🤖 Robot Position: {self.agent_position.coordinates}
        🔸 Visited Cells: {len(self.visited_cells)} / {self.width * self.height}
        📦 Total Moves: {self.num_moves}
        🏆 Goal Reached: {"Yes" if self.goal_reached else "No"}

        📋  Maze Stats
        ──────────────
        📐 Size: {self.width} x {self.height}
        🏁 Start: {self.maze.start_cell.coordinates}
        🏆 End:   {self.maze.end_cell.coordinates}
        """
        print(maze_str + stats)

    def _compute_score(self):
        """Compute the score based on the number of moves and visited cells."""

        # Scoring algorithm:
        # Start with a base score of 10,000 and apply penalties:
        # - 100 * manhattan distance to the goal (ignoring walls)
        # - 10 points for each move made more than the shortest path
        # - 1 points for each visited cell (to encourage exploration)

        return (
            10000
            - 100 * manhattan_distance(self.agent_position, self.maze.end_cell)
            - max(0, self.num_moves - len(self.shortest_path) - 1)
            * 10  # Penalize for extra moves
            - len(self.visited_cells)
        )

    def print_final_stats(self):
        """Print the final stats of the maze challenge in a stylized format."""

        shortest_path_length = len(self.shortest_path) - 1  # Exclude the start cell
        print(
            f"""
━━━━━━━━━━━━━━━━━━━━━━━
🏁  Final Maze Summary
━━━━━━━━━━━━━━━━━━━━━━━
🗺️  Cells Visited:     {len(self.visited_cells)} / {self.width * self.height}
🕹️  Moves Taken:       {self.num_moves} moves
📏 Shortest Path:      {shortest_path_length} moves
🏆 Goal Reached:       {'✅ Yes!' if self.goal_reached else '❌ No'}

🎯 Final Score:        {self._compute_score()}
━━━━━━━━━━━━━━━━━━━━━━━
"""
        )
