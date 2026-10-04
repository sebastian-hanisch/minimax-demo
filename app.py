"""Minimax: erschöpfende Baumsuche für ein deterministisches Nullsummenspiel.

Wurzel der Adversarische-Suche-Linie. Vehikel: Mini-Vier-Gewinnt auf kleinen,
vollständig durchsuchbaren Brettern.
"""

from __future__ import annotations

import streamlit as st

import mm_constants as C
from mm_evaluation import (
    branching_vs_depth_factor,
    explosion_growth_factor,
    format_de_number,
    to_move_verdict,
)

_de = format_de_number
from mm_game import replay
from mm_minimax import NodeCounter, solve_position
from mm_pdf_export import build_pdf
from mm_presets import (
    PRESET_HELP,
    PRESETS,
    apply_preset,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from mm_visualization import board_figure, explosion_figure

st.set_page_config(page_title="Minimax – Sebastian Hanisch", layout="wide")

st.title("♟️ Minimax: Adversarische Suche am Beispiel Mini-Vier-Gewinnt")
st.markdown(
    """
    **Minimax** durchsucht bei einem deterministischen Nullsummenspiel mit zwei
    abwechselnd ziehenden Gegnern (hier: Mini-Vier-Gewinnt) den **vollständigen**
    Spielbaum: eine Seite maximiert das Ergebnis, die andere minimiert es. Auf den
    kleinen Brettern dieser Demo beweist die Suche für jede Stellung exakt, ob
    Sieg, Remis oder Niederlage bei perfektem Spiel herauskommt – ganz **ohne**
    Pruning (das folgt erst im Kind-Stück **Alpha-Beta**). Am Ende der Seite:
    die **📐 Mathematische Formulierung**.
    """
)

st.caption("🎯 Schnellstart – eine Beispielstellung laden")
preset_cols = st.columns(len(PRESETS))
for col, name in zip(preset_cols, PRESETS):
    col.button(
        name,
        use_container_width=True,
        on_click=apply_preset,
        args=(name,),
        help=PRESET_HELP[name],
    )
st.caption("🔗 Die URL merkt sich Brettgröße und Zugfolge (Permalink).")

load_permalink_settings()
init_session_state_defaults()

def _reset_moves_on_board_change() -> None:
    st.session_state["moves"] = []


with st.sidebar:
    st.header("⚙️ Einstellungen")
    board_index = st.radio(
        "Brettgröße",
        options=range(len(C.BOARD_OPTIONS)),
        format_func=lambda i: C.BOARD_OPTIONS[i]["label"],
        key="board_index_select",
        on_change=_reset_moves_on_board_change,
        help="Live wählbar sind nur vorab gemessene, unter ~2,5 s liegende Größen. Wechsel setzt die Zugfolge zurück.",
    )
    if st.button("↺ Neues Spiel", use_container_width=True, help="Setzt die Zugfolge auf dieser Brettgröße zurück."):
        st.session_state["moves"] = []
        st.rerun()

board_spec = C.BOARD_OPTIONS[board_index]
rows, cols = board_spec["rows"], board_spec["cols"]
moves: list[int] = [m for m in st.session_state["moves"] if 0 <= m < cols]

sync_query_params(board_index, moves)


@st.cache_data(show_spinner="Durchsuche den Spielbaum erschöpfend ...")
def _replay_and_solve(rows: int, cols: int, moves: tuple[int, ...]):
    state = replay(rows, cols, list(moves))
    if state.is_terminal:
        return state, None
    counter = NodeCounter()
    result = solve_position([row[:] for row in state.board], state.player_to_move, counter)
    return state, result


state, result = _replay_and_solve(rows, cols, tuple(moves))

st.subheader("Stellung")
board_col, info_col = st.columns([2, 1])

with board_col:
    best_columns = result.best_columns if result is not None else []
    fig = board_figure(state.board, state.last_move, state.winner, best_columns)
    st.plotly_chart(fig, use_container_width=True, key="board_chart")

    if not state.is_terminal:
        click_cols = st.columns(cols)
        for c, click_col in enumerate(click_cols):
            full_column = state.board[0][c] != C.EMPTY
            is_best = c in best_columns
            label = f"⬇ {c}" + (" ★" if is_best else "")
            if click_col.button(label, key=f"drop_{c}", disabled=full_column, use_container_width=True):
                st.session_state["moves"] = moves + [c]
                st.rerun()

with info_col:
    if state.is_terminal:
        if state.winner is not None:
            st.success(f"Spiel beendet: {C.PLAYER_NAMES[state.winner]} hat gewonnen.")
        else:
            st.info("Spiel beendet: Remis (Brett voll).")
    else:
        st.metric("Am Zug", C.PLAYER_NAMES[state.player_to_move])
        st.metric("Durchsuchte Knoten (diese Stellung)", _de(result.node_count))
        verdict = to_move_verdict(result, state.player_to_move)
        if "erzwingen" in verdict and "nicht mehr" not in verdict:
            st.success(verdict)
        elif "verliert" in verdict:
            st.warning(verdict)
        else:
            st.info(verdict)
        st.caption("★ = optimale Spalte(n) laut vollständiger Suche.")

        pdf_bytes = build_pdf(rows, cols, moves, state.player_to_move, result)
        st.download_button(
            "📄 Analyse als PDF",
            data=pdf_bytes,
            file_name="minimax_analyse.pdf",
            mime="application/pdf",
        )

st.markdown("---")
st.subheader("🔬 Wie schnell explodiert die Suche?")
st.markdown(
    """
    Jedes zusätzliche freie Feld vervielfacht die Zahl der möglichen Fortsetzungen.
    Die folgenden Werte sind **gemessen** (naive Minimax-Suche ohne Pruning, ab dem
    leeren Brett) – das größte Brett ist zu langsam für die interaktive
    Nutzung oben und deshalb nur als Referenzpunkt gezeigt (grau).
    """
)
st.plotly_chart(explosion_figure((rows, cols) if not state.is_terminal else None), use_container_width=True, key="explosion_chart")
factor = explosion_growth_factor()
st.info(
    f"Von 3×3 auf 4×4 (nur 7 zusätzliche Felder) wächst die Knotenzahl um das "
    f"**{_de(factor)}**-fache – 4×4 dauert bereits über 5 Minuten und ist deshalb "
    f"oben nicht mehr live wählbar."
)

st.subheader("🔬 Verzweigungsfaktor oder Tiefe – was zählt mehr?")
st.markdown(
    """
    4 Zeilen × 3 Spalten und 3 Zeilen × 4 Spalten haben **beide 12 Felder** – aber
    unterschiedlich viele Zeilen (Tiefe) bzw. Spalten (Verzweigungsfaktor, weil
    jede Spalte ein möglicher Zug ist).
    """
)
b_factor = branching_vs_depth_factor()
st.success(
    f"Bei gleicher Feldzahl hat das breitere Brett (3×4, mehr Spalten) **{_de(b_factor, 1)}-mal** "
    f"so viele Suchknoten wie das tiefere Brett (4×3, mehr Zeilen) – der Verzweigungsfaktor "
    f"dominiert das b^d-Wachstum stärker als die Tiefe."
)

st.markdown("---")
st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
    - **Kein Pruning.** Die Suche besucht wirklich jede erreichbare Stellung – das
      ist hier bewusst der Punkt (Kontrast zum Kind-Stück Alpha-Beta), macht die
      Demo aber auf größeren Brettern (ab 4×4) unbrauchbar langsam.
    - **Keine Zeitkontrolle.** Echte Turnierpartien haben ein Zeitlimit; diese
      Demo bewertet nur die reine Spielbaumgröße, keine Schachuhr.
    - **Kleines Brett, kleine Aussagekraft.** Auf allen gemessenen Brettgrößen
      (3×3 bis 4×4) endet die Ausgangsstellung remis bei perfektem Spiel – der
      bekannte Vorteil des Startspielers
      bei Standard-Vier-Gewinnt (7×6, bewiesen von Victor Allis 1988) zeigt sich
      auf diesen kleinen Brettern noch nicht.
    """
)

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
        Für eine Stellung $s$ mit Spieler $p \in \{\text{Rot}, \text{Gelb}\}$ am Zug
        und Nachfolgestellungen $s' \in \text{Züge}(s)$:

        $$
        \text{minimax}(s) =
        \begin{cases}
        +1 & s \text{ ist Sieg Rot} \\
        -1 & s \text{ ist Sieg Gelb} \\
        0 & s \text{ ist Remis (Brett voll, kein Sieger)} \\
        \max_{s'} \text{minimax}(s') & p = \text{Rot} \\
        \min_{s'} \text{minimax}(s') & p = \text{Gelb}
        \end{cases}
        $$

        Die Rekursion terminiert immer, weil jede Stellung höchstens
        $\text{Zeilen} \times \text{Spalten}$ freie Felder hat – der Baum ist endlich,
        aber seine Größe wächst mit dem Verzweigungsfaktor (Spaltenzahl) hoch der
        Tiefe (freie Felder), siehe die Experimente oben.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Adversarische Suche: Minimax bis Selbstspiel](https://sebastianhanisch.net/konzepte-adversarische-suche.html)."
)
