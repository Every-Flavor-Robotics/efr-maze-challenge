"""Entry point for the labyrinth program."""

import importlib.util
import time

import click

from maze_interface import MazeInterface

# Parameters for the competition
# - Width and height of the maze
WIDTH = 20
HEIGHT = 20
# - Maximum number of moves allowed
MAX_MOVES = 2000


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

    maze_interface = MazeInterface(WIDTH, HEIGHT)

    maze_interface.draw()

    sleep = 0.005 if fast else 0.2

    # Import the solver dynamically
    # Append .py to the solver path if not provided
    if not solver.endswith(".py"):
        solver += ".py"

    spec = importlib.util.spec_from_file_location("Solver", solver)
    solver_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solver_module)

    solver = solver_module.Solver(maze_interface.width, maze_interface.height)

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


if __name__ == "__main__":
    main()
