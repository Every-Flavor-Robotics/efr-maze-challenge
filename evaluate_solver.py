"""Entry point for the labyrinth program."""

import importlib.util
import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import click
from tqdm import tqdm

from maze_interface import MazeInterface

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


def run_sample(solver: str) -> None:
    """Entry point for the 'labyrinth' and 'maze' programs."""

    # Import the solver dynamically
    spec = importlib.util.spec_from_file_location("Solver", solver)
    solver_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(solver_module)

    maze_interface = MazeInterface(WIDTH, HEIGHT, silent=True)

    solver = solver_module.Solver(maze_interface.width, maze_interface.height)

    for _ in range(MAX_MOVES):
        # Get the current position of the agent
        position = maze_interface.get_position()

        possible_moves = maze_interface.get_possible_moves()

        direction = solver.choose_move(position, possible_moves)

        maze_interface.move(direction)

        if maze_interface.completed():
            break

    return maze_interface.get_stats()


@click.command()
@click.option(
    "--solver",
    help="Name of the file containing the solver to test.",
    default="solver.py",
)
def main(solver: str):
    stats = []
    n = 20000
    start = time.time()

    print(f"🏁 Running Maze Solver for {n} mazes...")

    # Append .py to the solver if not already present
    solver_module_path = solver if solver.endswith(".py") else f"{solver}.py"

    # Confirm the file exists
    try:
        with open(solver_module_path, "r") as f:
            pass
    except FileNotFoundError:
        print(f"❌ Error: The solver file '{solver_module_path}' does not exist.")
        return

    try:
        spec = importlib.util.spec_from_file_location(
            "solver_module", solver_module_path
        )
        solver_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(solver_module)
    except (FileNotFoundError, AttributeError, ImportError, SyntaxError) as e:
        print(f"❌ Error loading solver module '{solver_module_path}': {e}")
        return

    if not hasattr(solver_module, "Solver"):
        print(
            f"❌ Error: The solver module '{solver_module_path}' does not define a Solver class."
        )
        return

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(run_sample, solver_module_path) for _ in range(n)]

        for f in tqdm(
            as_completed(futures), total=n, desc="Running Samples", unit="sample"
        ):
            stats.append(f.result())

    end = time.time()
    average = average_stats(stats)

    print(f"\n📊 Average Stats Over {n} Runs")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for key, value in average.items():
        if isinstance(value, float):
            print(f"{key.replace('_', ' ').capitalize():<25}: {value:.2f}")
        else:
            print(f"{key.replace('_', ' ').capitalize():<25}: {value}")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"🕒  Completed in {end - start:.2f} seconds")


if __name__ == "__main__":
    main()
