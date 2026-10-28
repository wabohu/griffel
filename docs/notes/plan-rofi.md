# Plan: rofi-Farben aus der griffel-Leiste (Veröffentlichung 2.5)

Stand: 2026-10-17, **umgesetzt**. Gesamtplan: `plan-veroeffentlichung.md`, Phase 2.5.

## Problem

`data/griffel.rasi` nimmt seine Farben aus Variablen meines Rofi-Setups (`base03`, `base02`,
`base01`, `base00`, `white`, `blue` aus `~/.config/rofi/colors.rasi`, das `notify.ask` per
`-theme-str @import` lädt). Wer diese Datei nicht hat (oder dort andere Namen), bekommt den
Tokyo-Night-Rückfall, der nicht zur griffel-Leiste passt. Und wer eine `colors.rasi` mit
denselben Namen, aber ganz anderem Sinn hat, bekommt ein zufälliges Ergebnis.

## Idee

griffel gibt rofi seine eigenen Farben mit, aus `ui.Theme` (also `[ui] bar_*`, Standard aus
der Palette). Dann sieht die Abfrage immer aus wie die Leiste:

```
rofi … -theme griffel.rasi -theme-str '* { background: #…; foreground: #…; … }'
```

`griffel.rasi` behält seine sechs Variablen, sie werden nur von außen gesetzt:

| rasi-Variable    | woher                                           |
|------------------|-------------------------------------------------|
| `background`     | Leistenhintergrund (deckend, ohne `bar_opacity`) |
| `foreground`     | Leistenvordergrund                              |
| `selected`       | Akzent (`bar_accent`)                           |
| `background-alt` | Hintergrund, 15 % zum Vordergrund gemischt (Eingabezeile, Auswahl) |
| `frame`          | Hintergrund, 30 % zum Vordergrund (Rahmen)      |
| `dimmed`         | Hintergrund, 65 % zum Vordergrund (nicht gewählte Einträge, Platzhalter) |

Deckend, weil durchsichtige rofi-Fenster einen Compositor brauchen und sonst schwarz werden.

## Config

```toml
[ui]
# Colors of the rofi prompts: empty = the bar colors above. Or a rasi file that is loaded
# instead (variables base03 base02 base01 base00 white blue, e.g. ~/.config/rofi/colors.rasi;
# it may also set the font).
rofi_colors = ""
```

- Leer (Standard): Farben aus dem Theme, `colors.rasi` wird **nicht** mehr geladen
- Pfad gesetzt: wie heute (`@import` der Datei, Variablen aus `griffel.rasi`), keine
  Theme-Farben. Datei fehlt: Hinweis, Theme-Farben
- Eigenes `rofi_theme`: bekommt die Theme-Farben trotzdem mitgeliefert (schadet nicht, es kann
  sie nutzen)

**Für dich ändert sich etwas:** Deine `colors.rasi` setzt auch `font: "Droid Sans 15"`. Ohne
sie zeigt rofi seine Standardschrift und die Leistenfarben. Wer das alte Aussehen will:
`rofi_colors = "~/.config/rofi/colors.rasi"`. Beim Handtest entscheidest du.

## Code

- `colors.py` (Qt-frei): `mix(a, b, t)` für `#rrggbb`
- `settings.py`: `Settings.rofi_colors` (Pfad oder None), `Settings.rofi_vars()` (Dict der
  sechs Variablen aus `self.theme`)
- `notify.ask(question, choices, theme=None, colors=None, colors_file=None)`: baut
  `-theme-str` aus `colors` (`* { name: value; … }`) bzw. `@import` aus `colors_file`.
  `ROFI_COLORS` (fester Pfad) fällt weg
- `canvas_output.ask`: übergibt beides aus den Settings
- `griffel.rasi`: Kopfkommentar neu; Rückfallwerte in `var(…)` bleiben (falls rofi direkt mit
  der Datei gestartet wird)
- `config.example.toml`: `rofi_colors`, Kommentar zu `rofi_theme` anpassen; README, falls
  dort `colors.rasi` steht

## Tests

- `test_settings.py`: `rofi_vars()` aus einem Theme (Mischwerte), `rofi_colors` leer/Pfad
- Qt-frei in `test_settings.py`: Befehlszeile von `ask` prüfen, ohne rofi zu starten
  (Funktion `rofi_command(…)` aus `ask` herausgezogen)
- GUI: `test_board` zeigt die rofi-Abfrage schon; ein Screenshot der Abfrage in
  `tests/gui/out/board/`, den schaue ich an (Farben wie die Leiste)

## Handtest bei dir

- Whiteboard (Alt+Delete), etwas zeichnen, Strg+Q: Abfrage in den Leistenfarben. Gefällt sie
  dir, oder willst du `rofi_colors` auf deine `colors.rasi` setzen?
