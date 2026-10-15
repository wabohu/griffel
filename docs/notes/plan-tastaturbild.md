# Plan: Tastaturbild der Übersicht für alle Tastaturen (Veröffentlichung 2.2)

Stand: 2026-10-15. Gesamtplan: `plan-veroeffentlichung.md`, Phase 2.2.

## Heute

- Die Übersicht (?) zeigt die linke Tastaturhälfte mit 6 Spalten × 3 Reihen wie auf meiner Kyria:
  `shortcuts.KEYBOARD_COLUMNS` (äußere Spalte `tab`, `=`, `` ` ``, dann `q a z` … `t g b`) und
  `ui.KEYBOARD_STAGGER` (Spaltenversatz). Kommentare „like my keyboard in Vial“
- Fest QWERTY: `KEYBOARD_COLUMNS` und `ui.KEY_ROWS` (sortiert die Farbfelder nach Tastaturreihe)
- Wer eine normale Tastatur hat, sieht ein fremdes Bild. Auf QWERTZ liegt „z“ (Unschärfe) oben
  rechts neben „t“, das Bild zeigt es unten links

## Neu in der Config

```toml
[help]
# Keyboard picture in the overview (?). Only the picture, the keys themselves stay as they are.
keyboard = "row"        # "row" = normal keyboard (rows offset), "column" = column stagger
                        # (split keyboards like Corne, Kyria), "ortho" = no offset (Planck)
layout = "auto"         # "auto" (from setxkbmap), "qwerty", "qwertz", "azerty"
# Only for keyboard = "column": how far each of the 6 columns sits lower, in key heights
# stagger = [0.78, 0.78, 0.26, 0.0, 0.26, 0.38]
# Keys of the outer column (top to bottom), default "tab" and two empty ones
# outer_column = ["tab", "=", "`"]
```

- Standard für alle: `row` und `auto`. Bei dir kommen `keyboard = "column"`, deine `stagger`
  und `outer_column = ["tab", "=", "`"]` in die eigene Config, dann sieht es aus wie heute
- Achtung beim Commit: Der Git-Hook übernimmt neue Schlüssel mit den Werten der Vorlage, also
  `row`. Deine drei Werte trage ich vorher in deine Config ein (nach Rückfrage), sonst siehst du
  danach die normale Tastatur

## Die drei Bilder

Alle zeigen die linke Hälfte: äußere Spalte + 5 Buchstaben je Reihe, 3 Reihen.

- **row** (ANSI): Reihen versetzt wie auf einer normalen Tastatur, Buchstabenreihen um 0, 0.25,
  0.75 Tastenbreiten nach rechts. Außen breitere Tasten `tab`, `caps`, `shift`, rechtsbündig vor
  der ersten Buchstabentaste. `caps` und `shift` sind nur Beschriftung (nicht belegbar, blass)
- **column**: wie heute, Versatz aus `stagger` (Standard: meine Werte), außen `outer_column`
- **ortho**: Raster ohne Versatz, außen `outer_column`
- ISO-Tastaturen haben links unten eine Taste mehr (`<`), das Bild zeigt trotzdem ANSI. Reicht,
  weil dort standardmäßig nichts liegt

## Layout

- Buchstaben der linken Hälfte je Layout:
  - qwerty `qwert asdfg zxcvb`
  - qwertz `qwert asdfg yxcvb` (z liegt rechts von t, also außerhalb des Bildes: die Unschärfe
    steht dann in der Liste daneben, wie alle Tasten ohne Platz im Bild)
  - azerty `azert qsdfg wxcvb`
- `auto`: `setxkbmap -query` lesen (bei dir: `layout: us`). `de`, `at`, `ch`, `cz`, `hu`, `sk`,
  `si`, `hr` → qwertz, `fr`, `be` → azerty, sonst und ohne setxkbmap → qwerty. Bei mehreren
  Layouts (`us,de`) das erste. Einmal pro Start, kein Neustart bei Layoutwechsel
- `ui.KEY_ROWS` (Farbfelder nach Reihe) kommt aus demselben Layout: Auf QWERTZ steht Shift+Z
  (Farbe 6) dann in der oberen Reihe
- Tottasten: `` ` `` ist standardmäßig nicht belegt, also kein Problem. Wer es belegt und eine
  Tottaste hat, bekommt das Zeichen evtl. erst mit der nächsten Taste, Hinweis im Kommentar zu
  `[keys]`

## Code

- Neues Modul `keyboard.py` (Qt-unabhängig, testbar): `layout_letters(name)`,
  `detect_layout()` (setxkbmap), `keyboard_caps(kind, letters, stagger, outer)` →
  Liste `(key, x, y, width, bindable)` in Tasteneinheiten. Daraus zeichnet `HelpPanel`, statt
  selbst mit `KEYBOARD_COLUMNS`/`KEYBOARD_STAGGER` zu rechnen; Breite und Höhe des Bildes ergeben
  sich aus den Kappen
- `shortcuts.keyboard()` und `overview()` bekommen die Tasten des Bildes als Parameter statt
  `KEYBOARD_KEYS` (was im Bild steht, fehlt in den Listen)
- `Settings`: `help_keyboard`, `help_layout` (`auto` erst beim Öffnen der Übersicht aufgelöst,
  `picture_layout()`: kein setxkbmap-Aufruf beim Start), `help_stagger`
  (6 Zahlen 0–3, sonst Standard mit Hinweis), `help_outer` (3 Einträge, Text, leer erlaubt)
- `KEYBOARD_COLUMNS`, `KEYBOARD_STAGGER`, `KEY_ROWS` fallen weg bzw. werden Standardwerte in
  `keyboard.py`, Kommentare neutral („split keyboard“ statt „my keyboard in Vial“)

## Prüfen

- `test_settings.py`: Standardwerte, gültige Werte, kaputte Werte (`keyboard = "foo"`, falsche
  Anzahl in `stagger`), `detect_layout` mit nachgebildeter Ausgabe von setxkbmap (`us`, `de`,
  `fr`, `us,de`, nicht vorhanden)
- Bestehender Test „keine Taste fehlt in der Übersicht“ für alle drei Bilder und alle Layouts
- `test_document.py` (offscreen, schneller als je eine X-Sitzung): ein Foto je Bild (`row`,
  `column`, `ortho`) und eins für qwertz, in `tests/gui/out/help-keyboard/`. Ansehen musst du sie, Geschmack prüft kein Test
- Handtest bei dir: ? mit deiner Config (soll aussehen wie heute), einmal ohne die drei Werte

## Doku

- `config.example.toml`: Abschnitt `[help]`, deine Kyria-Werte als Beispiel
- README, Abschnitt Configuration: „Default keys are laid out for QWERTY; on QWERTZ you may want
  to swap z and y under `[keys]`“
- `docs/usage.md` (?), `CLAUDE.md` (Tastaturbild, neues Modul)
