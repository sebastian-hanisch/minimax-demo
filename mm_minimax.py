"""Erschöpfende Minimax-Suche (Wurzel-Stück: bewusst OHNE Alpha-Beta-Pruning -
das ist der Gegenstand des Kind-Stücks `alpha-beta-demo`).

Der Spielwert ist immer aus Sicht von PLAYER_ONE kodiert: +1 = Sieg Rot,
-1 = Sieg Gelb, 0 = Remis bei perfektem Spiel beider Seiten.
"""

from __future__ import annotations

from dataclasses import dataclass

from mm_constants import PLAYER_ONE
from mm_game import (
    apply_move,
    check_win_at,
    is_full,
    legal_columns,
    other_player,
    undo_move,
)


@dataclass
class NodeCounter:
    count: int = 0


@dataclass
class SolveResult:
    value: int
    move_values: dict[int, int]
    node_count: int
    best_columns: list[int]


def solve_position(board: list[list[int]], player: int, counter: NodeCounter | None = None) -> SolveResult:
    """Löst die aktuelle Position vollständig für `player` am Zug.

    Erwartet ein NICHT-terminales Brett (kein Spieler hat schon gewonnen, es ist
    noch mindestens ein Zug frei) - das prüft die aufrufende Stelle (App). `value`
    entspricht `max`/`min` über `move_values`, je nachdem wer am Zug ist - die
    optimalen Spalten sind deshalb einfach die mit `move_values[c] == value`.
    """
    if counter is None:
        counter = NodeCounter()
    value, move_values = _recurse(board, player, counter)
    best_columns = [c for c, v in move_values.items() if v == value]
    return SolveResult(value=value, move_values=move_values, node_count=counter.count, best_columns=best_columns)


def _recurse(board: list[list[int]], player: int, counter: NodeCounter) -> tuple[int, dict[int, int]]:
    counter.count += 1
    move_values: dict[int, int] = {}
    for col in legal_columns(board):
        move = apply_move(board, col, player)
        if check_win_at(board, move, player):
            value = 1 if player == PLAYER_ONE else -1
        elif is_full(board):
            value = 0
        else:
            value, _ = _recurse(board, other_player(player), counter)
        move_values[col] = value
        undo_move(board, move)
    return (max(move_values.values()) if player == PLAYER_ONE else min(move_values.values())), move_values
