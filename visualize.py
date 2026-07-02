from __future__ import annotations

from statistics import mean

from maze import END, PATH, START, WALL, Coord, Grid, grid_to_text


PATH_MARK = "*"


def overlay_path(maze: Grid, path: list[Coord]) -> str:
    rendered = [row[:] for row in maze]

    for row, col in path:
        if rendered[row][col] not in {START, END}:
            rendered[row][col] = PATH_MARK

    return grid_to_text(rendered)


def write_path_preview(maze: Grid, path: list[Coord], target) -> None:
    target.write_text(overlay_path(maze, path), encoding="utf-8")


def write_maze_svg(
    maze: Grid,
    path: list[Coord],
    graph_nodes: set[Coord],
    target,
    cell_size: int = 28,
) -> None:
    rows = len(maze)
    cols = len(maze[0])
    width = cols * cell_size
    height = rows * cell_size
    path_set = set(path)

    parts = [
        _svg_header(width, height, "Maze shortest path"),
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<rect width="{width}" height="{height}" fill="none" stroke="#cbd5e1"/>',
    ]

    wall_path = _cells_to_path(maze, {WALL}, cell_size)
    path_cells = _cells_to_path_from_set(path_set, cell_size)
    if wall_path:
        parts.append(f'<path d="{wall_path}" fill="#111827"/>')
    if path_cells:
        parts.append(f'<path d="{path_cells}" fill="#bfdbfe"/>')

    if len(path) >= 2:
        points = " ".join(
            f"{col * cell_size + cell_size / 2},{row * cell_size + cell_size / 2}"
            for row, col in path
        )
        parts.append(
            f'<polyline points="{points}" fill="none" stroke="#2563eb" '
            f'stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
        )

    for row, col in graph_nodes:
        if maze[row][col] not in {START, END}:
            cx = col * cell_size + cell_size / 2
            cy = row * cell_size + cell_size / 2
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="4" fill="#f97316"/>')

    _append_label(parts, maze, START, "S", cell_size)
    _append_label(parts, maze, END, "E", cell_size)
    parts.append("</svg>")
    target.write_text("\n".join(parts), encoding="utf-8")


def write_comparison_svg(rows, target) -> None:
    avg_normal_visited = mean(row.normal_visited for row in rows)
    avg_compressed_visited = mean(row.compressed_visited for row in rows)
    avg_normal_ms = mean(row.normal_ms for row in rows)
    avg_compressed_ms = mean(row.compressed_ms for row in rows)
    visited_reduction = (avg_normal_visited - avg_compressed_visited) / avg_normal_visited * 100
    time_reduction = (avg_normal_ms - avg_compressed_ms) / avg_normal_ms * 100

    width = 760
    height = 420
    parts = [
        _svg_header(width, height, "A star comparison chart"),
        f'<rect width="{width}" height="{height}" rx="8" fill="#f8fafc"/>',
        '<text x="32" y="46" font-size="24" font-weight="700" fill="#0f172a">'
        "A* comparison</text>",
        f'<text x="32" y="74" font-size="14" fill="#475569">runs: {len(rows)} | '
        f'mode: {rows[0].compression_mode} | paths equal: '
        f'{str(all(row.path_delta == 0 for row in rows)).lower()}</text>',
    ]

    _append_bar_group(
        parts,
        x=70,
        y=130,
        title="Average searched nodes",
        normal=avg_normal_visited,
        compressed=avg_compressed_visited,
        unit="nodes",
        reduction=visited_reduction,
        max_value=avg_normal_visited,
    )
    _append_bar_group(
        parts,
        x=410,
        y=130,
        title="Average runtime",
        normal=avg_normal_ms,
        compressed=avg_compressed_ms,
        unit="ms",
        reduction=time_reduction,
        max_value=avg_normal_ms,
    )

    parts.append("</svg>")
    target.write_text("\n".join(parts), encoding="utf-8")


def _svg_header(width: int, height: int, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{title}">'
    )


def _cells_to_path(maze: Grid, symbols: set[str], cell_size: int) -> str:
    cells = {
        (row_index, col_index)
        for row_index, row in enumerate(maze)
        for col_index, cell in enumerate(row)
        if cell in symbols
    }
    return _cells_to_path_from_set(cells, cell_size)


def _cells_to_path_from_set(cells: set[Coord], cell_size: int) -> str:
    return " ".join(
        f"M{col * cell_size},{row * cell_size}h{cell_size}v{cell_size}h-{cell_size}z"
        for row, col in sorted(cells)
    )


def _append_label(parts: list[str], maze: Grid, symbol: str, label: str, cell_size: int) -> None:
    for row_index, row in enumerate(maze):
        for col_index, cell in enumerate(row):
            if cell == symbol:
                x = col_index * cell_size + cell_size / 2
                y = row_index * cell_size + cell_size / 2 + 5
                fill = "#22c55e" if symbol == START else "#ef4444"
                parts.append(
                    f'<circle cx="{x}" cy="{y - 5}" r="{cell_size / 2 - 3}" fill="{fill}"/>'
                )
                parts.append(
                    f'<text x="{x}" y="{y}" text-anchor="middle" font-size="16" '
                    f'font-weight="700" fill="#ffffff">{label}</text>'
                )
                return


def _append_bar_group(
    parts: list[str],
    x: int,
    y: int,
    title: str,
    normal: float,
    compressed: float,
    unit: str,
    reduction: float,
    max_value: float,
) -> None:
    chart_height = 190
    bar_width = 72
    gap = 28
    normal_height = chart_height * normal / max_value
    compressed_height = chart_height * compressed / max_value
    baseline = y + chart_height

    parts.append(f'<text x="{x}" y="{y - 24}" font-size="17" font-weight="700" fill="#0f172a">{title}</text>')
    parts.append(f'<line x1="{x - 8}" y1="{baseline}" x2="{x + 210}" y2="{baseline}" stroke="#94a3b8"/>')
    _append_bar(parts, x, baseline, bar_width, normal_height, "#64748b", "Normal", normal, unit)
    _append_bar(
        parts,
        x + bar_width + gap,
        baseline,
        bar_width,
        compressed_height,
        "#2563eb",
        "Compressed",
        compressed,
        unit,
    )
    parts.append(
        f'<text x="{x}" y="{baseline + 58}" font-size="14" font-weight="700" fill="#16a34a">'
        f'reduction {reduction:.2f}%</text>'
    )


def _append_bar(
    parts: list[str],
    x: int,
    baseline: int,
    width: int,
    height: float,
    color: str,
    label: str,
    value: float,
    unit: str,
) -> None:
    top = baseline - height
    parts.append(f'<rect x="{x}" y="{top:.2f}" width="{width}" height="{height:.2f}" fill="{color}"/>')
    parts.append(
        f'<text x="{x + width / 2}" y="{top - 8:.2f}" text-anchor="middle" '
        f'font-size="13" fill="#0f172a">{value:.2f}</text>'
    )
    parts.append(
        f'<text x="{x + width / 2}" y="{baseline + 22}" text-anchor="middle" '
        f'font-size="12" fill="#475569">{label}</text>'
    )
    parts.append(
        f'<text x="{x + width / 2}" y="{baseline + 38}" text-anchor="middle" '
        f'font-size="11" fill="#64748b">{unit}</text>'
    )
