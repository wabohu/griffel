# Plan: Veröffentlichung (GitHub, Doku, AUR)

Stand: 2026-10-10 (nach Review überarbeitet). Ziel: griffel (bisher slate) so aufbereiten,
dass es auf fremden Rechnern ohne meine Config läuft, auf GitHub gut aussieht und als
AUR-Paket installierbar ist. Reihenfolge der Phasen ist bewusst: erst die Paketstruktur (mechanisch,
Phase 2 braucht sie schon), dann portabel machen, dann dokumentieren, dann paketieren.
Jede Phase endet lauffähig mit grünen Tests.

## Phase 0: Entscheidungen vorab
- **Name: entschieden, `griffel`** (2026-10-10). `slate` ist im AUR (`slate`, `slate-git`) und
  auf PyPI vergeben, `griffel` überall frei, auch `griffel-git`. Ein Griffel ist der Stift zur
  Schiefertafel; englisch „GRIF-ul“. Umbenennung vor Phase 1 als eigener Commit, Plan in
  `docs/notes/plan-umbenennung-griffel.md`. Paket, Befehl, Modul und Repo heißen gleich
- **Was öffentlich bleibt: entschieden** (2026-10-14). Alles bleibt öffentlich, aber getrennt:
  deutsche Arbeitsnotizen (`roadmap.md`, `plan-*.md`) in `docs/notes/` mit englischem Hinweis
  (`docs/notes/README.md`). `CLAUDE.md` wird englisch und enthält nur Projektwissen; meine
  persönlichen Arbeitsregeln (Sprache, Bestätigung vor Commit/Push, Handtests, Qt erklären,
  Symlink/sxhkd) stehen in `CLAUDE.local.md` (nicht im Repo, `.gitignore`). Englische
  `docs/architecture.md`/`CONTRIBUTING.md` in Phase 3, weitgehend aus `CLAUDE.md`
- **Repo:** `wabohu/slate` ist bereits öffentlich, alle 82 Commits auf `main` sichtbar (geprüft
  2026-10-10). Also keine History umschreiben, nur umbenennen in `wabohu/griffel` (GitHub
  leitet weiter). Autor ist die noreply-Adresse, keine Secrets gefunden
- **Versionierung:** SemVer, erstes Release `v0.1.0` (signalisiert: benutzbar, aber jung)
- **Lizenz: entschieden, `GPL-3.0-or-later`** (2026-10-14). SPDX in README (erledigt),
  `pyproject.toml` und PKGBUILD; optional eine Zeile `# SPDX-License-Identifier: GPL-3.0-or-later` je Datei

## Phase 1: Paketstruktur (Roadmap 20, flach) – erledigt 2026-10-15, siehe `plan-pakete.md`
Voraussetzung für pipx und AUR, weil 22 flache Module sonst als Top-Level-Module
(`ui`, `config`, `history` …) in `site-packages` landen würden – Namenskonflikte garantiert.
Bewusst vor Phase 2: rein mechanisch, und Phase 2 braucht schon Paketdaten
(`importlib.resources` für `griffel.rasi`) und `griffel.__version__`.

Für 0.1.0 flach: alle Module unverändert in ein Paket, ohne Unterordner. Das löst die
Namenskonflikte schon allein. Unterpakete (`canvas/`, `model/`, `config/` …) später, falls die
Dateiliste stört; sie brächten Namen wie `griffel.config.config` und `griffel.ui.ui` und zwei
`history`-Module in verschiedenen Paketen. Roadmap 20 bleibt dafür offen.

```
griffel/
├── pyproject.toml          # Metadaten, Lizenz (SPDX), Entry Point griffel = "griffel.app:main"
├── README.md  LICENSE  CHANGELOG.md  CONTRIBUTING.md
├── config.example.toml     # bleibt oben, gut auffindbar
├── run.py                  # Starter aus dem Quellordner (Symlink, sxhkd), siehe unten
├── src/griffel/
│   ├── __init__.py         # __version__
│   ├── __main__.py         # python -m griffel
│   ├── app.py              # heute griffel.py (nach der Umbenennung): main, grab_screen
│   ├── canvas.py  canvas_input.py  …  wm.py   # alle übrigen Module unverändert
│   └── data/griffel.rasi
├── share/                  # neu: griffel.desktop, griffel-board.desktop, Icon (svg), evtl. man page
├── docs/
├── scripts/dev/            # sync_config.py, git-hooks
└── tests/                  # unit/, gui/, regress
```
- `src/`-Layout verhindert, dass Tests aus Versehen den Quellordner statt des installierten
  Pakets importieren
- Starter im Wurzelordner **nicht** `griffel.py` nennen: Python setzt den Ordner des Skripts
  (Symlink aufgelöst) an den Anfang von `sys.path`, `from griffel.app import main` fände dann
  `griffel.py` selbst statt des Pakets. Darum `run.py`, das `src/` in `sys.path` einträgt und
  `griffel.app.main()` aufruft; Symlink `~/.local/bin/griffel` auf `run.py` umstellen. Alternative:
  installiertes Paket (AUR/pipx), dann Symlink weg
- Build-Backend: `setuptools` (in Arch als `python-setuptools`, kein Exot), keine
  Laufzeitabhängigkeiten in `pyproject` außer PySide6 (für pip/pipx), auf Arch kommt es per pacman
- Paketdaten: `griffel.rasi` landet nur im Wheel, wenn es eingetragen ist
  (`[tool.setuptools.package-data] griffel = ["data/*.rasi"]`); Zugriff per
  `importlib.resources.files("griffel.data")`
- Imports: aus `import history` wird `from griffel import history` (oder relativ)
- `--version` aus `griffel.__version__`, die einzige Stelle für die Version
- Betrifft auch `scripts/sync_config.py`, den Git-Hook, `tests/regress.py` (REPO-Pfad),
  `tests/gui/harness.py` und CLAUDE.md
- Plan dazu wie üblich vorher in `docs/notes/plan-pakete.md`, Umbau in kleinen Commits
  (erst verschieben, dann Imports, dann Tests, dann Entry Point)

## Phase 2: Abhängigkeiten zu meinem System lösen
Gefunden beim Durchsehen des Codes, sortiert nach Wirkung auf fremde Nutzer.

### 2.1 Was in gespeicherten Dateien steckt – erledigt 2026-10-15, siehe `plan-rohbild.md`
- Strg+S, Shift+Enter und der Verlauf speichern den ganzen Rohscreenshot als Base64 im
  PNG-Text-Chunk, auch außerhalb des Ausschnitts (`save_drawing` übergibt `crop` nur als Rahmen).
  Die Unschärfe wird eingebrannt, der Ausschnitt nicht. Wer so eine Datei weitergibt, weil sie
  zugeschnitten aussieht, gibt den ganzen Monitor weiter
- Der Verlauf hält standardmäßig die letzten 100 bearbeiteten Screenshots in
  `~/.local/share/griffel/history`
- Neu: Option (Name offen, z. B. `[output] keep_full = true | false`): bei `false` wird das
  Rohbild beim Speichern auf den Ausschnitt beschnitten, der Rahmen ist danach nicht mehr
  vergrößerbar. Elemente dafür verschieben oder einen Versatz des Hintergrunds speichern
  (Format-Version prüfen). Standard für 0.1.0 entscheiden, sicherer wäre `false`
- Doku: README (Abschnitt „Privacy“), `file-format.md`, `usage.md`: „Zum Weitergeben Strg+E
  (sauberes PNG ohne Bearbeitungsdaten)“, dazu Verlauf und `[history] keep`
- Test: `tests/test_document.py`, gespeichertes Rohbild hat bei `false` die Größe des Ausschnitts

### 2.2 Tastaturbild in der Übersicht (?) – Kyria/Vial – erledigt 2026-10-15, siehe `plan-tastaturbild.md`
- `ui.KEYBOARD_STAGGER = (0.78, 0.78, 0.26, 0.0, 0.26, 0.38)` ist der Spaltenversatz meiner
  Kyria, `shortcuts.KEYBOARD_COLUMNS` legt `tab`, `=`, `` ` `` in die äußere Spalte (Kyria-Belegung)
- Neu: `[help] keyboard = "row" | "column" | "ortho"`
  - `row` (Standard für alle): normale Reihenversetzung (ANSI/ISO), Zeilen statt Spalten
    versetzt (0, 0.25, 0.5 bzw. 0.75 Tastenbreiten), äußere Spalte `tab`/`caps`/`shift`
  - `column`: Spaltenversatz, Werte per `[help] stagger = [0.78, 0.78, 0.26, 0.0, 0.26, 0.38]`
    (meine Werte als Beispiel in `config.example.toml`)
  - `ortho`: ohne Versatz (Planck, Preonic)
  - optional `[help] outer_column = ["tab", "=", "`"]` für eigene Belegungen
- **Layout (QWERTZ, AZERTY, Dvorak):** Qt arbeitet mit Tastensymbolen, nicht Positionen.
  Auf QWERTZ liegt „z“ (Unschärfe) oben, das Bild zeigt es unten. `KEY_ROWS` ist fest QWERTY.
  Neu: `[help] layout = "qwerty" | "qwertz" | "azerty"` oder eigene `rows`. Nur die Anzeige,
  die Tasten selbst bleiben. In der README erwähnen: Standardbelegung ist für QWERTY gedacht,
  auf QWERTZ evtl. `[keys]` anpassen (Z/Y)
- In der äußeren Spalte liegt `` ` ``, auf QWERTZ eine Tottaste: prüfen, ob die Taste bei Qt
  ankommt, sonst die Standardbelegung dort ändern
- Kommentare „like my keyboard in Vial“ neutral formulieren
- Test: `tests/test_settings.py` (Werte, Fallbacks), `test_help.py` je ein Foto pro Variante

### 2.3 Farben und Monospace-Schrift aus Alacritty – erledigt 2026-10-17, siehe `plan-farben.md`
- Fallback existiert schon (Tomorrow Night), stürzt also nicht ab. Aber wer kein Alacritty
  nutzt, hat keinen Weg zur eigenen Palette außer `#rrggbb` an jeder Stelle
- Neu: `[palette]` in der eigenen Config (`red = "#..."`, `bright_red`, `foreground`,
  `background`), Vorrang vor Alacritty. Und `[colors] source = "auto" | "alacritty" | "builtin"`
- Später denkbar: weitere Quellen (kitty `kitty.conf`, foot, Xresources). Nicht für 0.1.0
- Doku: „Colors come from your Alacritty config, if you have one“ statt „from your Alacritty config“
- Default-Schrift für Monospace ohne Alacritty: `QFontDatabase.FixedFont` (gibt es schon, prüfen)

### 2.4 Fokus zurückgeben (wm.py) – herbstluftwm
- Heute nur mit `herbstclient`, sonst passiert nichts. Unter i3, bspwm, awesome, Openbox,
  Xfce, KDE/GNOME auf Xorg bleibt das Problem „kein Fenster hat den Fokus“ evtl. bestehen
- Neu, allgemein: beim Start das aktive Fenster merken (`_NET_ACTIVE_WINDOW` per
  `xdotool getactivewindow` oder `xprop -root`; PySide6 bietet dafür keine xcb-Schnittstelle), beim Schließen zurückgeben (`xdotool windowactivate`, Fallback
  `windowfocus`). herbstluftwm-Weg bleibt als eigener Fall, weil er Tag-Wechsel währenddessen
  berücksichtigt
- Folge: Außerhalb von herbstluftwm ist xdotool für den Fokus faktisch Pflicht, nicht optional
  (README, optdepends)
- `[wm] focus = "auto" | "herbstluftwm" | "ewmh" | "off"`, `auto` wählt anhand von
  `herbstclient` bzw. EWMH
- Bypass-Fenster (`X11BypassWindowManagerHint`) unter anderen WMs/Compositoren prüfen:
  Fokus per `activateWindow()`, Flackern, Overlay über Panels. Mindestens i3 und Xfce, ideal
  KDE/GNOME auf Xorg. Wenn es irgendwo hakt: `[ui] overlay = "bypass" | "fullscreen"`
- GUI-Harness: WM als Parameter (`Session(wm="i3")`), dann laufen `test_overlay` und
  `test_board` auch mit i3 bzw. ohne WM

### 2.5 rofi-Theme und `~/.config/rofi/colors.rasi`
- `griffel.rasi` erwartet Variablennamen meines Rofi-Setups (`base03`, `base02` …), sonst
  Tokyo-Night-Fallback, der nicht zur griffel-Palette passt
- Neu: Farben aus `ui.Theme` per `-theme-str` übergeben (Hintergrund, Vordergrund, Akzent),
  dann passt rofi immer zur Leiste. `colors.rasi` nur noch, wenn `[ui] rofi_colors` gesetzt ist
- Beim Paket: `griffel.rasi` als Paketdatei finden (siehe Phase 1, `importlib.resources`)

### 2.6 Wayland und andere Grenzen sauber melden
- Unter Wayland liefert `grabWindow(0)` je nach Compositor ein schwarzes Bild, xclip geht nicht
- Beim Start prüfen, zuerst `WAYLAND_DISPLAY` gesetzt oder `XDG_SESSION_TYPE == "wayland"`, erst
  danach `QGuiApplication.platformName()` nicht `xcb`. Unter XWayland meldet Qt ebenfalls `xcb`,
  das wäre sonst genau der häufigste Fall, der durchrutscht. Dann klare Meldung
  („griffel needs an X11 session“), Exit-Code 2. Für `--board`
  evtl. erlauben (geht ohne Screenshot, Zwischenablage über Qt-Fallback)
- Python ≥ 3.11 (wegen `tomllib`) in README und PKGBUILD
- Fehlendes `xclip`: Fallback auf Qt-Zwischenablage gibt es, aber das Bild verschwindet beim
  Beenden. Einmalige Meldung beim ersten Kopieren

### 2.7 Tastenkürzel, die mit anderen Setups kollidieren können
- Alt+A S D F, Alt+V, Alt+Rad: viele i3/Openbox-Nutzer haben Alt als Mod-Taste. Kein Code-
  Problem (alles per `[keys]` änderbar), aber in der Doku erwähnen
- Globale Hotkeys: Beispiele für sxhkd, i3, bspwm, awesome, KDE/GNOME (Einstellungen), xbindkeys

### 2.8 Kleinkram
- `--version` (Version aus `griffel.__version__`, siehe Phase 1)
- Standardpfade prüfen: `[output] dir`, Verlauf in `$XDG_DATA_HOME/griffel/history` (ok)
- Mehrere Monitore und HiDPI (`QT_SCALE_FACTOR=2`) – testest du; ich gebe dir die Fälle
- Deutsch im Code/UI suchen (`grep` auf Umlaute) – soll laut CLAUDE.md schon englisch sein

## Phase 3: Doku und README
### README (Englisch, wie bisher persönlich im Ton)
1. Ein Satz, was es ist + **GIF/Screenshots** oben (annotierter Screenshot, Whiteboard mit
   Verbindern, Tastenübersicht). Tipp: Der Xvfb-Harness kann Demo-Bilder reproduzierbar
   erzeugen (neues Skript `tests/gui/demo.py`, gibt es noch nicht), GIF per `ffmpeg`/`peek` aus deiner echten Session
2. Why – das Epic-Pen/Tekapoint-Motiv, kurz
3. Features (gibt es schon, gut)
4. Install: AUR (`yay -S …`), pipx, aus dem Quellcode
5. Quick start: Hotkey einrichten (Beispiele für 3–4 WMs/DEs als aufklappbare `<details>`)
6. Configuration, Privacy (was gespeicherte Dateien und der Verlauf enthalten, Phase 2.1),
   Limitations (X11 only, getestet auf …), Contributing, License
- Requirements korrigieren: Das Arch-Paket heißt `pyside6`, nicht `python-pyside6` (steht so
  auch in CLAUDE.md)
- Badges sparsam: AUR-Version, Lizenz, CI

### docs/ (Englisch, öffentlich)
- `usage.md`: heute eine Bullet-Wand. Gliedern (Tools, Selecting, Text and labels,
  Connectors, Crop, Output, Whiteboard, History, Pointing) mit Tabellen „Key | Action“
- `configuration.md`: aus `config.example.toml` abgeleitet, mit Beispielen (Kyria-Stagger,
  eigene Palette, QWERTZ)
- `integration.md`: Hotkeys je WM, dunst/rofi, Fokus-Verhalten
- `file-format.md`: PNG mit JSON im Text-Chunk – für andere Tools interessant. Deutlich sagen,
  dass der ganze Rohscreenshot drinsteckt (Phase 2.1)
- `troubleshooting.md`: schwarzer Screenshot (Wayland), kein Fokus nach Schließen (xdotool fehlt),
  Zwischenablage leer nach Beenden (xclip fehlt), unscharf auf HiDPI
- `architecture.md`: englische Kurzfassung aus CLAUDE.md (Canvas + Mixins, Undo, Datenmodell)
- Optional später: GitHub Pages mit MkDocs Material aus demselben `docs/`

### Projekt-Dateien
- `CHANGELOG.md` (Keep a Changelog), `CONTRIBUTING.md` (Tests, Konventionen, Git-Hook)
- Man page `griffel.1` (aus argparse via `argparse-manpage` oder kurz von Hand in scdoc)

## Phase 4: GitHub
- Repo: Beschreibung, Topics (`screenshot`, `annotation`, `whiteboard`, `x11`, `pyside6`,
  `linux`, `tiling-wm`), Social-Preview-Bild
- Issue-Vorlagen: Bug (Distro, WM, X11/Wayland, `griffel --version`, Qt-Version), Feature
- CI (GitHub Actions): `test_settings`, `test_document`, `regress` mit
  `QT_QPA_PLATFORM=offscreen`. Achtung: `regress.py` vergleicht Pixel, Schriften im Runner
  rendern anders → Toleranz oder feste Schrift im Test. GUI-Tests optional in einem Job mit
  `xvfb herbstluftwm sxhkd xdotool` (Arch-Container `archlinux:latest`, dann passt es zum AUR)
- Release: Tag `v0.1.0`, GitHub-Release mit Notes aus dem CHANGELOG. Der automatisch
  erzeugte Tarball ist die Quelle fürs AUR

## Phase 5: AUR
### Pakete
- `griffel` aus dem Release-Tarball, später evtl. `griffel-git` aus `main` (ebenfalls frei)
- Skizze PKGBUILD:
```bash
pkgname=griffel          # Repo heißt gleich: der GitHub-Tarball entpackt nach griffel-$pkgver
pkgver=0.1.0
pkgrel=1
pkgdesc="Screenshot annotation tool and whiteboard for X11"
arch=('any')
url="https://github.com/wabohu/griffel"
license=('GPL-3.0-or-later')
depends=('python>=3.11' 'pyside6' 'xclip')
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
optdepends=('xdotool: give the focus back on close (needed outside herbstluftwm)'
            'libnotify: notifications via notify-send'
            'rofi: prompts with fuzzy search')
source=("$pkgname-$pkgver.tar.gz::$url/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')      # Platzhalter, vor jedem Push: updpkgsums

build() {
  cd "$pkgname-$pkgver"
  python -m build --wheel --no-isolation
}
check() {
  cd "$pkgname-$pkgver"
  # Das Paket ist hier noch nicht installiert: aus src/ importieren
  export PYTHONPATH="$PWD/src" QT_QPA_PLATFORM=offscreen
  python tests/test_settings.py
  python tests/test_document.py
}
package() {
  cd "$pkgname-$pkgver"
  python -m installer --destdir="$pkgdir" dist/*.whl
  install -Dm644 config.example.toml -t "$pkgdir/usr/share/doc/$pkgname/"
  install -Dm644 share/*.desktop -t "$pkgdir/usr/share/applications/"
  install -Dm644 share/griffel.svg "$pkgdir/usr/share/icons/hicolor/scalable/apps/griffel.svg"
}
```
- PySide6 heißt in Arch `pyside6` (`extra/pyside6`) und stellt nur `qt6-python-bindings` bereit,
  kein `python-pyside6` (geprüft 2026-10-10). Also `pyside6` in `depends`
- Lizenz-Angabe als SPDX, wie in Phase 0 entschieden (Header gibt es bisher keine)
- `sha256sums` nie mit `SKIP` pushen: nach jedem neuen Tag `updpkgsums`
- `griffel.rasi` muss als Paketdaten im Wheel landen (Phase 1), sonst fehlt es im installierten Paket
- Icon und `.desktop`-Dateien (`share/`) gibt es noch nicht, vor dem ersten Paket anlegen

### Ablauf
1. AUR-Konto, SSH-Key hinterlegen
2. Lokal: `makepkg -si`, `namcap PKGBUILD` und `namcap *.pkg.tar.zst`
3. Sauber bauen im Chroot: `extra-x86_64-build` (devtools) – findet fehlende Abhängigkeiten
4. `makepkg --printsrcinfo > .SRCINFO`
5. `git clone ssh://aur@aur.archlinux.org/griffel.git`, PKGBUILD + .SRCINFO, commit, push
6. Testinstallation per `yay -S griffel` auf einem frischen System/VM (z. B. Arch in einer VM
   mit i3 – gleichzeitig der Fremd-Setup-Test aus Phase 2)
- Pflege: neues Release → `pkgver` hoch, `pkgrel=1`, `updpkgsums`, `.SRCINFO`, push.
  PKGBUILD zusätzlich im Repo unter `packaging/aur/` ablegen (Kopie, nicht die Quelle)

## Phase 6: Generalprobe
- Frische Arch-VM (oder Container mit Xvfb) mit i3 und ohne Alacritty/rofi/dunst:
  Installation nur nach README, Checkliste: Start per Hotkey, Fokus nach Schließen,
  Farben, Übersicht (?), Kopieren, Speichern (mit Ausschnitt: was steckt im Rohbild?), Verlauf,
  Whiteboard
- Zweiter Durchgang mit Xfce oder KDE auf Xorg, einmal unter Wayland (Fehlermeldung)
- Dann Release `v0.1.0`, AUR-Push, evtl. Ankündigung (r/unixporn, r/archlinux, herbstluftwm-Community)

## Offene Fragen
- Unterstützte Ziele für 0.1.0: Vorschlag „X11 + beliebiger WM, getestet mit herbstluftwm und i3“,
  KDE/GNOME auf Xorg als „sollte gehen“, damit der Bypass-Fokus das Release nicht aufhält
- pipx/PyPI zusätzlich zum AUR? Der Name `griffel` ist auf PyPI frei
- ~~Gespeicherte Dateien: ganzes Rohbild behalten oder beschneiden~~ Entschieden 2026-10-15:
  Option `[output] keep_full_screenshot`, Standard `false` (beschneiden), Verlauf behält alles
