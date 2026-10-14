# Plan: Umbenennung slate → griffel

Ziel: Das Tool heißt `griffel`, überall: Befehl, Fenstertitel, Meldungen, Ordner,
Dateiformat, MIME-Typ, Doku und GitHub-Repo.

Warum (geprüft 2026-10-10): Im AUR sind `slate` (Qt-Pixel-Art-Editor) und `slate-git`
vergeben, auf PyPI `slate` (PDF-Textextraktion). `griffel` ist auf PyPI und im AUR frei,
`griffel-git` ebenso. Ein Griffel ist der Stift zur Schiefertafel, damit bleibt die
slate-Idee erhalten. Aussprache englisch „GRIF-ul“, fast wie im Deutschen. Für die README:
*"griffel (say GRIF-ul) is German for the stylus you write on a slate with."*
Namensvetter: `microsoft/griffel` (CSS-in-JS), andere Welt, kein Linux-Paket.

Zeitpunkt: vor Phase 1 von `plan-veroeffentlichung.md`, als eigener Commit, noch mit den
flachen Modulen. Phase 1 legt dann direkt `src/griffel/` an.

Anders als bei annotate → slate (`plan-umbenennung.md`): Seit 2026-10-02 gibt es echte
Zeichnungen und einen Verlauf. Darum eine einzige Stelle Rückwärtskompatibilität: Beim
Laden gilt der alte PNG-Schlüssel `slate` weiter. Die Ordner ziehen einmalig von Hand um,
dafür gibt es keinen Rückfall-Code.

## Vorher

- Offene Änderungen fertig machen und committen, auch die beiden noch ungetrackten Pläne
  (`plan-veroeffentlichung.md`, diese Datei), damit die Umbenennung ein eigener, sauberer
  Commit wird
- Erledigt 2026-10-10: `pacman -F /usr/bin/griffel` ohne Treffer, kein offizielles Arch-Paket
  bringt den Befehl mit

## Schritt 1: Dateiformat und Zwischenablage

- `document.py`: `FORMAT = "griffel"`, `PNG_KEY = "griffel"`. Neu `LEGACY_PNG_KEYS = ("slate",)`:
  `load_document` liest zuerst `griffel`, sonst `slate`, und nimmt beim Prüfen von `format`
  beide Werte an. Gespeichert wird immer unter `griffel`. Fehlermeldung „not a griffel
  document“, Docstring
- `canvas_output.py`: `ELEMENTS_MIME = "application/x-griffel-elements"`,
  `CLIP_FORMAT = "griffel-elements"`, `rich_copy_path()` → `$XDG_RUNTIME_DIR/griffel/clipboard.json`.
  Was vor der Umbenennung in der Zwischenablage lag, ist egal (nur vorübergehend)
- `export.py`: `default_output_dir()` → `~/Pictures/griffel`, Dateinamen `griffel_….png`,
  Docstring mit MIME-Typ
- `history.py`: `_NAME_RE` nur noch mit `griffel_`, Standardordner
  `$XDG_DATA_HOME/griffel/history`. Die alten Einträge werden in Schritt 4 umbenannt
- `tests/test_document.py`: `glob("griffel_*.png")`, `QImage.text("griffel")`. Neuer Fall: ein
  PNG mit dem Schlüssel `slate` lädt bearbeitbar

## Schritt 2: Startdatei, Befehl, Tests

- `git mv slate.py griffel.py` (behält `755`, mit `git diff --summary` prüfen), Docstring
  (Aufrufe `python griffel.py …`, Symlink)
- Bei dir, im Projektordner: `ln -sfn "$PWD/griffel.py" ~/.local/bin/griffel` (erst das Ziel, dann
  der Link; vertauscht überschreibt `-f` die echte Datei mit einem Symlink); den alten
  Symlink `~/.local/bin/slate` erst nach den Handtests entfernen
- Bei dir: `~/.config/herbstluftwm/keybindings.sxhkd`: `slate` → `griffel` (Alt+Escape,
  Alt+Delete, ggf. `--last`), danach `pkill -USR1 sxhkd`
- `tests/gui/harness.py`: `SLATE` → `GRIFFEL`, Prüfung `b"griffel.py"` in der Kommandozeile,
  `slate_pids()` → `griffel_pids()`, Präfix `griffel-gui-`, Config- und Verlaufsordner,
  `glob("griffel_*.png")`
- Aufrufe von `slate_pids` in allen `tests/gui/test_*.py` (blur, board, clipboard, connector,
  crop, help, label, marker, overlay, pointer, select, text_font)
- `tests/regress.py`: Präfix `griffel-test-`, `.config/griffel`

## Schritt 3: Sichtbare Namen

- `canvas_board.py`: Fenstertitel `griffel – Whiteboard – …`, Titel der Nachfrage beim Schließen
- `notify.py`: `--app-name=griffel` und Überschrift der Meldung. dunst-Regeln, die auf
  `slate` passen, müsstest du selbst anpassen
- `rofi/slate.rasi` → `rofi/griffel.rasi` (`git mv`), Pfad in `notify.py` (`ROFI_THEME`),
  Kommentar in `settings.py`
- `config.example.toml`: Kopf, Pfade (`~/.config/griffel`, `dir = "~/Pictures/griffel"`,
  `dir = "~/.local/share/griffel/history"`), rofi-Kommentare
- Docstrings und Kommentare in `colors.py`, `tools.py`, `config.py`
- `scripts/sync_config.py` (Hilfetext `--config`), `scripts/git-hooks/pre-commit` (Kommentar)

## Schritt 4: Ordner und Dateien (bei dir, von Hand)

| Alt | Neu | Was drin ist |
|---|---|---|
| `~/.config/slate/` | `~/.config/griffel/` | `config.toml` (+ `.bak`) |
| `~/.local/share/slate/history/` | `~/.local/share/griffel/history/` | Verlauf, Dateien umbenennen |
| `~/Pictures/slate/` | `~/Pictures/griffel/` | gespeicherte Bilder (optional, öffnen dank Schritt 1 weiter) |
| `$XDG_RUNTIME_DIR/slate/` | nichts tun | `clipboard.json`, nur vorübergehend |

```sh
mv ~/.config/slate ~/.config/griffel
mkdir -p ~/.local/share/griffel
mv ~/.local/share/slate/history ~/.local/share/griffel/history
cd ~/.local/share/griffel/history && for f in slate_*.png; do mv -- "$f" "griffel_${f#slate_}"; done
mv ~/Pictures/slate ~/Pictures/griffel   # optional
grep -n slate ~/.config/griffel/config.toml
```

Achtung bei der letzten Zeile: In `config.example.toml` stehen `[output] dir` und
`[history] dir` nicht auskommentiert, und der Git-Hook übernimmt die Vorlage in deine Config.
Stehen dort noch `slate`-Pfade, auf `griffel` ändern, sonst schreibt das Tool weiter in die
alten Ordner. Die Einträge im Verlauf enthalten intern noch den Schlüssel `slate`, das fängt
Schritt 1 ab.

## Schritt 5: Doku

- `README.md`: Titel, erste Zeile mit Aussprache (siehe oben), Befehle, Clone-URL
  (`wabohu/griffel`), Symlink, Pfade
- `docs/usage.md` (`python griffel.py …`), `docs/roadmap.md` (Hotkeys, Pfad des Verlaufs)
- `CLAUDE.md`: Projektname, `griffel.py`, Symlink `~/.local/bin/griffel`, Pfade, rofi-Theme,
  PNG-Schlüssel `griffel` (alter `slate` wird gelesen), MIME-Typ `application/x-griffel-elements`
- Alte Pläne (`plan-*.md`, auch `plan-umbenennung.md`) bleiben, wie sie sind: Sie beschreiben
  den Stand von damals. `plan-veroeffentlichung.md` ist schon auf griffel umgestellt

## Schritt 6: GitHub-Repo und Ordner (zuletzt)

- GitHub: Settings → Repository name → `griffel`. GitHub leitet alte URLs und Git-Remotes
  weiter, aber nur, solange du kein neues Repo `wabohu/slate` anlegst
- `git remote set-url origin git@github.com:wabohu/griffel.git`
- Pushen wie immer erst nach deiner Bestätigung
- Optional: Projektordner `slate` → `griffel`. Danach:
  - Symlink `~/.local/bin/griffel` neu setzen (zeigt sonst ins Leere)
  - Git-Hook bleibt aktiv (`core.hooksPath` ist relativ)
  - Claude-Code-Gedächtnis hängt am Pfad: den Projektordner von Claude Code (`projects/…-slate`)
    nach `…-griffel` umbenennen
  - Freigegebene Ordner in der Claude-App neu verbinden (der Pfad ändert sich)

## Prüfen

- `grep -rIwn slate --exclude-dir=.git .`: übrig bleiben dürfen nur die alten Pläne, diese
  Datei, die Fakten zum Namen in `plan-veroeffentlichung.md` und `LEGACY_PNG_KEYS` in `document.py`
- Alle Tests: `python tests/test_settings.py`, `python tests/test_document.py`,
  `python tests/regress.py` (Referenzbild ändert sich nicht, der Name taucht im Bild nicht
  auf), `python tests/gui/run.py`

Handtests bei dir:
- Alt+Escape und Alt+Delete starten griffel
- Deine Config-Werte gelten noch (Farben, Tasten)
- dunst-Meldung und Whiteboard-Fenstertitel heißen `griffel`
- Eine alte Zeichnung aus `~/Pictures/griffel` öffnet bearbeitbar
- Verlauf: ← zeigt die alten Einträge, Änderungen landen darin
- Elemente kopieren und in einem zweiten Fenster einfügen (neuer MIME-Typ)
- Neu gespeicherte Datei landet in `~/Pictures/griffel` und heißt `griffel_….png`

Ein Commit für Schritt 1–5 („Umbenennung slate → griffel“), Schritt 6 braucht keinen.
