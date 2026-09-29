import pytest

from mm_constants import EMPTY, PLAYER_ONE, PLAYER_TWO
from mm_game import (
    apply_move,
    check_win_at,
    empty_board,
    is_full,
    legal_columns,
    other_player,
    replay,
    undo_move,
    winning_line,
)


def test_empty_board_shape():
    board = empty_board(3, 4)
    assert len(board) == 3
    assert all(len(row) == 4 for row in board)
    assert all(cell == EMPTY for row in board for cell in row)


def test_other_player():
    assert other_player(PLAYER_ONE) == PLAYER_TWO
    assert other_player(PLAYER_TWO) == PLAYER_ONE


def test_drop_lands_on_lowest_free_row():
    board = empty_board(3, 3)
    move = apply_move(board, 1, PLAYER_ONE)
    assert move.row == 2
    move2 = apply_move(board, 1, PLAYER_TWO)
    assert move2.row == 1


def test_full_column_raises():
    board = empty_board(2, 1)
    apply_move(board, 0, PLAYER_ONE)
    apply_move(board, 0, PLAYER_TWO)
    with pytest.raises(ValueError):
        apply_move(board, 0, PLAYER_ONE)


def test_legal_columns_excludes_full_ones():
    board = empty_board(2, 2)
    apply_move(board, 0, PLAYER_ONE)
    apply_move(board, 0, PLAYER_TWO)
    assert legal_columns(board) == [1]


def test_undo_move_restores_empty_cell():
    board = empty_board(3, 3)
    move = apply_move(board, 0, PLAYER_ONE)
    undo_move(board, move)
    assert board[move.row][move.column] == EMPTY
    assert legal_columns(board) == [0, 1, 2]


def test_is_full_true_only_when_no_columns_left():
    board = empty_board(1, 2)
    assert not is_full(board)
    apply_move(board, 0, PLAYER_ONE)
    assert not is_full(board)
    apply_move(board, 1, PLAYER_TWO)
    assert is_full(board)


def test_horizontal_win_detected():
    board = empty_board(1, 4)
    move = None
    for col in range(4):
        move = apply_move(board, col, PLAYER_ONE)
    assert check_win_at(board, move, PLAYER_ONE)


def test_vertical_win_detected():
    board = empty_board(4, 1)
    move = None
    for _ in range(4):
        move = apply_move(board, 0, PLAYER_ONE)
    assert check_win_at(board, move, PLAYER_ONE)


def test_diagonal_win_detected():
    # Klassisches Diagonal-Muster: Gelb baut die Treppe, auf der Rot gewinnt.
    board = empty_board(4, 4)
    sequence = [
        (0, PLAYER_ONE),
        (1, PLAYER_TWO),
        (1, PLAYER_ONE),
        (2, PLAYER_TWO),
        (2, PLAYER_TWO),
        (2, PLAYER_ONE),
        (3, PLAYER_TWO),
        (3, PLAYER_TWO),
        (3, PLAYER_TWO),
        (3, PLAYER_ONE),
    ]
    move = None
    for col, player in sequence:
        move = apply_move(board, col, player)
    assert check_win_at(board, move, PLAYER_ONE)
    line = winning_line(board, move, PLAYER_ONE)
    assert line is not None
    assert len(line) == 4


def test_three_in_a_row_is_not_a_win():
    board = empty_board(1, 3)
    move = None
    for col in range(3):
        move = apply_move(board, col, PLAYER_ONE)
    assert not check_win_at(board, move, PLAYER_ONE)


def test_replay_empty_moves_returns_start_position():
    state = replay(3, 3, [])
    assert state.player_to_move == PLAYER_ONE
    assert state.last_move is None
    assert not state.is_terminal


def test_replay_stops_at_win():
    # Spalte 0 bekommt (abwechselnd mit Spalte 1) viermal in Folge Rot -> Sieg
    # senkrecht in Spalte 0 nach dem 7. (letzten) Zug.
    state = replay(4, 4, [0, 1, 0, 1, 0, 1, 0])
    assert state.is_terminal
    assert state.winner == PLAYER_ONE


def test_replay_ignores_moves_after_terminal_state():
    winning_moves = [0, 1, 0, 1, 0, 1, 0]
    state_short = replay(4, 4, winning_moves)
    state_long = replay(4, 4, winning_moves + [2, 2, 2])
    assert state_long.board == state_short.board
    assert state_long.is_terminal


def test_replay_full_board_without_winner_is_draw():
    # 1x1-Brett: einziger Zug fuellt das Brett sofort, ohne Sieg moeglich.
    state = replay(1, 1, [0])
    assert state.is_terminal
    assert state.winner is None
