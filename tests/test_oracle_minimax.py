"""Unabhängiges Orakel für die erschöpfende Minimax-Suche.

Anderer Rechenweg als `mm_minimax`: Stellung als Spalten-Tupel (statt Zeilenliste),
Siegprüfung durch Aufzählen ALLER Viererlinien des Bretts (statt Strahlen vom
letzten Stein), Bewertung memoisiert über Stellungen (statt Baumrekursion). Die
Zahl der Suchknoten der ungeprunten Suche wird ebenfalls memoisiert nachgezählt.
"""

import random
from functools import lru_cache

import pytest

from mm_game import apply_move, check_win_at, empty_board, legal_columns
from mm_minimax import solve_position


def _lines(rows, cols):
    out = []
    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                cells = [(r + i * dr, c + i * dc) for i in range(4)]
                if all(0 <= a < rows and 0 <= b < cols for a, b in cells):
                    out.append(cells)
    return out


class _Oracle:
    def __init__(self, rows, cols):
        self.rows, self.cols = rows, cols
        self.lines = _lines(rows, cols)
        self.value = lru_cache(maxsize=None)(self._value)
        self.nodes = lru_cache(maxsize=None)(self._nodes)

    def cell(self, st, r, c):
        h = self.rows - 1 - r  # Zeile 0 = oben
        return st[c][h] if h < len(st[c]) else 0

    def won(self, st, p):
        return any(all(self.cell(st, r, c) == p for r, c in line) for line in self.lines)

    def moves(self, st):
        return [c for c in range(self.cols) if len(st[c]) < self.rows]

    def play(self, st, c, p):
        return st[:c] + (st[c] + (p,),) + st[c + 1 :]

    def move_values(self, st, p):
        res = {}
        for c in self.moves(st):
            ns = self.play(st, c, p)
            if self.won(ns, p):
                res[c] = 1 if p == 1 else -1
            elif not self.moves(ns):
                res[c] = 0
            else:
                res[c] = self.value(ns, 3 - p)
        return res

    def _value(self, st, p):
        vals = self.move_values(st, p).values()
        return max(vals) if p == 1 else min(vals)

    def _nodes(self, st, p):
        n = 1
        for c in self.moves(st):
            ns = self.play(st, c, p)
            if not (self.won(ns, p) or not self.moves(ns)):
                n += self.nodes(ns, 3 - p)
        return n


def _to_state(board):
    rows, cols = len(board), len(board[0])
    out = []
    for c in range(cols):
        col = []
        for r in range(rows - 1, -1, -1):
            if board[r][c] == 0:
                break
            col.append(board[r][c])
        out.append(tuple(col))
    return tuple(out)


def _random_position(rng, rows, cols, max_free):
    board, p = empty_board(rows, cols), 1
    for _ in range(rng.randint(max(0, rows * cols - max_free), rows * cols)):
        free = legal_columns(board)
        if not free:
            return None
        mv = apply_move(board, rng.choice(free), p)
        if check_win_at(board, mv, p) or not legal_columns(board):
            return None
        p = 3 - p
    return (board, p) if legal_columns(board) else None


def test_oracle_hand_example():
    o = _Oracle(4, 1)
    assert o.won(((1, 1, 1, 1),), 1) and not o.won(((1, 1, 1, 2),), 1)
    assert o.value(((),), 1) == 0


def test_random_positions_match_oracle():
    rng = random.Random(5)
    done = 0
    while done < 120:
        rows, cols = rng.randint(1, 5), rng.randint(1, 5)
        pos = _random_position(rng, rows, cols, 8)
        if pos is None:
            continue
        board, p = pos
        o = _Oracle(rows, cols)
        st = _to_state(board)
        res = solve_position([r[:] for r in board], p)
        mv = o.move_values(st, p)
        assert res.move_values == mv
        assert res.value == o.value(st, p)
        assert sorted(res.best_columns) == sorted(c for c, v in mv.items() if v == res.value)
        assert res.node_count == o.nodes(st, p)
        done += 1


@pytest.mark.parametrize("rows,cols,expected", [(3, 3, 3_568), (4, 3, 69_877), (3, 4, 700_777)])
def test_empty_board_node_count_matches_memoised_oracle(rows, cols, expected):
    o = _Oracle(rows, cols)
    st = tuple(() for _ in range(cols))
    assert o.nodes(st, 1) == expected
    assert o.value(st, 1) == 0
