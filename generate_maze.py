from maze import generate_maze, save_maze


def main() -> None:
    path = save_maze(generate_maze())
    print(f"Saved maze: {path}")


if __name__ == "__main__":
    main()
