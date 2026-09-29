"""PDF-Export der aktuellen Positions-Analyse (fpdf2)."""

from __future__ import annotations

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from mm_constants import PLAYER_NAMES
from mm_evaluation import format_de_number, to_move_verdict, value_verdict
from mm_minimax import SolveResult

_NEXT_LINE = dict(new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_pdf(
    rows: int,
    cols: int,
    moves: list[int],
    player_to_move: int,
    result: SolveResult,
) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Minimax - Analyse der aktuellen Stellung", **_NEXT_LINE)

    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Brett: {rows} Zeilen x {cols} Spalten", **_NEXT_LINE)
    move_text = ", ".join(str(m) for m in moves) if moves else "keine (Startstellung)"
    pdf.cell(0, 8, f"Bisherige Züge (Spalten): {move_text}", **_NEXT_LINE)
    pdf.cell(0, 8, f"Am Zug: {PLAYER_NAMES[player_to_move]}", **_NEXT_LINE)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Ergebnis der erschöpfenden Suche", **_NEXT_LINE)
    pdf.set_font("Helvetica", "", 12)
    # multi_cell lässt den Cursor per Default am RECHTEN Rand stehen (anders als
    # cell) - ohne new_x=LMARGIN würde der nächste multi_cell-Aufruf mit einer
    # verbleibenden Breite von 0 rechnen und abstürzen (echter Fund, siehe Test).
    pdf.multi_cell(0, 8, value_verdict(result.value), **_NEXT_LINE)
    pdf.multi_cell(0, 8, to_move_verdict(result, player_to_move), **_NEXT_LINE)
    pdf.cell(0, 8, f"Durchsuchte Knoten: {format_de_number(result.node_count)}", **_NEXT_LINE)
    best_cols = ", ".join(str(c) for c in result.best_columns)
    pdf.cell(0, 8, f"Optimale Spalte(n): {best_cols}", **_NEXT_LINE)

    return bytes(pdf.output())
