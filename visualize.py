from __future__ import annotations

from maze import END, START, Coord, Grid, grid_to_text


PATH_MARK = "*"


def overlay_path(maze: Grid, path: list[Coord]) -> str:
    rendered = [row[:] for row in maze]

    for row, col in path:
        if rendered[row][col] not in {START, END}:
            rendered[row][col] = PATH_MARK

    return grid_to_text(rendered)


def write_path_preview(maze: Grid, path: list[Coord], target) -> None:
    target.write_text(overlay_path(maze, path), encoding="utf-8")
