from maze_challenge import MazeInterface


def generate_level_1():
    """Generate a 3 level 1 mazes."""

    for i in range(3):
        maze_interface = MazeInterface(5, 5, silent=True)

        # Save the maze to a file
        maze_interface.export_maze(f"assets/level_1_mazes/maze_{i + 1}.txt")


if __name__ == "__main__":
    generate_level_1()
    print("Level 1 mazes generated successfully!")
    print("You can find them in the assets/level_1_mazes directory.")
