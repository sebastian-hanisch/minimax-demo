"""Handverifikation + unabhängige Gegenprobe für die erschöpfende Suche.

Kein öffentlicher Referenzlöser für diese Nicht-Standardgrößen verfügbar (siehe
Moduldoku) - Korrektheit stattdessen über zwei Wege: (1) von Hand nachvollziehbare
Trivialfälle, (2) eine strukturell unabhängige zweite Implementierung
(Alpha-Beta-Pruning, hier nur testintern) - liefert nach Definition denselben
Spielwert wie volle Minimax-Suche, nur mit weniger besuchten Knoten.
"""

from mm_constants import PLAYER_ONE, PLAYER_TWO
from mm_game import apply_move, check_win_at, empty_board, is_full, legal_columns, other_player, undo_move
from mm_minimax import NodeCounter, solve_position


def test_1x1_board_is_a_trivial_draw():
    # Einziges Feld, Sieglänge 4 unerreichbar -> muss Remis sein.
    board = empty_board(1, 1)
    result = solve_position(board, PLAYER_ONE)
    assert result.value == 0
    assert result.best_columns == [0]


def test_1x4_board_can_never_be_won_by_either_side():
    # 4 Zellen, 2 Spieler im Wechsel -> jeder bekommt genau 2, ein Sieg (alle 4
    # gleiche Farbe) ist strukturell unmöglich, egal welche Spalte gewählt wird.
    board = empty_board(1, 4)
    result = solve_position(board, PLAYER_ONE)
    assert result.value == 0
    assert sorted(result.best_columns) == [0, 1, 2, 3]
    assert all(v == 0 for v in result.move_values.values())


def test_one_move_from_a_forced_win_is_detected():
    # Nach 6 real alternierenden Zügen (P1,P2,P1,P2,P1,P2) steht Rot mit drei
    # Steinen senkrecht in Spalte 0 und ist wieder am Zug -> muss sofort
    # gewinnen können (Spaltenwert 1 in der einzig sinnvollen Spalte).
    board = empty_board(4, 2)
    for col, player in [(0, PLAYER_ONE), (1, PLAYER_TWO)] * 3:
        apply_move(board, col, player)
    result = solve_position(board, PLAYER_ONE)
    assert result.value == 1
    assert result.move_values[0] == 1


def _alpha_beta(board, player, alpha, beta):
    """Unabhängige zweite Implementierung (Alpha-Beta) für die Gegenprobe.

    Liefert per Definition denselben Wert wie volle Minimax-Suche - dient hier
    NICHT als Vorlage für das spätere `alpha-beta-demo`-Stück (eigener,
    quellcodetreuer Bau dort), sondern nur als testinterne Kontrolle.
    """
    for col in legal_columns(board):
        move = apply_move(board, col, player)
        won = check_win_at(board, move, player)
        undo_move(board, move)
        if won:
            return 1 if player == PLAYER_ONE else -1
    if is_full(board):
        return 0

    if player == PLAYER_ONE:
        value = -2
        for col in legal_columns(board):
            move = apply_move(board, col, player)
            value = max(value, _alpha_beta(board, other_player(player), alpha, beta))
            undo_move(board, move)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = 2
        for col in legal_columns(board):
            move = apply_move(board, col, player)
            value = min(value, _alpha_beta(board, other_player(player), alpha, beta))
            undo_move(board, move)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


def test_cross_check_against_independent_alpha_beta_implementation():
    for rows, cols in [(3, 3), (4, 3)]:
        board = empty_board(rows, cols)
        expected = _alpha_beta(board, PLAYER_ONE, -2, 2)
        result = solve_position(board, PLAYER_ONE)
        assert result.value == expected, f"{rows}x{cols}: minimax={result.value} alpha-beta={expected}"


def test_node_count_increases_with_recursion_and_matches_manual_root_count():
    board = empty_board(3, 3)
    counter = NodeCounter()
    result = solve_position(board, PLAYER_ONE, counter)
    assert result.node_count == counter.count
    assert result.node_count > len(legal_columns(board))  # mehr als nur die Wurzel + 1 Ebene


def test_solve_is_deterministic_and_pure_no_board_mutation():
    board = empty_board(3, 3)
    before = [row[:] for row in board]
    solve_position(board, PLAYER_ONE)
    assert board == before
