from __future__ import annotations

import secrets
import string
from pathlib import Path


WIDTH = 20
HEIGHT = 20

WALL = "1"
PATH = "0"
START = "2"
END = "3"

NAME_LENGTH = 16
NAME_CHARS = string.ascii_lowercase + string.digits


def make_unique_filename(directory: Path) -> Path:
    while True:
        name = "".join(secrets.choice(NAME_CHARS) for _ in range(NAME_LENGTH))
        path = directory / f"{name}.txt"
        if not path.exists():
            return path


def generate_maze() -> list[list[str]]:
    maze = [[WALL for _ in range(WIDTH)] for _ in range(HEIGHT)]
    start = (1, 1)
    end = (HEIGHT - 3, WIDTH - 3)
    stack = [start]
    visited = {start}
    maze[start[0]][start[1]] = PATH

    while stack:
        row, col = stack[-1]
        neighbors = []

        for dr, dc in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            next_row = row + dr
            next_col = col + dc

            if (
                1 <= next_row < HEIGHT - 1
                and 1 <= next_col < WIDTH - 1
                and (next_row, next_col) not in visited
            ):
                neighbors.append((next_row, next_col, dr // 2, dc // 2))

        if not neighbors:
            stack.pop()
            continue

        next_row, next_col, wall_dr, wall_dc = secrets.choice(neighbors)
        maze[row + wall_dr][col + wall_dc] = PATH
        maze[next_row][next_col] = PATH
        visited.add((next_row, next_col))
        stack.append((next_row, next_col))

    maze[start[0]][start[1]] = START
    maze[end[0]][end[1]] = END
    return maze


def save_maze(maze: list[list[str]]) -> Path:
    maze_dir = Path(__file__).resolve().parent / "maze"
    maze_dir.mkdir(exist_ok=True)

    path = make_unique_filename(maze_dir)
    text = "\n".join("".join(row) for row in maze)
    path.write_text(text, encoding="utf-8")
    return path


def main() -> None:
    path = save_maze(generate_maze())
    print(f"Saved maze: {path}")


if __name__ == "__main__":
    main()
