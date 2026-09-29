"""Kennzahlen und Verdikt-Texte rund um eine gelöste Position."""

from __future__ import annotations

from mm_constants import BRANCHING_VS_DEPTH_PAIR, MEASURED_EXPLOSION, PLAYER_NAMES, PLAYER_ONE, PLAYER_TWO
from mm_minimax import SolveResult


def value_verdict(value: int) -> str:
    if value == 0:
        return "Bei perfektem Spiel beider Seiten endet diese Position remis."
    winner = PLAYER_ONE if value > 0 else PLAYER_TWO
    return f"Bei perfektem Spiel beider Seiten gewinnt {PLAYER_NAMES[winner]}."


def to_move_verdict(result: SolveResult, player_to_move: int) -> str:
    """Verdikt aus Sicht des Spielers, der gerade am Zug ist."""
    outcome_for_mover = result.value if player_to_move == PLAYER_ONE else -result.value
    name = PLAYER_NAMES[player_to_move]
    if outcome_for_mover == 0:
        return f"{name} kann das Remis erzwingen, aber nicht mehr gewinnen."
    if outcome_for_mover > 0:
        return f"{name} kann den Sieg erzwingen."
    return f"{name} verliert bei perfektem Gegenspiel - jeder Zug ist gleich schlecht."


def explosion_growth_factor() -> float:
    """Wie viel mehr Knoten braucht das größte gemessene Brett gegenüber 3x3."""
    small = next(e for e in MEASURED_EXPLOSION if (e["rows"], e["cols"]) == (3, 3))
    large = max(MEASURED_EXPLOSION, key=lambda e: e["nodes"])
    return large["nodes"] / small["nodes"]


def branching_vs_depth_factor() -> float:
    """4x3 und 3x4 haben beide 12 Felder - wie viel mehr Knoten braucht 3x4?"""
    fewer_cols, more_cols = BRANCHING_VS_DEPTH_PAIR
    return more_cols["nodes"] / fewer_cols["nodes"]


def format_de_number(value: float, decimals: int = 0) -> str:
    """Deutsches Tausendertrennzeichen NUR für diese Zahl.

    Bewusst kein `.replace(",", ".")` auf einem ganzen Satz - das würde auch
    echte Satzkommas in Text daneben kaputtmachen (realer Fund beim Bau: "3×4,
    mehr Spalten" wurde so zu "3×4. mehr Spalten").
    """
    return f"{value:,.{decimals}f}".replace(",", ".")
