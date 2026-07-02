from __future__ import annotations

import random
import secrets
import string
from pathlib import Path


WIDTH = 20
HEIGHT = 20

PATH = "0"
WALL = "1"
START = "2"
END = "3"

PASSABLE = {PATH, START, END}
NAME_LENGTH = 16
NAME_CHARS = string.ascii_lowercase + string.digits

Coord = tuple[int, int]
Grid = list[list[str]]


def make_unique_filename(directory: Path) -> Path:
    while True:
        name = "".join(secrets.choice(NAME_CHARS) for _ in range(NAME_LENGTH))
        path = directory / f"{name}.txt"
        if not path.exists():
            return path


def generate_maze(
    width: int = WIDTH,
    height: int = HEIGHT,
    rng: random.Random | None = None,
) -> Grid:
    if width < 5 or height < 5:
        raise ValueError("Maze width and height must be at least 5.")

    rng = rng or random.SystemRandom()
    maze = [[WALL for _ in range(width)] for _ in range(height)]
    start = (1, 1)
    end = (_last_odd_inside(height), _last_odd_inside(width))
    stack = [start]
    visited = {start}
    maze[start[0]][start[1]] = PATH

    while stack:
        row, col = stack[-1]
        neighbors: list[tuple[int, int, int, int]] = []

        for dr, dc in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            next_row = row + dr
            next_col = col + dc

            if (
                1 <= next_row < height - 1
                and 1 <= next_col < width - 1
                and (next_row, next_col) not in visited
            ):
                neighbors.append((next_row, next_col, dr // 2, dc // 2))

        if not neighbors:
            stack.pop()
            continue

        next_row, next_col, wall_dr, wall_dc = rng.choice(neighbors)
        maze[row + wall_dr][col + wall_dc] = PATH
        maze[next_row][next_col] = PATH
        visited.add((next_row, next_col))
        stack.append((next_row, next_col))

    maze[start[0]][start[1]] = START
    maze[end[0]][end[1]] = END
    return maze


def _last_odd_inside(size: int) -> int:
    value = size - 2
    return value if value % 2 == 1 else value - 1


def save_maze(maze: Grid, directory: Path | None = None) -> Path:
    maze_dir = directory or Path(__file__).resolve().parent / "maze"
    maze_dir.mkdir(exist_ok=True)
    path = make_unique_filename(maze_dir)
    path.write_text(grid_to_text(maze), encoding="utf-8")
    return path


def load_maze(path: Path) -> Grid:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    if not lines:
        raise ValueError("Maze file is empty.")

    width = len(lines[0])
    if any(len(line) != width for line in lines):
        raise ValueError("Maze rows must have the same width.")

    maze = [list(line) for line in lines]
    validate_maze(maze)
    return maze


def validate_maze(maze: Grid) -> None:
    starts = sum(row.count(START) for row in maze)
    ends = sum(row.count(END) for row in maze)
    invalid = sorted({cell for row in maze for cell in row} - {PATH, WALL, START, END})

    if starts != 1:
        raise ValueError(f"Maze must contain exactly one start '{START}'.")
    if ends != 1:
        raise ValueError(f"Maze must contain exactly one end '{END}'.")
    if invalid:
        raise ValueError(f"Maze contains invalid symbols: {invalid}")


def find_symbol(maze: Grid, symbol: str) -> Coord:
    for row_index, row in enumerate(maze):
        for col_index, cell in enumerate(row):
            if cell == symbol:
                return row_index, col_index
    raise ValueError(f"Symbol not found: {symbol}")


def grid_to_text(maze: Grid) -> str:
    return "\n".join("".join(row) for row in maze)


def in_bounds(maze: Grid, coord: Coord) -> bool:
    row, col = coord
    return 0 <= row < len(maze) and 0 <= col < len(maze[0])


def is_passable(maze: Grid, coord: Coord) -> bool:
    row, col = coord
    return in_bounds(maze, coord) and maze[row][col] in PASSABLE


def passable_neighbors(maze: Grid, coord: Coord) -> list[Coord]:
    row, col = coord
    neighbors = []

    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        next_coord = (row + dr, col + dc)
        if is_passable(maze, next_coord):
            neighbors.append(next_coord)

    return neighbors
