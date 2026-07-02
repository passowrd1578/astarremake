# 20x20 Maze A* Comparison

This project compares normal grid-based A* with compressed graph A* on generated
20x20 mazes.

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

## Latest Result

The latest 30-run batch kept every shortest path length equal while reducing
the average searched nodes from `77.27` to `25.80`.

See:

- `results/latest_summary.txt`
- `results/latest_comparison.csv`
