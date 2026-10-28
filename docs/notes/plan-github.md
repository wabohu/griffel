# Plan: GitHub (Veröffentlichung Phase 4)

Stand: 2026-10-28, **umgesetzt** (Teile 2–4; Teil 1 machst du in der Weboberfläche). GUI-Tests in der CI: ja; Release per Workflow: ja. Gesamtplan: `plan-veroeffentlichung.md`, Phase 4.

Vier Teile. Was ich nicht selbst machen kann: `gh` ist nicht installiert, und Repo-
Einstellungen gehen nur über die Weboberfläche. Das machst du, ich liefere die Texte.

## 1. Repo-Angaben (machst du, Settings → General bzw. „About“ auf der Startseite)

- **Description:** `Screenshot annotation tool and whiteboard for X11, made for the keyboard and tiling window managers`
- **Topics:** `screenshot`, `annotation`, `whiteboard`, `x11`, `linux`, `pyside6`, `qt6`,
  `tiling-window-manager`, `herbstluftwm`, `i3`
- **Social preview** (Bild, das bei Links in Chats/Foren erscheint, 1280×640):
  `tests/gui/demo.py` erzeugt zusätzlich `docs/images/social.png` (Ausschnitt aus dem
  markierten Terminal mit Namen und Einzeiler). Hochladen unter Settings → Social preview
- Releases und Packages in der Seitenleiste lassen, Wiki und Projects ausschalten
  (die Doku liegt in `docs/`)

## 2. Issue-Vorlagen (`.github/ISSUE_TEMPLATE/`)

GitHub-Formulare (YAML), damit die nötigen Angaben gleich mitkommen:
- `bug.yml`: griffel-Version (`griffel --version`), Distribution, Fenstermanager/Desktop,
  X11 oder Wayland, was getan / erwartet / passiert, Terminalausgabe (Feld mit Codeblock).
  Hinweis oben: erst `docs/troubleshooting.md` lesen
- `feature.yml`: was willst du tun, wie machst du es heute
- `config.yml`: leere Issues erlaubt (für alles andere), Link auf die Doku

Dieselben Angaben wie in `CONTRIBUTING.md`, „Reporting a bug“.

## 3. CI (GitHub Actions, `.github/workflows/tests.yml`)

Läuft bei jedem Push auf `main` und bei Pull Requests. Alles in einem
**`archlinux:latest`-Container**: dieselben Pakete wie beim Nutzer und im AUR (`pyside6` aus
pacman), kein pip.

**Job `tests`** (schnell, ca. 2 min):
- `pacman -Syu --noconfirm python pyside6 ttf-droid python-build python-setuptools python-wheel`
- `test_settings.py`, `test_document.py`, `regress.py` (alle ohne Bildschirm)
- Paket bauen: `python -m build --wheel --no-isolation`, prüfen, dass `griffel.rasi` im Wheel
  ist (sonst fehlt es nach der AUR-Installation, Phase 5)

**Job `gui`** (langsam, ca. 6–8 min, parallel):
- zusätzlich `xorg-server-xvfb herbstluftwm sxhkd xdotool xclip imagemagick i3-wm`
- `python tests/gui/run.py`; die Screenshots aus `tests/gui/out/` als Artefakt hochladen,
  bei Fehlern zum Anschauen

**Ergebnis (lokal im Container geprüft):** Die Referenz ist nicht mit Droid Sans gerendert,
sondern mit DejaVu Sans: `regress.py` läuft mit leerem HOME, deine Schriftvorgabe in
`~/.config/fontconfig` greift dort nicht, fontconfig nimmt DejaVu. Mit `ttf-dejavu` im
Container ist das Bild pixelgleich, eine Toleranz braucht es nicht.

**Knackpunkt `regress.py` (Entwurf):** vergleicht Pixel genau. Die Referenz ist bei dir mit Droid Sans
gerendert (deine Standardschrift, `fc-match sans-serif`). Im Container installiere ich
`ttf-droid`, damit dort dieselbe Schrift gewählt wird. Freetype und Qt sind auf Arch bei
dir und im Container gleich alt, solange du aktuell bist. Weicht es trotzdem ab (andere
Kantenglättung, neuere Qt-Version im Container als bei dir):
- Vorschlag: `regress.py` bekommt eine Toleranz (Anteil abweichender Pixel, z. B. 0,5 %),
  die nur in der CI gilt (`--tolerance`). Lokal bleibt der exakte Vergleich
- Erst ausprobieren, dann entscheiden. Ich baue die Toleranz nur ein, wenn die CI sie braucht

**Wackelige GUI-Tests:** `test_curve` war schon einmal wackelig (behoben). Schlägt in der
CI ein GUI-Test sporadisch fehl, bekommt `run.py` einen einzigen Wiederholungsversuch pro
Szenario mit deutlicher Meldung („passed on retry“), statt rot zu bleiben. Auch das erst,
wenn es nötig ist.

Badge im README danach: Teststatus (der aus Phase 3 offen gebliebene Punkt).

## 4. Release-Ablauf (vorbereiten, ausgelöst erst nach Phase 6)

Laut Gesamtplan kommt das Release erst nach der Generalprobe (Phase 6). Jetzt nur
vorbereiten:
- **Workflow `.github/workflows/release.yml`:** bei einem Tag `v*` laufen die Tests, dann
  wird ein GitHub-Release angelegt, Text = der Abschnitt dieser Version aus `CHANGELOG.md`
  (kleines Skript `scripts/changelog_section.py`, Qt-frei, mit Test). Prüft auch, dass Tag
  und `griffel.__version__` übereinstimmen, sonst Abbruch
- **Ablauf fürs Release** (schreibe ich in `CONTRIBUTING.md`, Abschnitt „Releasing“):
  1. `__version__` in `src/griffel/__init__.py` auf `0.1.0` (heute `0.1.0.dev0`)
  2. In `CHANGELOG.md` „unreleased“ durch das Datum ersetzen
  3. Commit, `git tag -a v0.1.0 -m "griffel 0.1.0"`, `git push origin main v0.1.0`
  4. Der Workflow legt das Release an; der Tarball darunter ist die Quelle fürs AUR
- Danach `__version__` auf `0.2.0.dev0` und ein neuer Abschnitt „unreleased“

Nur `main` und Tags `v*` pushen, nie die Sicherungs-Branches.

## Reihenfolge und Tests

1. Issue-Vorlagen + Social-Preview-Bild (klein, sofort)
2. CI-Workflow; nach dem Push schauen wir gemeinsam auf den ersten Lauf (Actions-Tab).
   Toleranz/Wiederholung nur bei Bedarf
3. Release-Workflow + `changelog_section.py` + Test in `test_settings.py`; ausprobieren
   ohne echtes Release: Workflow-Lauf mit einem Test-Tag auf einem Fork wäre sauber, ist
   aber Aufwand. Vorschlag: Skript lokal testen, Workflow erst beim echten Release scharf
4. Du: Beschreibung, Topics, Social Preview, Wiki/Projects aus

Für die CI braucht es keine Geheimnisse (Tokens): Der Release-Workflow nutzt das
eingebaute `GITHUB_TOKEN`.

## Offene Fragen

- GUI-Tests in der CI: ja (Vorschlag), oder nur die schnellen Tests?
- Release automatisch per Workflow (Vorschlag) oder von Hand über die Weboberfläche?
