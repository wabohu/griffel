# Plan: Wayland und andere Grenzen sauber melden (Veröffentlichung 2.6)

Stand: 2026-10-28, **umgesetzt**. Gesamtplan: `plan-veroeffentlichung.md`, Phase 2.6.

## Problem

Unter Wayland startet griffel scheinbar normal, aber:
- `grabWindow(0)` liefert je nach Compositor ein schwarzes oder leeres Bild (unter XWayland
  sieht X nur die X-Fenster, nicht den Desktop). Der Nutzer malt dann auf Schwarz und weiß nicht,
  warum
- Das Overlay hängt an X11-Eigenheiten: `X11BypassWindowManagerHint`, xdotool für den Fokus
- xclip erreicht unter XWayland je nach Compositor nur die X-Zwischenablage

Heute gibt es keine Meldung, nur „Wayland doesn't work.“ im README.

## Schon erledigt (beim Durchsehen festgestellt)

- Python ≥ 3.11: steht in `pyproject.toml` (`requires-python`) und im README. Ein PKGBUILD gibt es
  noch nicht, das kommt mit Phase 4
- Fehlendes `xclip`: `copy_to_clipboard` meldet schon bei jedem Kopieren „Copied to the clipboard
  (without xclip, possibly not permanent)“. Eine extra einmalige Meldung brauchen wir nicht

Bleibt also nur die Wayland-Prüfung.

## Erkennen

`wm.wayland_session(env=os.environ)` (Qt-frei, testbar):
- `WAYLAND_DISPLAY` gesetzt **oder** `XDG_SESSION_TYPE == "wayland"` → Wayland
- Wichtig: zuerst die Umgebung prüfen. Unter XWayland meldet Qt `platformName() == "xcb"`, das
  wäre der häufigste Fall und würde sonst durchrutschen

Zusätzlich in `app.py` nach dem Anlegen der `QApplication`: `platformName()` ist weder `xcb`
noch `offscreen` (z. B. `wayland` oder `eglfs`) → ebenfalls nicht unterstützt.

## Verhalten

| Start                          | unter Wayland                                           |
|--------------------------------|---------------------------------------------------------|
| `griffel` (Screenshot)         | Abbruch, Meldung, Exit-Code 2, **kein** Screenshot       |
| `griffel --board`              | erlaubt (normales Fenster, kein Screenshot, kein Bypass) |
| `griffel bild.png`, `--last`   | Abbruch wie oben (Overlay mit Bypass-Fenster und xdotool) |
| gespeichertes Whiteboard       | erlaubt (normales Fenster wie `--board`)                 |

Meldung (stderr und `notify`, weil oft per Hotkey ohne Terminal gestartet, wie bei `--last`):

> griffel needs an X11 session for screenshots (Wayland detected). The whiteboard works:
> griffel --board

Für Leute, deren Setup trotzdem geht (z. B. ein Compositor, der XWayland-Screenshots erlaubt),
ein Notausgang: Umgebungsvariable `GRIFFEL_IGNORE_WAYLAND=1` überspringt die Prüfung. Bewusst
keine Config-Option, das ist für Bastler und gehört nicht in `config.example.toml`; erwähnt im
README.

## Code

- `wm.py`: `wayland_session(env)` (die Datei ist ohnehin der Ort für „welche Umgebung läuft“)
- `app.py`: `unsupported_session(app)` → Text oder None (Umgebung, Notausgang, `platformName`);
  in `main()` vor `grab_screen()` bzw. vor dem Öffnen einer Datei; `--board` überspringt es
- README: Abschnitt Requirements/„Wayland doesn't work“ um die Meldung und
  `GRIFFEL_IGNORE_WAYLAND` ergänzen; `docs/usage.md`, falls dort Startoptionen stehen

## Tests

- `test_settings.py` (Qt-frei): `wayland_session` mit `WAYLAND_DISPLAY`, mit
  `XDG_SESSION_TYPE=wayland`, mit `x11`, leer
- `test_document.py` (offscreen): `griffel` als Unterprozess mit `WAYLAND_DISPLAY=wayland-0`
  → Exit-Code 2, Meldung auf stderr; mit `GRIFFEL_IGNORE_WAYLAND=1` keine Meldung
  (Abbruch per Timeout/`--version` reicht nicht, also nur bis zur Prüfung: z. B. eine nicht
  vorhandene Datei öffnen → Exit-Code 1 statt 2)
- GUI-Harness: unverändert, die X-Session dort hat kein `WAYLAND_DISPLAY`. Prüfen, dass der
  Harness die Variable nicht von außen erbt (falls du ihn mal aus einer Wayland-Sitzung startest)

## Handtest bei dir

Nichts Wayland-spezifisches nötig (du hast X11). Nur: normaler Start per Alt+Escape und
Alt+Delete geht wie vorher. Optional im Terminal:
`WAYLAND_DISPLAY=x griffel` → Meldung als Benachrichtigung, Programm startet nicht.

## Entschieden

- Datei öffnen unter Wayland: abbrechen (kein Overlay ohne Bypass). Gespeicherte Whiteboards
  öffnen trotzdem, die Prüfung sitzt erst im Overlay-Zweig nach dem Laden
- Tests anders als oben skizziert: `unsupported_session` direkt in `test_document.py` mit
  gesetzter Umgebung, dazu ein Unterprozess ohne Argumente → Exit-Code 2. Der Harness entfernt
  auch `XDG_SESSION_TYPE` und `GRIFFEL_IGNORE_WAYLAND` aus der Umgebung
