"""Entry point for the labyrinth program."""

import multiprocessing
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import click
from tqdm import tqdm

from maze_interface import MazeInterface
from solver import Solver

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


def run_sample() -> None:
    """Entry point for the 'labyrinth' and 'maze' programs."""

    maze_interface = MazeInterface(WIDTH, HEIGHT, silent=True)

    solver = Solver(maze_interface.width, maze_interface.height)

    for _ in range(MAX_MOVES):
        # Get the current position of the agent
        position = maze_interface.get_position()

        possible_moves = maze_interface.get_possible_moves()

        direction = solver.choose_move(position, possible_moves)

        maze_interface.move(direction)

        if maze_interface.completed():
            break

    return maze_interface.get_stats()


def main():
    print("🏁 Running Maze Solver on 10,000 Mazes in Parallel...\n")

    stats = []
    n = 10000
    start = time.time()

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        futures = [executor.submit(run_sample) for _ in range(n)]

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
