from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from time import perf_counter

from maze import Coord, Grid, passable_neighbors


@dataclass(frozen=True)
class AStarResult:
    found: bool
    path: list[Coord]
    visited_count: int
    elapsed_ms: float

    @property
    def path_length(self) -> int:
        return max(0, len(self.path) - 1)


def manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_search(maze: Grid, start: Coord, goal: Coord) -> AStarResult:
    started = perf_counter()
    open_heap: list[tuple[int, int, Coord]] = []
    heappush(open_heap, (manhattan(start, goal), 0, start))

    came_from: dict[Coord, Coord] = {}
    g_score = {start: 0}
    closed: set[Coord] = set()
    sequence = 1

    while open_heap:
        _, _, current = heappop(open_heap)
        if current in closed:
            continue

        closed.add(current)
        if current == goal:
            elapsed_ms = (perf_counter() - started) * 1000
            return AStarResult(True, reconstruct_path(came_from, current), len(closed), elapsed_ms)

        for neighbor in passable_neighbors(maze, current):
            if neighbor in closed:
                continue

            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, 1_000_000_000):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + manhattan(neighbor, goal)
                heappush(open_heap, (f_score, sequence, neighbor))
                sequence += 1

    elapsed_ms = (perf_counter() - started) * 1000
    return AStarResult(False, [], len(closed), elapsed_ms)


def reconstruct_path(came_from: dict[Coord, Coord], current: Coord) -> list[Coord]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
