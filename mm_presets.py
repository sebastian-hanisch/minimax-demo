"""PRESETS, Permalink (Begrenzen/Einrasten), Session-Defaults.

Kein Zufalls-Regler: die Position ist vollständig durch Brettgröße + Zugfolge
bestimmt, es gibt hier keine Szenario-Zufallsgenerierung wie in anderen Demos.
"""

from __future__ import annotations

import streamlit as st

from mm_constants import BOARD_OPTIONS, DEFAULT_BOARD_INDEX

PRESETS = {
    "Leeres 3×3": {"board_index": 0, "moves": []},
    "Leeres 4×3 (Standard)": {"board_index": 1, "moves": []},
    "3×4 nach mittigem Eröffnungszug": {"board_index": 2, "moves": [1]},
}
PRESET_HELP = {
    "Leeres 3×3": "Das kleinste Brett - Suche in Sekundenbruchteilen.",
    "Leeres 4×3 (Standard)": "Ausgangsstellung des Standard-Vehikels dieser Linie.",
    "3×4 nach mittigem Eröffnungszug": "Zeigt, wie sich der Suchbaum nach einem Zug verkleinert.",
}

_DEFAULTS = {"board_index": DEFAULT_BOARD_INDEX, "moves": []}


def apply_preset(name: str) -> None:
    preset = PRESETS[name]
    st.session_state["board_index_select"] = preset["board_index"]
    st.session_state["moves"] = list(preset["moves"])


def init_session_state_defaults() -> None:
    if "board_index_select" not in st.session_state:
        st.session_state["board_index_select"] = _DEFAULTS["board_index"]
    if "moves" not in st.session_state:
        st.session_state["moves"] = list(_DEFAULTS["moves"])


def _parse_moves(raw: str) -> list[int]:
    if not raw:
        return []
    try:
        return [int(x) for x in raw.split(",") if x != ""]
    except ValueError:
        return []


def load_permalink_settings() -> None:
    """Lädt Brettgröße/Zugfolge aus der URL - aber NUR beim allerersten Lauf
    dieser Session.

    `st.query_params` bleibt über Reruns hinweg bestehen und wird am Ende jedes
    Laufs per `sync_query_params()` neu geschrieben - würde diese Funktion bei
    JEDEM Rerun unbedingt aus den Query-Params laden, würde sie jeden Spalten-
    Klick sofort wieder rückgängig machen (die Params spiegeln zu diesem
    Zeitpunkt im Skript noch den Stand VOR dem Klick) und jeden Preset-Klick
    überschreiben. Der Guard macht die Funktion ab dem zweiten Lauf zum No-Op.
    """
    if "board_index_select" in st.session_state:
        return
    params = st.query_params
    if "board" not in params and "moves" not in params:
        return
    board_index = _DEFAULTS["board_index"]
    if "board" in params:
        try:
            candidate = int(params["board"])
        except ValueError:
            candidate = board_index
        if 0 <= candidate < len(BOARD_OPTIONS):
            board_index = candidate
    moves = _parse_moves(params.get("moves", ""))
    st.session_state["board_index_select"] = board_index
    st.session_state["moves"] = moves


def sync_query_params(board_index: int, moves: list[int]) -> None:
    st.query_params["board"] = str(board_index)
    st.query_params["moves"] = ",".join(str(m) for m in moves)
