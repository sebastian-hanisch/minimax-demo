# Minimax: Adversarische Suche am Beispiel Mini-Vier-Gewinnt

Wurzel der **Adversarische-Suche-Linie** (Spiel-KI/Game-Engines), einer Anknüpfung an die
Turnierplanung-Linie (Schach) aus einem anderen Blickwinkel: nicht *wer gegen wen*, sondern *wie
entscheidet eine Maschine ihren nächsten Zug*. Vehikel: Mini-Vier-Gewinnt auf kleinen, vollständig
durchsuchbaren Brettern. Kind-Stücke (geplant): Alpha-Beta-Pruning, Transpositionstabellen,
Bewertungsfunktionen, Endspiel-Datenbanken, Self-Play mit gelernter Bewertung.

## Warum dieses Problem

Bei einem deterministischen Nullsummenspiel mit zwei abwechselnd ziehenden Gegnern lässt sich der
optimale Zug beweisen, nicht nur schätzen: **Minimax** durchsucht den vollständigen Spielbaum, eine
Seite maximiert das Ergebnis, die andere minimiert es. Der Preis: die Baumgröße explodiert mit der
Brettgröße. Diese Demo zeigt beides – den Beweis UND die Explosion – bewusst **ohne** jedes Pruning
(das ist Gegenstand des Kind-Stücks Alpha-Beta).

## Modell

Board als Liste von Zeilen, Spielsteine fallen wie bei Vier-Gewinnt in die unterste freie Zeile einer
Spalte. Sieglänge fest auf 4. Der Spielwert einer Stellung ist rekursiv definiert (siehe 📐-Expander in
der App): +1 = Sieg Rot, -1 = Sieg Gelb, 0 = Remis bei perfektem Spiel beider Seiten.

## Methodik

Vollständige, ungeprunte Rekursion (`mm_minimax.solve_position`) ab jeder angefragten Stellung. Live
wählbar sind ausschließlich drei vorab gemessene, unter 2,5 s liegende Brettgrößen (3×3, 4×3, 3×4) –
größere Bretter (ab 4×4) werden nur als vorab gemessener Referenzpunkt gezeigt, nicht live berechnet.

## Befunde (gemessen, keine Behauptungen)

Naive Minimax-Suche ohne Pruning, ab dem leeren Brett, gemessen mit der tatsächlich ausgelieferten
Suche (`mm_minimax.solve_position`, siehe `tests/test_claims.py`):

| Brett | Knoten | Zeit | Live wählbar |
|---|---|---|---|
| 3×3 | 3.568 | 0,01 s | ja |
| 4×3 | 69.877 | 0,24 s | ja |
| 3×4 | 700.777 | 2,39 s | ja |
| 4×4 | 83.078.201 | 334 s (~5,6 min) | nein (nur Referenzpunkt) |

- **Explosion:** von 3×3 auf 4×4 (nur 7 zusätzliche Felder) wächst die Knotenzahl um das rund
  23.282-fache.
- **Verzweigungsfaktor schlägt Tiefe:** 4×3 und 3×4 haben beide 12 Felder, aber 3×4 (mehr Spalten =
  höherer Verzweigungsfaktor) hat rund das 10-fache an Suchknoten gegenüber 4×3 (mehr Zeilen = mehr
  Tiefe) – bei gleicher Feldzahl dominiert der Verzweigungsfaktor das b^d-Wachstum stärker als die
  Tiefe.
- **Alle gemessenen Bretter (3×3 bis 4×4) enden remis** bei perfektem Spiel ab der Startstellung – der
  bekannte Vorteil des Startspielers bei Standard-Vier-Gewinnt (7×6, bewiesen von Victor Allis 1988)
  zeigt sich auf diesen kleinen Brettern noch nicht.

## Ehrliche Grenzen

- Kein Pruning – bewusst der Punkt dieses Stücks, macht die Demo aber auf Bretter ab 4×4 unbrauchbar
  langsam.
- Keine Zeitkontrolle/Schachuhr, nur reine Spielbaumgröße.
- Kein öffentlicher Referenzlöser für diese Nicht-Standardgrößen verfügbar – Korrektheit stattdessen
  über handverifizierte Trivialfälle (1×1, 1×4) und eine strukturell unabhängige zweite Implementierung
  (Alpha-Beta, testintern) abgesichert, siehe `tests/test_minimax.py`.

## Tests

29 Tests (`pytest tests/ -v`): Brettmechanik, Suchalgorithmus (Handverifikation + Alpha-Beta-Gegenprobe),
PDF-Export, Streamlit-Rauchtests (AppTest: jede Brettgröße, Spaltenklick, Permalink-Rundlauf,
Brettgrößenwechsel setzt die Zugfolge zurück). Zwei echte Bugs beim Bau gefunden und gefixt:
`multi_cell(w=0, ...)` lässt den Cursor am rechten Rand stehen (nicht wie `cell` am linken) – ein
zweiter `multi_cell`-Aufruf direkt danach stürzte ab; und `load_permalink_settings()` hätte ohne einen
Session-Guard bei JEDEM Rerun die Zugfolge aus der (noch nicht aktualisierten) URL überschrieben und
so jeden Spaltenklick sofort wieder rückgängig gemacht.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Einstiegspunkt |
| `mm_constants.py` | Brettgrößen, Farben, gemessene Referenzwerte |
| `mm_game.py` | Brettmechanik (Zug, Sieg-/Remisprüfung, Zugfolgen-Wiedergabe) |
| `mm_minimax.py` | Erschöpfende Suche |
| `mm_evaluation.py` | Verdikt-Texte, abgeleitete Kennzahlen |
| `mm_visualization.py` | Plotly-Brett und Explosions-Diagramm |
| `mm_presets.py` | Presets, Permalink, Session-Defaults |
| `mm_pdf_export.py` | PDF-Export |

## Bewusst nicht umgesetzt

- Bretter ab 4×4 live berechenbar zu machen (Gegenstand des Kind-Stücks Alpha-Beta).
- Eröffnungsbücher, Zeitkontrolle, Turniermodus.

## Lokal ausführen

```bash
pip install -r requirements-dev.txt
streamlit run app.py
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.
