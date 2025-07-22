import multiprocessing
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import matplotlib
from tqdm import tqdm

from .maze_interface import MazeInterface
from .solver import Solver

# Parameters for the competition
# - Width and height of the maze
WIDTH = 20
HEIGHT = 20
# - Maximum number of moves allowed
MAX_MOVES = 2000


def safe_matplotlib_backend():
    if not os.environ.get("DISPLAY") and sys.platform != "win32":
        matplotlib.use("Agg")  # Use non-interactive backend


def run_solver(
    solver_class: Solver, fast: bool, use_ascii: bool = False, maze_file: str = None
) -> None:
    # Confirm solver is the correct type
    if not issubclass(solver_class, Solver):
        raise TypeError("The solver must be an instance of the Solver class.")

    maze_interface = None
    if maze_file is not None:
        # Confirm that the maze file exists, this means user is providing a maze file
        maze_path = Path(maze_file)
        if not maze_path.exists():
            raise FileNotFoundError(f"The maze file '{maze_file}' does not exist.")

        maze_interface = MazeInterface.load(maze_path, use_ascii=use_ascii)

    else:
        maze_interface = MazeInterface(WIDTH, HEIGHT, use_ascii=use_ascii)

    sleep = 0.005 if fast else 0.2

    solver = solver_class(maze_interface.width, maze_interface.height)

    for _ in range(MAX_MOVES):
        # Get the current state variables
        position = maze_interface.get_position()
        cherry_position = maze_interface.get_cherry_location()
        possible_moves = maze_interface.get_possible_moves()

        direction = solver.choose_move(position, cherry_position, possible_moves)

        if direction == "":
            break

        maze_interface.move(direction)

        maze_interface.draw()

        if maze_interface.completed():
            break

        time.sleep(sleep)

    maze_interface.print_final_stats()


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


def run_sample(solver_class: Solver) -> None:
    """Entry point for the 'labyrinth' and 'maze' programs."""

    maze_interface = MazeInterface(WIDTH, HEIGHT, silent=True)

    solver = solver_class(maze_interface.width, maze_interface.height)

    for _ in range(MAX_MOVES):
        # Get the current position of the agent
        position = maze_interface.get_position()

        cherry_position = maze_interface.get_cherry_location()

        possible_moves = maze_interface.get_possible_moves()

        direction = solver.choose_move(position, cherry_position, possible_moves)

        if direction == "":
            break

        maze_interface.move(direction)

        if maze_interface.completed():
            break

    return maze_interface.get_stats()


def generate_plots(stats: list[dict]) -> None:
    """Generate plots from the stats of multiple runs."""

    # Generate histograms of the score, explorer score, number of moves, and visted cells
    import matplotlib.pyplot as plt

    score = [stat["score"] for stat in stats]
    explorer_score = [stat["explorer_score"] for stat in stats]
    num_moves = [stat["num_moves"] for stat in stats]
    visited_cells = [stat["visited_cells"] for stat in stats]

    plt.figure(figsize=(12, 8))
    plt.subplot(2, 2, 1)
    plt.hist(score, bins=20, color="blue", alpha=0.7)
    # xscale
    plt.xlim(0, 11000)
    plt.title("Score Distribution")
    plt.xlabel("Score")
    plt.ylabel("Frequency")

    plt.subplot(2, 2, 2)
    plt.hist(explorer_score, bins=20, color="green", alpha=0.7)
    plt.xlim(0, 5000)
    plt.title("Explorer Score Distribution")
    plt.xlabel("Explorer Score")
    plt.ylabel("Frequency")

    plt.subplot(2, 2, 3)
    plt.hist(num_moves, bins=20, color="red", alpha=0.7)
    plt.xlim(0, MAX_MOVES)
    plt.title("Number of Moves Distribution")
    plt.xlabel("Number of Moves")
    plt.ylabel("Frequency")

    plt.subplot(2, 2, 4)
    plt.hist(visited_cells, bins=20, color="purple", alpha=0.7)
    plt.xlim(0, WIDTH * HEIGHT)
    plt.title("Visited Cells Distribution")
    plt.xlabel("Visited Cells")
    plt.ylabel("Frequency")
    plt.tight_layout()

    plt.show()
    plt.close()


def evaluate_solver(solver_class: Solver, n: int = 5000) -> None:
    # Confirm solver is the correct type
    if not issubclass(solver_class, Solver):
        raise TypeError("The solver must be an instance of the Solver class.")

    stats = []

    start = time.time()

    print(f"🏁 Running Maze Solver for {n} mazes...")

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(run_sample, solver_class) for _ in range(n)]

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

    # Get index of the worst run
    best_run_index = max(range(len(stats)), key=lambda i: stats[i]["score"])
    worst_run_index = min(range(len(stats)), key=lambda i: stats[i]["score"])

    # Print worst run stats
    print(f"\n😱 Worst Run Stats (Run {worst_run_index + 1})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for key, value in stats[worst_run_index].items():
        if isinstance(value, float):
            print(f"{key.replace('_', ' ').capitalize():<25}: {value:.2f}")
        else:
            print(f"{key.replace('_', ' ').capitalize():<25}: {value}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Print best run stats
    print(f"\n🏆 Best Run Stats (Run {best_run_index + 1})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for key, value in stats[best_run_index].items():
        if isinstance(value, float):
            print(f"{key.replace('_', ' ').capitalize():<25}: {value:.2f}")
        else:
            print(f"{key.replace('_', ' ').capitalize():<25}: {value}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    generate_plots(stats)


# @click.command()
# @click.option(
#     "--solver",
#     type=click.Path(),
#     help="Path to the solver module to use.",
#     default="solver.py",
# )
# @click.option(
#     "--fast",
#     is_flag=True,
#     help="Run the maze solver in fast mode (speed up animation).",
#     default=False,
# )
# def main(solver, fast) -> None:
#     """Entry point for the 'labyrinth' and 'maze' programs."""

#     run_maze(solver, fast)


if __name__ == "__main__":
    main()
