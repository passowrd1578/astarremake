from __future__ import annotations

from pathlib import Path
from time import perf_counter

from astar import astar_search
from cga_star import compressed_astar_search
from compressed_graph import build_compressed_graph
from maze import END, START, Grid, find_symbol, load_maze
from visualize import overlay_path


RESULTS_DIR = Path(__file__).resolve().parent / "results"


def write_normal_report(maze_path: Path, output_path: Path | None = None) -> Path:
    maze = load_maze(maze_path)
    start = find_symbol(maze, START)
    goal = find_symbol(maze, END)
    result = astar_search(maze, start, goal)

    report = _format_report(
        title="Normal A* result",
        maze=maze,
        path=result.path,
        lines=[
            ("Maze file", str(maze_path)),
            ("Start", str(start)),
            ("Goal", str(goal)),
            ("Found path", str(result.found)),
            ("Path length", str(result.path_length)),
            ("Visited nodes", str(result.visited_count)),
            ("Elapsed ms", f"{result.elapsed_ms:.4f}"),
        ],
    )
    return _write_report(report, output_path or RESULTS_DIR / "latest_normal_result.txt")


def write_cga_report(
    maze_path: Path,
    compression_mode: str = "optimized",
    output_path: Path | None = None,
) -> Path:
    maze = load_maze(maze_path)
    start = find_symbol(maze, START)
    goal = find_symbol(maze, END)

    build_started = perf_counter()
    graph = build_compressed_graph(maze, include_turns=compression_mode == "design")
    build_ms = (perf_counter() - build_started) * 1000

    result = compressed_astar_search(graph, start, goal)
    total_ms = build_ms + result.elapsed_ms

    report = _format_report(
        title="CGA* result",
        maze=maze,
        path=result.path,
        lines=[
            ("Maze file", str(maze_path)),
            ("Mode", compression_mode),
            ("Start", str(start)),
            ("Goal", str(goal)),
            ("Found path", str(result.found)),
            ("Path length", str(result.path_length)),
            ("Visited nodes", str(result.visited_count)),
            ("Graph nodes", str(len(graph.nodes))),
            ("Graph edges", str(graph.edge_count)),
            ("Build ms", f"{build_ms:.4f}"),
            ("Search ms", f"{result.elapsed_ms:.4f}"),
            ("Elapsed ms", f"{total_ms:.4f}"),
        ],
    )
    return _write_report(report, output_path or RESULTS_DIR / "latest_cga_result.txt")


def _format_report(
    title: str,
    maze: Grid,
    path,
    lines: list[tuple[str, str]],
) -> str:
    separator = "=" * 64
    preview_separator = "-" * 64
    label_width = max(len(label) for label, _ in lines)
    body = [separator, title, separator]

    for label, value in lines:
        body.append(f"{label:<{label_width}} : {value}")

    body.extend(
        [
            separator,
            "Path preview (* = shortest path)",
            preview_separator,
            overlay_path(maze, path),
            separator,
        ]
    )
    return "\n".join(body) + "\n"


def _write_report(report: str, output_path: Path) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return output_path
