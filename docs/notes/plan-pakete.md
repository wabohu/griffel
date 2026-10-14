# Plan: Paketstruktur `src/griffel/` (Veröffentlichung Phase 1, Roadmap 20 flach)

Stand: 2026-10-14. Ziel: Die 23 flachen Module werden ein Python-Paket `griffel`, das sich
mit `pyproject.toml` bauen und installieren lässt (Voraussetzung für AUR und pipx). Funktional
ändert sich nichts. Gesamtplan: `plan-veroeffentlichung.md`, Phase 1.

## Warum überhaupt

- Installiert landen Module in `site-packages`. Flach hießen sie dort `ui`, `config`, `history`,
  `tools`, `commands` … und würden mit anderen Paketen kollidieren. In einem Paket heißen sie
  `griffel.ui`, `griffel.config` usw.
- Qt-unabhängiges Python-Konzept, kurz: Ein **Paket** ist ein Ordner mit `__init__.py`. Was darin
  liegt, importiert man als `griffel.<modul>`. Python sucht Pakete in den Ordnern von `sys.path`,
  darum muss beim Start aus dem Quellordner `src/` dort stehen (nicht `src/griffel/`)

## Zielstruktur

```
griffel/                    # Projektordner (Repo)
├── run.py                  # neu: Starter aus dem Quellordner, 755, Ziel des Symlinks
├── pyproject.toml          # neu: Metadaten, Lizenz, Entry Point, Paketdaten
├── config.example.toml  README.md  LICENSE  CLAUDE.md
├── src/griffel/
│   ├── __init__.py         # neu: __version__ = "0.1.0.dev0"
│   ├── __main__.py         # neu: python -m griffel
│   ├── app.py              # heute griffel.py: main, grab_screen
│   ├── canvas.py  canvas_*.py  colors.py  commands.py  config.py  connectors.py
│   ├── document.py  elements.py  export.py  history.py  keymap.py  notify.py
│   ├── settings.py  shortcuts.py  tools.py  ui.py  wm.py
│   └── data/griffel.rasi   # heute rofi/griffel.rasi
├── docs/  scripts/  tests/ # bleiben, wo sie sind
```

Bewusst **nicht** in dieser Phase: Unterpakete (`canvas/`, `config/` …, Roadmap 20 bleibt
offen), `tests/unit/` und `scripts/dev/` (bringt nur Umzüge ohne Nutzen), `share/` mit
`.desktop`-Dateien und Icon (Phase 5).

## Entscheidungen

1. **Startdatei `app.py`, Starter `run.py`.** Ein Starter `griffel.py` im Wurzelordner ginge
   nicht: Python setzt den Ordner des Skripts an den Anfang von `sys.path`, `import griffel`
   fände dann das Skript statt des Pakets. `run.py` trägt `src/` in `sys.path` ein und ruft
   `griffel.app.main()` auf
2. **Absolute Imports:** `from griffel.canvas import Canvas`, `from griffel import history`.
   Alternative wären relative (`from .canvas import Canvas`). Empfehlung absolut: Jede Zeile
   sagt, woher etwas kommt, und PEP 8 empfiehlt sie. Nachteil: Bei einer weiteren Umbenennung
   wären wieder alle Imports dran
3. **Version** nur an einer Stelle, `griffel.__version__`. `pyproject.toml` liest sie per
   `dynamic = ["version"]` aus. Bis zum Release `0.1.0.dev0`, neue Option `--version`
4. **rofi-Theme als Paketdaten:** `importlib.resources.files("griffel") / "data" / "griffel.rasi"`
   statt `Path(__file__)`, dann findet es sich auch im installierten Paket. Muss in
   `pyproject.toml` als `package-data` stehen, sonst fehlt es im Wheel
5. **Tests importieren immer aus `src/`**, nie ein installiertes griffel: `sys.path.insert(0, src)`
   steht vorn. Wichtig, sobald griffel bei dir per AUR installiert ist

## Schritt 1: Verschieben (nur `git mv`)

- `git mv *.py src/griffel/` (außer dem Starter), `git mv griffel.py src/griffel/app.py`,
  `git mv rofi/griffel.rasi src/griffel/data/griffel.rasi`. Reine Umbenennungen, Git zeigt sie
  als `rename … (100%)`, `git log --follow` findet die Historie
- Damit es lauffähig bleibt, ohne Imports anzufassen: `run.py` trägt übergangsweise
  `src/griffel/` in `sys.path` ein (die Module finden sich dann wie heute flach). Ebenso
  `tests/regress.py`, `tests/gui/harness.py` (`REPO` → Quellordner, `GRIFFEL` → `run.py`),
  `scripts/sync_config.py`
- `notify.py`: Pfad zum rofi-Theme (`data/` statt `rofi/`)
- `harness.griffel_pids()`: sucht heute `griffel.py` in der Kommandozeile. Neu: den vollen Pfad
  von `run.py` (eindeutiger als nur ein Dateiname)
- `~/.local/bin/griffel` zeigt danach ins Leere, bei dir: im Projektordner
  `ln -sfn "$PWD/run.py" ~/.local/bin/griffel`. sxhkd und tdrop bleiben unverändert
- Tests, Handtest (Hotkeys), Commit

## Schritt 2: Paket und Imports

- `src/griffel/__init__.py` (Docstring, `__version__`), `src/griffel/__main__.py` (ruft `main()`)
- Alle internen Imports in `src/griffel/` auf `from griffel.x import …` bzw. `from griffel import x`
  (heute rund 70 Zeilen, mechanisch). Ebenso die Imports in Tests (viele stehen in Funktionen von
  `tests/test_document.py`) und `scripts/sync_config.py`
- Jetzt steht `src/` statt `src/griffel/` in `sys.path` (`run.py`, Tests, Skripte)
- **Stolperstelle:** Nie beide Ordner zugleich in `sys.path`. Sonst lädt Python dasselbe Modul
  zweimal (`export` und `griffel.export` sind dann zwei verschiedene Objekte), und ein Test, der
  etwas in `export` ersetzt, trifft das Modul nicht, das die Canvas benutzt. Prüfen per
  `grep -rn "sys.path" .` und einem Test, der nach dem Start nachsieht, dass kein Modul flach
  (ohne `griffel.`) geladen ist
- `app.py`: Option `--version` (aus `griffel.__version__`), Shebang und `755` weg (wird nicht
  mehr direkt gestartet); `run.py` ist jetzt die ausführbare Datei
- `python -m griffel --board` muss mit `PYTHONPATH=src` starten
- Tests, Handtest, Commit

## Schritt 3: `pyproject.toml`

```toml
[build-system]
requires = ["setuptools>=77"]  # SPDX string in license, license-files
build-backend = "setuptools.build_meta"

[project]
name = "griffel"
dynamic = ["version"]
description = "Screenshot annotation tool and whiteboard for X11"
readme = "README.md"
license = "GPL-3.0-or-later"
license-files = ["LICENSE"]
requires-python = ">=3.11"
dependencies = ["PySide6>=6.5"]

[project.scripts]
griffel = "griffel.app:main"

[project.urls]
Homepage = "https://github.com/wabohu/griffel"

[tool.setuptools.dynamic]
version = { attr = "griffel.__version__" }

[tool.setuptools.package-data]
griffel = ["data/*.rasi"]
```

- `dependencies = ["PySide6"]` gilt nur für pip/pipx. Auf Arch kommt es per pacman (`pyside6`),
  das PKGBUILD baut mit `--no-isolation` und prüft keine pip-Abhängigkeiten
- Prüfen ohne Installation, nur mit Arch-Paketen (alle schon installiert: `python-build`,
  `python-installer`, `python-setuptools`, `python-wheel`):
  - `python -m build --wheel --no-isolation` → `dist/griffel-0.1.0.dev0-py3-none-any.whl`
  - Inhalt ansehen (`python -m zipfile -l dist/*.whl`): alle Module, `data/griffel.rasi`,
    keine Tests, kein `run.py`
  - Probeinstallation in einen Wegwerf-Ordner:
    `python -m installer --destdir=<scratch> dist/*.whl`, dann von dort
    `PYTHONPATH=<scratch>/usr/lib/python3.x/site-packages QT_QPA_PLATFORM=offscreen
    <scratch>/usr/bin/griffel --version`. So ist geprüft, dass der Entry Point und das Theme im
    installierten Paket funktionieren, ohne etwas auf deinem System zu installieren
- `.gitignore`: `dist/`, `build/`, `*.egg-info/`
- Tests, Commit (kein Handtest nötig, der Start aus dem Quellordner ändert sich nicht)

## Schritt 4: Doku

- `CLAUDE.md`: Dateipfade (`src/griffel/…`), `run.py` statt `griffel.py` als ausführbare Datei,
  Stolperstelle doppelter Import, Imports `from griffel.x`, Version an einer Stelle
- `CLAUDE.local.md`: Symlink auf `run.py`
- `README.md`: Getting started (`ln -s "$PWD/griffel/run.py" ~/.local/bin/griffel`)
- `docs/usage.md`: `python griffel.py …` → `griffel …`
- `config.example.toml`, Kommentar in `settings.py`: rofi-Theme liegt in `src/griffel/data/`
- Docstrings, die `griffel.py` nennen (`app.py`, Tests)
- `roadmap.md`: Punkt 20 bleibt offen (Unterpakete), Vermerk „flach erledigt“
- Commit, danach evtl. Push (Block fertig)

## Prüfen

- Nach jedem Schritt alle Tests: `test_settings`, `test_document`, `regress` (Referenzbild
  unverändert), `python tests/gui/run.py`
- `git diff --summary`: `run.py` ist `755`
- `grep -rn "sys.path" .`: nur `run.py`, Tests, `scripts/sync_config.py`, alle mit `src/`

Handtests bei dir (Schritt 1 und 2):
- Alt+Escape, Alt+Delete, tdrop-Whiteboard starten
- rofi-Nachfrage beim Schließen des Whiteboards hat das griffel-Theme
- `griffel --last`, `griffel --version` (ab Schritt 2)

## Entschieden (2026-10-14)

- Absolute Imports (`from griffel.canvas import Canvas`)
- Vier getrennte Commits, Schritt 1 nur Umbenennungen
