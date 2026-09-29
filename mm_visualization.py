"""Plotly-Figuren: Brett-Darstellung und Explosions-Diagramm (alle Achsen fest)."""

from __future__ import annotations

import plotly.graph_objects as go

from mm_constants import EMPTY, EMPTY_COLOUR, MEASURED_EXPLOSION, PLAYER_COLOURS
from mm_game import winning_line


def board_figure(
    board: list[list[int]],
    last_move,
    winner: int | None,
    best_columns: list[int] | None = None,
) -> go.Figure:
    rows, cols = len(board), len(board[0])
    fig = go.Figure()

    win_cells = set()
    if winner is not None and last_move is not None:
        line = winning_line(board, last_move, winner)
        if line:
            win_cells = set(line)

    xs, ys, colours, line_widths, line_colours = [], [], [], [], []
    for r in range(rows):
        for c in range(cols):
            value = board[r][c]
            xs.append(c)
            ys.append(rows - 1 - r)
            colours.append(EMPTY_COLOUR if value == EMPTY else PLAYER_COLOURS[value])
            if (r, c) in win_cells:
                line_widths.append(4)
                line_colours.append("#1a1a1a")
            else:
                line_widths.append(1)
                line_colours.append("#9a9a9a")

    fig.add_trace(
        go.Scatter(
            x=xs,
            y=ys,
            mode="markers",
            marker=dict(
                size=46,
                color=colours,
                line=dict(width=line_widths, color=line_colours),
            ),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    if best_columns:
        fig.add_trace(
            go.Scatter(
                x=list(best_columns),
                y=[rows + 0.35] * len(best_columns),
                mode="markers",
                marker=dict(size=16, color="#2ca02c", symbol="triangle-down"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # scaleanchor + eine EXPLIZITE range friert den Bereich beim ersten Zeichnen
    # anhand der (zu diesem Zeitpunkt noch schmalen) Containerbreite ein, nicht
    # anhand der Daten - Karte/Brett wird winzig. Stattdessen: autorange plus
    # zwei unsichtbare Eckmarker, die den gewünschten Bereich über die Daten
    # selbst erzwingen (siehe feedback_plotly_scaleanchor_explicit_range).
    fig.add_trace(
        go.Scatter(
            x=[-0.7, cols - 0.3],
            y=[-0.7, rows + 0.9],
            mode="markers",
            marker=dict(size=1, color="rgba(0,0,0,0)"),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.update_xaxes(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        fixedrange=True,
    )
    fig.update_yaxes(
        autorange=True,
        showgrid=False,
        zeroline=False,
        showticklabels=False,
        fixedrange=True,
        scaleanchor="x",
        scaleratio=1,
    )
    fig.update_layout(
        height=110 * rows + 140,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="#f7f7f7",
    )
    return fig


def explosion_figure(highlight: tuple[int, int] | None = None) -> go.Figure:
    labels = [f"{e['rows']}×{e['cols']}" for e in MEASURED_EXPLOSION]
    nodes = [e["nodes"] for e in MEASURED_EXPLOSION]
    colours = [
        "#2ca02c" if (e["rows"], e["cols"]) == highlight else ("#1f77b4" if e["live"] else "#9a9a9a")
        for e in MEASURED_EXPLOSION
    ]
    texts = [f"{n:,}".replace(",", ".") for n in nodes]

    fig = go.Figure(
        go.Bar(x=labels, y=nodes, marker_color=colours, text=texts, textposition="outside")
    )
    fig.update_yaxes(type="log", title="Suchknoten (log-Skala)", fixedrange=True)
    fig.update_xaxes(title="Brettgröße (Zeilen × Spalten)", fixedrange=True)
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=30, b=10))
    return fig
