import json
import os
import platform
import random
from pathlib import Path

from labyrinth.generate import KruskalsGenerator
from labyrinth.maze import Direction, Maze

from maze_challenge.dijkstra import (  # Assuming dijkstra.py is in the same directory
    dijkstra,
    manhattan_distance,
)


def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")


class MazeInterface:
    def __init__(
        self, width: int, height: int, silent: bool = False, skip_generate: bool = False
    ):
        self.width = width
        self.height = height

        # Whether to print messages or not
        self.silent = silent

        self.maze = self._generate(skip_generate)

        self.shortest_path, _ = dijkstra(
            self.maze, self.maze.start_cell, self.maze.end_cell
        )

        # Generate a random cherry location, ensuring it's not the start or end cell
        self.cherry_location = None
        self.cherry_cell = None

        # Do not generate a cherry if skip_generate is True
        if not skip_generate:
            while True:
                cherry_row = random.randint(0, self.height - 1)
                cherry_column = random.randint(0, self.width - 1)
                try:
                    self._set_cherry_location(cherry_row, cherry_column)
                    break
                except ValueError:
                    # Retry if the location is invalid (start or end cell)
                    continue

        self.reset()

    def reset(self):
        """Reset the maze interface to its initial state."""

        self.agent_position = self.maze.start_cell

        self.visited_cells = set()
        self.visited_cells.add(self.agent_position.coordinates)

        self.cherry_captured = False
        self.num_moves = 0
        self.goal_reached = False

    def _set_cherry_location(self, row: int, column: int):
        """Set the cherry location in the maze."""
        if (row, column) == self.maze.start_cell.coordinates or (
            row,
            column,
        ) == self.maze.end_cell.coordinates:
            raise ValueError("Cherry cannot be placed at the start or end cell.")

        self.cherry_location = (row, column)
        self.cherry_cell = self.maze[self.cherry_location]

    def _generate(self, skip_generate: bool = False):
        """Generate a maze with the specified dimensions."""
        if skip_generate:
            return Maze(self.width, self.height, generator=None)

        return Maze(self.width, self.height, generator=KruskalsGenerator())

    def get_position(self):
        """Get the current position of the agent in the maze."""
        return self.agent_position.coordinates

    def get_possible_moves(self):
        moves = self.agent_position.open_walls

        # moves is a set
        if not moves:
            return {}

        output = {
            key.name: (
                self.agent_position.coordinates[0] + key.value[1],
                self.agent_position.coordinates[1] + key.value[0],
            )
            for key in moves
        }

        # breakpoint()
        return output

    def get_cherry_location(self):
        """Get the current location of the cherry in the maze."""
        if self.cherry_location is None:
            return None
        return self.cherry_location

    def completed(self):
        """Check if the agent has reached the goal."""
        return self.goal_reached

    def move(self, direction: str):
        """Move the agent in the specified direction if possible."""

        # Map from string to Direction enum
        direction_map = {
            "N": Direction.N,
            "S": Direction.S,
            "E": Direction.E,
            "W": Direction.W,
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

            if self.agent_position == self.cherry_cell:
                self.cherry_captured = True
                if not self.silent:
                    print("move(): Cherry captured!")
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
        elif cell.coordinates == self.cherry_location:
            return " 🍒 "
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
                            🍒 Cherry Captured: {"Yes" if self.cherry_captured else "No"}


                            📋  Maze Info
                            ──────────────
                            📐 Size: {self.width} x {self.height}
                            🏁 Start: {self.maze.start_cell.coordinates}
                            🍒 Cherry: {self.cherry_location}
                            🏆 End:   {self.maze.end_cell.coordinates}
        """
        print(maze_str + stats)

    def _compute_score(self):
        """Compute the score based on the number of moves and visited cells."""

        # Scoring algorithm:
        # Start with a base score of 10,000 and apply penalties:
        # - 100 * manhattan distance to the goal (ignoring walls)
        # - 10 points for each move made more than the shortest path
        # + 500 points for capturing the cherry

        return (
            10000
            - 100 * manhattan_distance(self.agent_position, self.maze.end_cell)
            - 10 * max(0, self.num_moves - len(self.shortest_path) - 1)
            + 500 * self.cherry_captured
        )

    def _compute_secondary_scores(self):
        """Compute secondary scores for additional metrics."""

        # Reward each node visited, but penalize for moves
        explorer_score = len(self.visited_cells) * 10 - self.num_moves

        return explorer_score

    def get_stats(self):
        """Get the current stats of the maze challenge."""
        return {
            "visited_cells": len(self.visited_cells),
            "num_moves": self.num_moves,
            "goal_reached": int(self.goal_reached),
            "cherry_captured": int(self.cherry_captured),
            "score": self._compute_score(),
            "explorer_score": self._compute_secondary_scores(),
        }

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
                            🍒 Cherry Captured:    {"✅ Yes!" if self.cherry_captured else "❌ No"}
                            🏆 Goal Reached:       {"✅ Yes!" if self.goal_reached else "❌ No"}

                            ━━━━━━━━━━━━━━━━━━━━━━━
                            🎯 Efficiency Score:   {self._compute_score()}
                            🧭 Explorer Score:     {self._compute_secondary_scores()}
                            ━━━━━━━━━━━━━━━━━━━━━━━
"""
        )

    def _generate_maze_description(self):
        """Generate a description of the maze with open walls and other details."""
        open_walls = []
        for row in range(self.height):
            for col in range(self.width):
                cell = self.maze[row, col]
                for direction in cell.open_walls:
                    neighbor = self.maze.neighbor(cell, direction)
                    if neighbor and cell.coordinates < neighbor.coordinates:
                        open_walls.append(
                            [list(cell.coordinates), list(neighbor.coordinates)]
                        )

        data = {
            "width": self.width,
            "height": self.height,
            "open_walls": open_walls,
            "start": self.maze.start_cell.coordinates,
            "end": self.maze.end_cell.coordinates,
            "cherry": self.cherry_location,
        }

        return data

    def export_stats(self, filename: str) -> None:
        """Export the current run's stats to a file."""
        stats = {
            "position": self.agent_position.coordinates,
            "visited_cells": list(self.visited_cells),
            "num_moves": self.num_moves,
            "goal_reached": self.goal_reached,
            "cherry_captured": self.cherry_captured,
            "score": self._compute_score(),
            "explorer_score": self._compute_secondary_scores(),
            "shortest_path_length": len(self.shortest_path) - 1,
            "maze": self._generate_maze_description(),
        }

        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".json")
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(stats, f, indent=2, sort_keys=True)

    def export_maze(self, filename: str) -> None:
        """Export the maze to a file in a simple text format using open wall pairs."""

        data = self._generate_maze_description()

        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".json")
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(data, f, indent=2, sort_keys=True)

    @classmethod
    def load(cls, filename: str):
        """Load a maze from a file with open wall pairs."""
        path = Path(filename)
        if not path.suffix:
            path = path.with_suffix(".json")
        if not path.exists():
            raise FileNotFoundError(f"File {filename} does not exist.")

        with open(path, "r") as f:
            data = json.load(f)

        maze_interface = cls(
            data["width"], data["height"], silent=True, skip_generate=True
        )

        # Open walls using Maze.open_wall
        for pair in data["open_walls"]:
            (r1, c1), (r2, c2) = pair
            cell1 = maze_interface.maze[r1, c1]
            cell2 = maze_interface.maze[r2, c2]
            Maze.open_wall(cell1, cell2)

        # Restore cherry position
        maze_interface._set_cherry_location(*data["cherry"])

        # Recompute shortest path
        maze_interface.shortest_path, _ = dijkstra(
            maze_interface.maze,
            maze_interface.maze.start_cell,
            maze_interface.maze.end_cell,
        )

        return maze_interface
