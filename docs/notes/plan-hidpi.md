# Plan: HiDPI – Elemente in Bildpixeln speichern (gefunden bei Veröffentlichung 2.8)

Stand: 2026-10-28, **umgesetzt** (Variante a).

## Befund (im Harness mit `QT_SCALE_FACTOR=2`, 1920×1080)

- `grabWindow(0)` liefert ein Pixmap mit 1920×1080 echten Pixeln und `devicePixelRatio` 2.
  Für Qt ist es damit 960×540 „logische“ Pixel groß, und die Szene richtet sich danach
- Ein Rechteck von Bildschirmpixel 400,300 bis 1000,700 liegt in der Szene bei 200,150 bis
  500,350. Auf dem Bildschirm und im fertigen PNG stimmt alles (Export rendert in voller
  Auflösung)
- Gespeichert wird aber: Hintergrund 1920×1080 (echte Pixel), Elemente in Szenenkoordinaten
  (logisch). Beim Wieder-Öffnen hat das Bild keinen `devicePixelRatio` mehr, die Szene ist
  1920×1080, und **alle Markierungen liegen bei halber Position und Größe**
  (Bild: Rechteck bei 200,150 bis 500,350 statt 400,300 bis 1000,700)
- Trifft auch auf demselben Rechner zu: Verlauf ← →, `--last`, Datei öffnen
- Betroffen: jeder mit Skalierung. Qt 6 skaliert unter X11 auch ohne `QT_SCALE_FACTOR`
  automatisch nach `Xft.dpi` (z. B. 4K mit 192 dpi → Faktor 2). Du (1080p, 96 dpi) nicht

## Idee

Szene immer in echten Bildpixeln, egal wie skaliert. Nach dem Screenshot
`pixmap.setDevicePixelRatio(1)`: Dann ist die Szene 1920×1080, `fit_overlay` sieht ein Bild,
das größer als der (logische) Bildschirm ist, und verkleinert die Ansicht auf 0,5. Genau
dieser Weg läuft heute schon beim Öffnen einer Datei von einem größeren Monitor. Frischer
Screenshot und wieder geöffnete Datei sind damit dasselbe, gespeichert wird in Bildpixeln.

Eine Zeile in `app.grab_screen` (und die alte Fallstrick-Notiz in CLAUDE.md anpassen).

## Nebenwirkung: Strichstärken und Schrift

Stärken und Schriftgrößen sind Szeneneinheiten. Bei Faktor 2 erscheinen sie danach auf dem
Bildschirm halb so dick wie heute (eine 4-px-Linie ist 4 echte Pixel statt 8). Das ist
dasselbe Aussehen wie heute bei einem unskalierten 4K-Monitor.

Zwei Möglichkeiten:
- **a) so lassen** (Vorschlag für jetzt): einfach, konsistent mit unskaliertem 4K. Wer es
  dicker will, stellt `[size]` um
- b) im Screenshot-Modus neue Stärken/Schriftgrößen mit dem Skalierungsfaktor
  multiplizieren. Mehr Code (Größenstufen, Anzeige in der Leiste, Vergleich „aktive Stufe“),
  später als eigener Schritt, falls (a) stört

Handles, Klicktoleranz, Andockabstand usw. laufen schon über `screen_px` (teilt durch den
Zoom), die bleiben auf dem Bildschirm gleich groß.

## Alte Dateien

Unter Skalierung gespeicherte Dateien von vorher bleiben falsch (nicht erkennbar, was
logisch war). Das Projekt ist frisch veröffentlicht, in Kauf nehmen.

## Tests

- GUI-Szenario `tests/gui/test_hidpi.py`: Harness mit `QT_SCALE_FACTOR=2` (Session bekommt
  einen Parameter `env`), Rechteck ziehen, Enter, Verlaufseintrag laden: Hintergrund
  1920×1080, Rechteck bei 400,300 bis 1000,700 in Bildpixeln; gerendertes PNG prüfen
- (entfallen: ein Canvas-Test mit `devicePixelRatio` 2 in `test_document.py` prüft nichts, die
  Korrektur sitzt in `grab_screen`; der GUI-Test deckt genau diesen Weg ab und schlägt ohne
  die Korrektur fehl)
- Alle bisherigen Tests unverändert (ohne Skalierung ändert sich nichts)

## Handtest bei dir

- `QT_SCALE_FACTOR=2 griffel`: etwas zeichnen, Enter, dann `QT_SCALE_FACTOR=2 griffel --last`
  und `griffel --last`: Markierungen jeweils an derselben Stelle. Strichstärke ok?
- Zwei Monitore (unabhängig davon, aus 2.8): auf jedem Monitor einmal Alt+Escape mit der Maus
  dort. Screenshot vom richtigen Monitor, Overlay deckt genau ihn ab, Leiste/Toast dort
