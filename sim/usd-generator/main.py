import os
import pdb
import sys

import click
from pxr import Gf, Usd, UsdGeom

# Add repo root (2 levels up from this file) to sys.path
sys.path.append(os.path.abspath(os.path.join(__file__, "..", "..", "..")))
from maze_challenge import MazeInterface


@click.command()
@click.option(
    "--maze-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the maze file to convert to USD.",
    required=True,
)
def main(maze_file):
    """Convert a maze file to USD format."""

    # Confirm that the maze file exists
    if not os.path.isfile(maze_file):
        print(f"❌ Error: The maze file '{maze_file}' does not exist.")
        return

    # Load the maze from the JSON file
    maze = MazeInterface.load(maze_file)

    pdb.set_trace()

    stage = Usd.Stage.CreateNew("maze.usda")

    # Set up root
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    UsdGeom.SetStageMetersPerUnit(stage, 1.0)

    # Create the floor plane
    floor = UsdGeom.Mesh.Define(stage, "/World/Floor")
    floor.CreateExtentAttr([(-5, -5, 0), (5, 5, 0.1)])
    # (You could create a proper plane mesh here)

    # Maze parameters
    cell_size = 1.0
    wall_height = 1.0
    wall_thickness = 0.1

    for y, row in enumerate(maze):
        for x, val in enumerate(row):
            if val == 1:
                wall_path = f"/World/Wall_{x}_{y}"
                wall = UsdGeom.Cube.Define(stage, wall_path)
                wall.AddTranslateOp().Set(
                    Gf.Vec3f(x * cell_size, y * cell_size, wall_height / 2)
                )
                wall.AddScaleOp().Set(Gf.Vec3f(cell_size, cell_size, wall_height))

    # Save
    stage.GetRootLayer().Save()


if __name__ == "__main__":
    main()
    main()
    main()
    main()
