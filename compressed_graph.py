from __future__ import annotations

from dataclasses import dataclass

from maze import Coord, Grid, END, START, find_symbol, is_passable, passable_neighbors


@dataclass(frozen=True)
class Edge:
    to: Coord
    cost: int
    path: tuple[Coord, ...]


@dataclass(frozen=True)
class CompressedGraph:
    nodes: frozenset[Coord]
    edges: dict[Coord, tuple[Edge, ...]]

    @property
    def edge_count(self) -> int:
        return sum(len(edges) for edges in self.edges.values())


def build_compressed_graph(maze: Grid, include_turns: bool = False) -> CompressedGraph:
    start = find_symbol(maze, START)
    goal = find_symbol(maze, END)
    nodes = _important_nodes(maze, start, goal, include_turns)
    edge_map: dict[Coord, dict[Coord, Edge]] = {node: {} for node in nodes}

    for node in nodes:
        for neighbor in passable_neighbors(maze, node):
            edge = _walk_until_node(maze, nodes, node, neighbor)
            if edge is None:
                continue

            current = edge_map[node].get(edge.to)
            if current is None or edge.cost < current.cost:
                edge_map[node][edge.to] = edge

    return CompressedGraph(
        nodes=frozenset(nodes),
        edges={node: tuple(edges.values()) for node, edges in edge_map.items()},
    )


def _important_nodes(maze: Grid, start: Coord, goal: Coord, include_turns: bool) -> set[Coord]:
    nodes = {start, goal}

    for row_index, row in enumerate(maze):
        for col_index, _ in enumerate(row):
            coord = (row_index, col_index)
            if not is_passable(maze, coord):
                continue

            neighbors = passable_neighbors(maze, coord)
            degree = len(neighbors)

            if degree != 2:
                nodes.add(coord)
            elif include_turns and _is_turn(coord, neighbors):
                nodes.add(coord)

    return nodes


def _is_turn(coord: Coord, neighbors: list[Coord]) -> bool:
    first, second = neighbors
    dr1 = first[0] - coord[0]
    dc1 = first[1] - coord[1]
    dr2 = second[0] - coord[0]
    dc2 = second[1] - coord[1]
    return (dr1 + dr2, dc1 + dc2) != (0, 0)


def _walk_until_node(
    maze: Grid,
    nodes: set[Coord],
    source: Coord,
    first_step: Coord,
) -> Edge | None:
    previous = source
    current = first_step
    path = [source, first_step]
    cost = 1

    while current not in nodes:
        if current in path[:-1]:
            return None

        next_steps = [coord for coord in passable_neighbors(maze, current) if coord != previous]
        if not next_steps:
            return None

        previous, current = current, next_steps[0]
        path.append(current)
        cost += 1

    return Edge(to=current, cost=cost, path=tuple(path))
