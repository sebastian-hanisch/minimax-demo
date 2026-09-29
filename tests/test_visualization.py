"""Regressionstest: scaleanchor + explizite range friert den Bereich beim ersten
Zeichnen anhand der Containerbreite ein (Karte/Brett wird winzig) - echter Fund
beim Bau, im echten Browser sichtbar, von AppTest nicht erkannt. Fix:
autorange=True + unsichtbare Eckmarker statt expliziter range.
"""

from mm_game import empty_board
from mm_visualization import board_figure


def test_board_figure_uses_autorange_not_explicit_range():
    board = empty_board(4, 3)
    fig = board_figure(board, None, None, [0, 1, 2])
    assert fig.layout.xaxis.autorange is True
    assert fig.layout.xaxis.range is None
    assert fig.layout.yaxis.autorange is True
    assert fig.layout.yaxis.range is None


def test_board_figure_has_corner_anchor_points_covering_full_board():
    rows, cols = 4, 3
    board = empty_board(rows, cols)
    fig = board_figure(board, None, None, None)
    anchor_trace = fig.data[-1]
    assert min(anchor_trace.x) <= -0.7
    assert max(anchor_trace.x) >= cols - 0.3
    assert min(anchor_trace.y) <= -0.7
    assert max(anchor_trace.y) >= rows + 0.9


def test_board_figure_cell_count_matches_board_size():
    board = empty_board(3, 4)
    fig = board_figure(board, None, None, None)
    cell_trace = fig.data[0]
    assert len(cell_trace.x) == 3 * 4
