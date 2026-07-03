# 20x20 Maze A* Comparison

This project compares normal grid-based A* with compressed graph A* on generated
20x20 mazes. The maze is generated with a randomized DFS-style maze generator,
so each generated maze has a connected route from the start to the end.

## Graph Model

A 20x20 maze is modeled as a graph `G = (V, E)`.

- Each passable cell is a node in `V`.
- Each up, down, left, or right connection between passable cells is an edge in
  `E`.
- Every edge has weight `1`.
- A path length is the sum of its edge weights.
- A* uses the Manhattan distance heuristic:
  `h(a, b) = |a.row - b.row| + |a.col - b.col|`.

The compressed graph `G'` keeps only important nodes: the start, the end,
junctions, dead ends, and, depending on the mode, turn points. A straight or
choice-free corridor between two important nodes is replaced by one weighted
edge. If the compression is correct, the shortest path length in `G'` must stay
equal to the shortest path length in `G`.

## Implementation Notes

- The 20x20 maze is stored as a two-dimensional array.
- A* uses a priority queue for its open set.
- The number of passable neighbors of each cell is used to decide whether that
  cell is an important compressed-graph node.
- Corridors between important nodes are compressed into weighted edges.
- Normal A* and compressed graph A* are run on the same maze.
- Searched node count, path length, graph size, and runtime metrics are saved to
  CSV.
- SVG files visualize the maze, shortest path, compressed graph nodes, and
  summary comparison chart.
- A seed value makes batch experiments reproducible.

## Symbols

- `0`: passable space
- `1`: wall
- `2`: start
- `3`: end

## Run

Generate one maze:

```powershell
python .\main.py generate
```

Compare one maze:

```powershell
python .\main.py compare --maze .\maze\oy43i1j73lkdfe1r.txt
```

Run a batch comparison:

```powershell
python .\main.py compare --runs 30 --seed 1578
```

Use the PDF-style node rule, which keeps turns as graph nodes:

```powershell
python .\main.py compare --runs 30 --seed 1578 --mode design
```

## Compression Modes

`optimized` mode compresses every degree-2 cell, including both straight corridor
cells and turn cells. This treats any no-choice sequence of cells as one weighted
edge and usually reduces the searched node count the most.

`design` mode keeps turn points as compressed graph nodes. This is easier to
explain visually and matches the first design idea, but it can create more graph
nodes than `optimized` mode.

The main experiment should usually use `optimized` mode. `design` mode is useful
for design explanation or a supporting experiment.

## Validation

Each comparison checks two correctness conditions:

- Both algorithms must find a path.
- The compressed graph A* path length must equal the normal A* path length.

If either condition fails, the experiment raises an error. This verifies that the
compressed graph preserves shortest path length.

## Runtime Metrics

The result CSV separates compressed graph construction time from search time:

- `normal_ms`: normal grid-based A* runtime.
- `compressed_ms`: old name kept for compatibility; same value as
  `compressed_search_ms`.
- `compressed_build_ms`: compressed graph construction time.
- `compressed_search_ms`: A* search time on the compressed graph.
- `compressed_total_ms`: `compressed_build_ms + compressed_search_ms`.

For a fair end-to-end runtime comparison, compare `normal_ms` with
`compressed_total_ms`. `compressed_search_ms` is still useful for analyzing how
fast the search becomes after the compressed graph already exists.

## Latest Result

The latest optimized 30-run batch kept every shortest path length equal while
reducing the average searched nodes from `77.27` to `6.97`. The average path
length stayed equal at `68.53`.

Compressed graph A* reduces the searched node count while preserving the same
shortest path length because it searches only the decision-relevant graph nodes
instead of every passable maze cell. This shows that graph compression can
improve search efficiency without changing shortest-path quality.

## Result Files

- `results/latest_summary.txt`: average results from the latest experiment.
- `results/latest_comparison.csv`: per-run searched node count, path length,
  graph size, and runtime details.
- `results/latest_maze.svg`: the latest maze with the shortest path and
  compressed graph nodes.
- `results/latest_comparison.svg`: a chart comparing average searched nodes and
  total runtime.
