from __future__ import annotations

import argparse
from pathlib import Path

from compare import compare_maze, run_batch
from maze import generate_maze, save_maze


def main() -> None:
    parser = argparse.ArgumentParser(description="20x20 maze A* experiment runner.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("generate", help="Generate one 20x20 maze text file.")

    compare_parser = subparsers.add_parser("compare", help="Compare one maze file or a batch of generated mazes.")
    compare_parser.add_argument("--maze", type=Path, help="Existing maze file to compare.")
    compare_parser.add_argument("--runs", type=int, default=30, help="Batch size when --maze is not provided.")
    compare_parser.add_argument("--seed", type=int, default=1578, help="Base seed for repeatable batch generation.")

    args = parser.parse_args()

    if args.command == "generate":
        print(f"Saved maze: {save_maze(generate_maze())}")
    elif args.maze:
        print(compare_maze(args.maze))
    else:
        run_batch(args.runs, args.seed)
        print("Saved results/latest_summary.txt and results/latest_comparison.csv")


if __name__ == "__main__":
    main()
