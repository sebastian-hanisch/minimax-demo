"""Jede Zahl aus dem README wird hier gegen den tatsächlichen Code nachgerechnet.

Zeiten werden bewusst NICHT exakt geprüft (plattformabhängig) - nur Knotenzahlen
(deterministisch, ganzzahlig) und die daraus abgeleiteten Verhältnisse.
"""

import pytest

from mm_constants import MEASURED_EXPLOSION, PLAYER_ONE
from mm_evaluation import branching_vs_depth_factor, explosion_growth_factor, format_de_number
from mm_game import empty_board
from mm_minimax import solve_position


def test_format_de_number_does_not_touch_surrounding_text():
    # Echter Fund beim Bau: ein blankes `.replace(",", ".")` auf einem ganzen
    # Satz zerstörte auch echte Satzkommas ("3x4, mehr Spalten" -> "3x4. mehr
    # Spalten"). format_de_number formatiert NUR die Zahl.
    sentence = f"Das breitere Brett (3x4, mehr Spalten) hat {format_de_number(700_777)} Knoten."
    assert sentence == "Das breitere Brett (3x4, mehr Spalten) hat 700.777 Knoten."


def test_format_de_number_with_decimals():
    assert format_de_number(10.03, 1) == "10.0"


@pytest.mark.parametrize(
    "rows,cols,expected_nodes",
    [(3, 3, 3_568), (4, 3, 69_877), (3, 4, 700_777)],
)
def test_readme_node_counts_for_live_boards(rows, cols, expected_nodes):
    board = empty_board(rows, cols)
    result = solve_position(board, PLAYER_ONE)
    assert result.node_count == expected_nodes


def test_readme_explosion_growth_factor():
    assert explosion_growth_factor() == pytest.approx(23_282, rel=1e-3)


def test_readme_branching_vs_depth_factor():
    assert branching_vs_depth_factor() == pytest.approx(10.03, rel=1e-2)


def test_readme_all_measured_boards_are_draws():
    for entry in MEASURED_EXPLOSION:
        if not entry["live"]:
            continue
        board = empty_board(entry["rows"], entry["cols"])
        result = solve_position(board, PLAYER_ONE)
        assert result.value == 0


def test_readme_4x4_reference_point_is_flagged_not_live():
    entry = next(e for e in MEASURED_EXPLOSION if (e["rows"], e["cols"]) == (4, 4))
    assert entry["live"] is False
    assert entry["nodes"] == 83_078_201
