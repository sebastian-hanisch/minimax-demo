"""Regressionstest: aufeinanderfolgende multi_cell-Aufrufe duerfen nicht crashen.

Echter Fund beim Bau: `multi_cell(w=0, ...)` laesst den Cursor per fpdf2-Default
am RECHTEN Rand stehen (anders als `cell`) - ohne `new_x=LMARGIN` rechnet der
naechste `multi_cell`-Aufruf mit 0 verbleibender Breite und wirft
`FPDFException("Not enough horizontal space to render a single character")`.
"""

from mm_constants import PLAYER_ONE, PLAYER_TWO
from mm_game import apply_move, empty_board
from mm_minimax import solve_position
from mm_pdf_export import build_pdf


def test_build_pdf_with_two_consecutive_multi_cells_does_not_crash():
    board = empty_board(3, 3)
    result = solve_position(board, PLAYER_ONE)
    pdf_bytes = build_pdf(3, 3, [], PLAYER_ONE, result)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500


def test_build_pdf_after_some_moves():
    board = empty_board(4, 3)
    apply_move(board, 0, PLAYER_ONE)
    apply_move(board, 1, PLAYER_TWO)
    result = solve_position(board, PLAYER_ONE)
    pdf_bytes = build_pdf(4, 3, [0, 1], PLAYER_ONE, result)
    assert pdf_bytes.startswith(b"%PDF")
