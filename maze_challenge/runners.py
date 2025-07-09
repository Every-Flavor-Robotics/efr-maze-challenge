import importlib.util
import time

import click

from .maze_interface import MazeInterface
from .solver import Solver

# Parameters for the competition
# - Width and height of the maze
WIDTH = 20
HEIGHT = 20
# - Maximum number of moves allowed
MAX_MOVES = 2000


def average_stats(stats: list[dict]) -> dict:
    """Calculate the average of the stats from multiple runs."""
    if not stats:
        return {}

    total = {key: 0 for key in stats[0].keys()}
    for stat in stats:
        for key, value in stat.items():
            total[key] += value

    average = {key: value / len(stats) for key, value in total.items()}
    return average


def run_solver(solver: Solver, fast: bool) -> None:

    # Confirm solver is the correct type
    if not issubclass(solver, Solver):
        raise TypeError("The solver must be an instance of the Solver class.")

    maze_interface = MazeInterface(WIDTH, HEIGHT)

    sleep = 0.005 if fast else 0.2

    solver = solver(maze_interface.width, maze_interface.height)

    for _ in range(MAX_MOVES):
        # Get the current position of the agent
        position = maze_interface.get_position()

        possible_moves = maze_interface.get_possible_moves()

        direction = solver.choose_move(position, possible_moves)

        maze_interface.move(direction)

        maze_interface.draw()

        if maze_interface.completed():
            break

        time.sleep(sleep)

    maze_interface.print_final_stats()
    maze_interface.export_stats("stats.json")


@click.command()
@click.option(
    "--solver",
    type=click.Path(),
    help="Path to the solver module to use.",
    default="solver.py",
)
@click.option(
    "--fast",
    is_flag=True,
    help="Run the maze solver in fast mode (speed up animation).",
    default=False,
)
def main(solver, fast) -> None:
    """Entry point for the 'labyrinth' and 'maze' programs."""

    run_maze(solver, fast)


if __name__ == "__main__":
    main()
    main()
