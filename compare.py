from __future__ import annotations

import argparse
import csv
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean

from astar import astar_search
from cga_star import compressed_astar_search
from compressed_graph import build_compressed_graph
from maze import END, START, find_symbol, generate_maze, load_maze, save_maze
from visualize import write_path_preview


RESULTS_DIR = Path(__file__).resolve().parent / "results"
PROJECT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ComparisonRow:
    run: int
    maze_file: str
    normal_found: bool
    compressed_found: bool
    normal_visited: int
    compressed_visited: int
    normal_path_length: int
    compressed_path_length: int
    normal_ms: float
    compressed_ms: float
    compressed_nodes: int
    compressed_edges: int
    visited_reduction_percent: float
    time_reduction_percent: float
    path_delta: int


def compare_maze(maze_path: Path | None = None, run: int = 1, seed: int | None = None) -> ComparisonRow:
    rng = random.Random(seed) if seed is not None else None
    maze = load_maze(maze_path) if maze_path else generate_maze(rng=rng)
    saved_path = maze_path or save_maze(maze)
    start = find_symbol(maze, START)
    goal = find_symbol(maze, END)

    normal = astar_search(maze, start, goal)
    graph = build_compressed_graph(maze)
    compressed = compressed_astar_search(graph, start, goal)

    _validate_results(normal.found, compressed.found, normal.path_length, compressed.path_length)

    RESULTS_DIR.mkdir(exist_ok=True)
    preview_path = RESULTS_DIR / f"{saved_path.stem}_path.txt"
    write_path_preview(maze, compressed.path, preview_path)

    return ComparisonRow(
        run=run,
        maze_file=_display_path(saved_path),
        normal_found=normal.found,
        compressed_found=compressed.found,
        normal_visited=normal.visited_count,
        compressed_visited=compressed.visited_count,
        normal_path_length=normal.path_length,
        compressed_path_length=compressed.path_length,
        normal_ms=round(normal.elapsed_ms, 4),
        compressed_ms=round(compressed.elapsed_ms, 4),
        compressed_nodes=len(graph.nodes),
        compressed_edges=graph.edge_count,
        visited_reduction_percent=_reduction(normal.visited_count, compressed.visited_count),
        time_reduction_percent=_reduction(normal.elapsed_ms, compressed.elapsed_ms),
        path_delta=compressed.path_length - normal.path_length,
    )


def run_batch(runs: int = 30, seed: int = 1578) -> list[ComparisonRow]:
    rows = []
    for run in range(1, runs + 1):
        rows.append(compare_maze(run=run, seed=seed + run))

    RESULTS_DIR.mkdir(exist_ok=True)
    csv_path = RESULTS_DIR / "latest_comparison.csv"
    summary_path = RESULTS_DIR / "latest_summary.txt"
    _write_csv(rows, csv_path)
    _write_summary(rows, summary_path)
    return rows


def _validate_results(
    normal_found: bool,
    compressed_found: bool,
    normal_path_length: int,
    compressed_path_length: int,
) -> None:
    if not normal_found or not compressed_found:
        raise RuntimeError("Both algorithms must find a path.")
    if normal_path_length != compressed_path_length:
        raise RuntimeError(
            "Compressed graph A* must preserve shortest path length: "
            f"normal={normal_path_length}, compressed={compressed_path_length}"
        )


def _reduction(before: float, after: float) -> float:
    if before == 0:
        return 0.0
    return round((before - after) / before * 100, 2)


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_DIR))
    except ValueError:
        return str(path)


def _write_csv(rows: list[ComparisonRow], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def _write_summary(rows: list[ComparisonRow], path: Path) -> None:
    lines = [
        "Compressed Graph A* Comparison Summary",
        f"runs: {len(rows)}",
        f"avg_normal_visited: {mean(row.normal_visited for row in rows):.2f}",
        f"avg_compressed_visited: {mean(row.compressed_visited for row in rows):.2f}",
        f"avg_visited_reduction_percent: {mean(row.visited_reduction_percent for row in rows):.2f}",
        f"avg_normal_path_length: {mean(row.normal_path_length for row in rows):.2f}",
        f"avg_compressed_path_length: {mean(row.compressed_path_length for row in rows):.2f}",
        f"avg_normal_ms: {mean(row.normal_ms for row in rows):.4f}",
        f"avg_compressed_ms: {mean(row.compressed_ms for row in rows):.4f}",
        f"avg_time_reduction_percent: {mean(row.time_reduction_percent for row in rows):.2f}",
        f"all_path_lengths_equal: {all(row.path_delta == 0 for row in rows)}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare normal A* and compressed graph A*.")
    parser.add_argument("--runs", type=int, default=30, help="Number of generated mazes to compare.")
    parser.add_argument("--seed", type=int, default=1578, help="Base seed for repeatable generated mazes.")
    args = parser.parse_args()

    rows = run_batch(args.runs, args.seed)
    summary = RESULTS_DIR / "latest_summary.txt"
    print(summary.read_text(encoding="utf-8"))
    print(f"Saved detailed CSV: {RESULTS_DIR / 'latest_comparison.csv'}")
    print(f"Best node reduction: {max(row.visited_reduction_percent for row in rows):.2f}%")


if __name__ == "__main__":
    main()
