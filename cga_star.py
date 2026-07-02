from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from time import perf_counter

from astar import manhattan
from compressed_graph import CompressedGraph, Edge
from maze import Coord


@dataclass(frozen=True)
class CompressedAStarResult:
    found: bool
    path: list[Coord]
    graph_path: list[Coord]
    visited_count: int
    elapsed_ms: float

    @property
    def path_length(self) -> int:
        return max(0, len(self.path) - 1)


def compressed_astar_search(
    graph: CompressedGraph,
    start: Coord,
    goal: Coord,
) -> CompressedAStarResult:
    started = perf_counter()
    open_heap: list[tuple[int, int, Coord]] = []
    heappush(open_heap, (manhattan(start, goal), 0, start))

    came_from: dict[Coord, tuple[Coord, Edge]] = {}
    g_score = {start: 0}
    closed: set[Coord] = set()
    sequence = 1

    while open_heap:
        _, _, current = heappop(open_heap)
        if current in closed:
            continue

        closed.add(current)
        if current == goal:
            graph_path = _reconstruct_graph_path(came_from, current)
            full_path = _expand_path(came_from, graph_path)
            elapsed_ms = (perf_counter() - started) * 1000
            return CompressedAStarResult(True, full_path, graph_path, len(closed), elapsed_ms)

        for edge in graph.edges.get(current, ()):
            if edge.to in closed:
                continue

            tentative_g = g_score[current] + edge.cost
            if tentative_g < g_score.get(edge.to, 1_000_000_000):
                came_from[edge.to] = (current, edge)
                g_score[edge.to] = tentative_g
                f_score = tentative_g + manhattan(edge.to, goal)
                heappush(open_heap, (f_score, sequence, edge.to))
                sequence += 1

    elapsed_ms = (perf_counter() - started) * 1000
    return CompressedAStarResult(False, [], [], len(closed), elapsed_ms)


def _reconstruct_graph_path(came_from: dict[Coord, tuple[Coord, Edge]], current: Coord) -> list[Coord]:
    path = [current]
    while current in came_from:
        current = came_from[current][0]
        path.append(current)
    path.reverse()
    return path


def _expand_path(came_from: dict[Coord, tuple[Coord, Edge]], graph_path: list[Coord]) -> list[Coord]:
    if not graph_path:
        return []

    full_path = [graph_path[0]]
    for node in graph_path[1:]:
        _, edge = came_from[node]
        full_path.extend(edge.path[1:])
    return full_path
