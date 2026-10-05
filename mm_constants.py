"""Regler-Grenzen, feste Annahmen, Farben."""

WIN_LENGTH = 4
EMPTY = 0
PLAYER_ONE = 1  # beginnt immer, entspricht "Rot"
PLAYER_TWO = 2  # "Gelb"

PLAYER_NAMES = {PLAYER_ONE: "Rot", PLAYER_TWO: "Gelb"}
PLAYER_COLOURS = {PLAYER_ONE: "#d62728", PLAYER_TWO: "#f2c744"}
EMPTY_COLOUR = "#e5e5e5"

# Live wählbare Brettgrößen: ausschließlich vorab gemessene, unter ~2,5 s liegende
# Größen (siehe tools/PRESET_SWEEP.md) - bewusst eine Auswahl statt zweier freier
# Regler, damit die 4x4-Falle (334 s) strukturell nicht wählbar ist.
BOARD_OPTIONS = [
    {"rows": 3, "cols": 3, "label": "3 × 3"},
    {"rows": 4, "cols": 3, "label": "4 Zeilen × 3 Spalten"},
    {"rows": 3, "cols": 4, "label": "3 Zeilen × 4 Spalten"},
]
DEFAULT_BOARD_INDEX = 1  # 4x3

# Vorab gemessene, NICHT live wählbare Referenzpunkte für die Explosions-Kurve -
# gemessen mit der TATSÄCHLICH ausgelieferten Suche (mm_minimax.solve_position),
# nicht mit einem Wegwerf-Skript (tools/PRESET_SWEEP.md dokumentiert den Lauf).
# 4x4 dauert bereits 334 s - eine weitere Stufe (z. B. 3x5) wurde deshalb bewusst
# NICHT nachgemessen, um keine Zahl zu zeigen, die nicht am ausgelieferten Code
# gemessen wurde.
MEASURED_EXPLOSION = [
    {"rows": 3, "cols": 3, "nodes": 3_568, "seconds": 0.01, "live": True},
    {"rows": 4, "cols": 3, "nodes": 69_877, "seconds": 0.24, "live": True},
    {"rows": 3, "cols": 4, "nodes": 700_777, "seconds": 2.39, "live": True},
    {"rows": 4, "cols": 4, "nodes": 83_078_201, "seconds": 334.09, "live": False},
]

# Der Verzweigungsfaktor-vs-Tiefe-Befund: 4x3 und 3x4 haben beide 12 Felder.
BRANCHING_VS_DEPTH_PAIR = (
    {"rows": 4, "cols": 3, "nodes": 69_877},
    {"rows": 3, "cols": 4, "nodes": 700_777},
)
