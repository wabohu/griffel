# Plan: Farben ohne Alacritty (Veröffentlichung 2.3)

Stand: 2026-10-17, **umgesetzt**. Gesamtplan: `plan-veroeffentlichung.md`, Phase 2.3.

## Problem

Die Farbwerte kommen nur aus der Alacritty-Config (`colors.load_palette`), sonst aus der
eingebauten Palette (Tomorrow Night). Wer kein Alacritty nutzt (oder dort ein anderes Schema
hat, als griffel zeigen soll), kann die Palette nicht ändern, nur einzelne Stellen per
`#rrggbb` überschreiben (`[ui]`, `[board]`, `[colors.light]`). In `[colors] order` gehen nur
Namen, also nie eine eigene Farbe in die Leiste.

Monospace-Schrift: schon erledigt. Ohne `[text] mono_font` und ohne Alacritty nimmt
`elements.text_font` `QFontDatabase.FixedFont`. Nur die Doku sagt noch „from your Alacritty
config“.

## Neu in der Config

```toml
[colors]
# Where the color values come from: "auto" = Alacritty config if there is one, otherwise the
# built-in palette; "alacritty" = only Alacritty (hint if it is missing); "builtin" = never
# read a terminal config. [palette] below overrides single values in every case.
source = "auto"

# Own color values, they win over the source. Names: black red green yellow blue magenta
# cyan white, the same with "bright_" in front, foreground, background. Missing names come
# from the source.
[palette]
# red = "#f7768e"
# bright_red = "#ff7a93"
# background = "#1a1b26"
```

- Werte nur `#rrggbb` oder `0xrrggbb` (wie Alacritty, `normalize_color`). Ungültiger Wert
  oder unbekannter Name: Hinweis auf stderr, Wert ignoriert, nie ein Absturz
- Ungültiges `source`: Hinweis, `auto`
- `source` gilt nur für Farben, nicht für die Schrift. Die Schrift hat schon ihren eigenen
  Schalter (`[text] mono_font`), und wer Alacritty-Farben nicht will, will die Schrift aus dem
  Terminal vielleicht trotzdem. Kein neuer Schalter dafür
- Später denkbar (nicht für 0.1.0): weitere Quellen (kitty, foot, Xresources) als neue Werte
  für `source`, `auto` probiert sie dann der Reihe nach

## Code

- `colors.py`: `load_palette(config_path=None, source="auto", overrides=None)`.
  Ablauf: eingebaute Palette → bei `auto`/`alacritty` Alacritty darüber → `overrides`
  (Dict aus `[palette]`) darüber. `Palette.source` beschreibt das Ergebnis, z. B.
  „~/.config/alacritty/alacritty.toml + [palette]“ (nur Info, `python -m griffel.colors`)
- Neue Hilfsfunktion `palette_overrides(values)` in `colors.py` (Qt-frei): prüft Namen und
  Werte, gibt das bereinigte Dict zurück
- `settings.py`: `SOURCES = ("auto", "alacritty", "builtin")`, liest `[colors] source` und
  `[palette]`, übergibt an `load_palette`. Sonst ändert sich nichts, alle weiteren Stellen
  (`lookup`, Leiste, Theme, Whiteboard-Hintergrund, `[colors.light]`) gehen schon über die
  Palette
- Doku-Texte neutral: Modul-Docstrings (`colors.py`, `ui.py`), Kommentare in `settings.py`,
  `config.example.toml` („come from your Alacritty config, if you have one, or [palette]“),
  README Zeile 47, `docs/usage.md` (Alt+V: „terminal font from the Alacritty config, if there
  is one, otherwise the system monospace font“)

## Tests

`tests/test_settings.py` (Umgebung ohne HOME, also eingebaute Palette), mit einer
Alacritty-Datei im Temp-Ordner:
- `[palette]` überschreibt einzelne Farben, der Rest bleibt; auch `background`/`foreground`
  (wirkt auf `Settings.theme` und `lookup("background")`)
- `[palette]` gewinnt über Alacritty
- `source = "builtin"` ignoriert die Alacritty-Datei, `"alacritty"` ohne Datei: Hinweis +
  eingebaute Palette, ungültige `source`: Hinweis + auto
- ungültige Werte/Namen in `[palette]`: Hinweis, ignoriert

`regress.py` bleibt gleich (Standard ändert sich nicht). Kein GUI-Szenario nötig, keine neue
Bedienung.

## Handtest bei dir

- Unverändert starten: Farben wie bisher (deine Config hat weder `source` noch `[palette]`)
- `[palette] yellow = "#ff0000"` → gelb in der Leiste ist rot
- `[colors] source = "builtin"` → Tomorrow-Night-Farben statt deiner Alacritty-Farben
