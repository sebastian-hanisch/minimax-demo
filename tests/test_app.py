"""Rauchtests der Streamlit-Oberfläche per AppTest."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

import mm_constants as C

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"


def _run(setup=None):
    at = AppTest.from_file(str(APP), default_timeout=60)
    if setup is not None:
        setup(at)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_default_renders_without_exception():
    at = _run()
    assert any("Stellung" in h.value for h in at.subheader)


def test_every_board_option_renders():
    for index in range(len(C.BOARD_OPTIONS)):

        def setup(at, index=index):
            at.session_state["board_index_select"] = index
            at.session_state["moves"] = []

        _run(setup)


def test_clicking_a_column_button_plays_a_move():
    at = _run()
    drop_buttons = [b for b in at.button if b.key and b.key.startswith("drop_")]
    assert drop_buttons
    drop_buttons[0].click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert len(at.session_state["moves"]) == 1


def test_switching_board_size_resets_moves():
    def setup(at):
        at.session_state["board_index_select"] = 1
        at.session_state["moves"] = [0]

    at = _run(setup)
    at.radio(key="board_index_select").set_value(2)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["moves"] == []


def test_terminal_position_hides_move_buttons():
    # 3x3 kann laut Suche (Sieglaenge 4 > jede Brettdimension) nie gewonnen
    # werden - drei volle Runden durch alle Spalten fuellen das Brett zum Remis.
    def setup_full(at):
        at.session_state["board_index_select"] = 0
        at.session_state["moves"] = [0, 1, 2, 0, 1, 2, 0, 1, 2]

    at = _run(setup_full)
    drop_buttons = [b for b in at.button if b.key and b.key.startswith("drop_")]
    assert drop_buttons == []


def test_permalink_restores_board_and_moves():
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.query_params["board"] = "0"
    at.query_params["moves"] = "0,1"
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    assert at.session_state["board_index_select"] == 0
    assert at.session_state["moves"] == [0, 1]
