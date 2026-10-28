# Plan: Doku für die Veröffentlichung (Phase 3)

Stand: 2026-10-28, Schritt 1 (`usage.md`) **umgesetzt**, Schritte 2 und 3 offen. Gesamtplan: `plan-veroeffentlichung.md`, Phase 3.

Entschieden: nur AUR, kein PyPI/pipx.

## Schritt 1: `docs/usage.md` nach Funktionen statt nach Tasten

### Problem heute
35 lange Aufzählungspunkte, jeder beginnt mit einer Taste. Wer wissen will „wie schneide ich
zu“ oder „was steckt in der gespeicherten Datei“, muss alles lesen. Dazwischen
Implementierungsdetails (`PropertyCommand` mit `mergeWith`, `Canvas.set_board_color`), die
nicht in eine Benutzerdoku gehören, und ein Verweis auf die deutschen Arbeitsnotizen.

### Neue Gliederung
Jeder Abschnitt erklärt eine Funktion: wozu, wie (Schritte), Tasten in einer kleinen Tabelle,
Feinheiten am Ende. Kurze Sätze, Tasten in `<kbd>`.

1. **Overview**: zwei Modi (Screenshot, Whiteboard), wie man startet und beendet,
   die Leiste, `?` für die Tastenübersicht. Hinweis: alle Tasten änderbar (`[keys]`)
2. **Drawing**: Werkzeuge als Tabelle (Werkzeug | Taste | was es macht), dann Farbe
   (Shift+Taste, Tab), Größe (Alt+Taste, Alt+Rad), Mauszeiger
   - Text und Monospace
   - Geschwungener Pfeil
   - Marker (1 2 3 / A B C)
   - Blur (nur Screenshot)
3. **Selecting and editing**: auswählen (Klick, Shift, Rahmen, Ctrl+A), verschieben
   (Maus, hjkl), Größe ändern, drehen, Reihenfolge, löschen, Farbe/Größe der Auswahl,
   Rückgängig
4. **Text in shapes and on arrows** (Beschriftungen)
5. **Connectors** (nur Whiteboard)
6. **Crop and clearing an area** (nur Screenshot): zuschneiden, anpassen, Fläche leeren
7. **Copy, save, export**: Tabelle „Taste | was passiert | was die Datei enthält“
   (Enter, Ctrl+C, Shift+Enter, Ctrl+S, Ctrl+E), danach: Dateien wieder öffnen,
   was gespeichert wird (Ausschnitt, `keep_full_screenshot`, Blur eingebrannt)
8. **Copying elements and pasting images** (zwischen Screenshot und Whiteboard,
   Bilder aus anderen Programmen, Duplizieren)
9. **Whiteboard**: Ansicht (Rad, Zoom, Übersicht), Hintergründe, Speichern-Abfrage beim Schließen
10. **History**: was wann gespeichert wird, ← →, `--last`, Ordner und Anzahl
11. **Pointing**: Spotlight und Lupe
12. **Command line**: `griffel`, `FILE`, `--board`, `--last`, `--version`, Exit-Codes,
    Wayland und `GRIFFEL_IGNORE_WAYLAND`
13. **Key reference**: alle Standardtasten auf einen Blick, gruppiert wie die Übersicht (?),
    zum Nachschlagen. Die einzige Stelle, die nach Tasten geordnet ist

Implementierungsdetails fliegen raus (stehen schon in `CLAUDE.md`, sonst dorthin).

### Damit es aktuell bleibt
Test in `test_settings.py`: jede Aktion aus `DEFAULT_KEYS` (mit Taste) kommt in der
Tastenreferenz (Abschnitt 13) mit ihrer Taste vor. Neue Taste ohne Doku → Test rot. Die
CLAUDE.md-Regel „usage.md aktuell halten“ bekommt damit einen Wächter.

### Ablauf
Ich schreibe die ganze Datei neu (Inhalt aus der alten, nichts geht verloren), du liest sie
in der Markdown-Vorschau. Kein Code betroffen außer dem Test.

## Schritt 2: README

Nach dem Plan in `plan-veroeffentlichung.md`, angepasst:
- Oben 2–3 Bilder: annotierter Screenshot, Whiteboard mit Verbindern, Tastenübersicht.
  Erzeugt reproduzierbar im Harness (`tests/gui/demo.py`), damit sie bei Änderungen neu
  gemacht werden können. Ein GIF aus deiner echten Session wäre schöner, machst du optional
- Install: AUR (`yay -S griffel`) und aus dem Quellcode. Das AUR-Paket gibt es erst nach
  Phase 5; bis dahin steht es als „coming“ drin oder der Abschnitt kommt mit Phase 5
- Limitations / Tested on (siehe „Ziele für 0.1.0“ unten)
- Requirements prüfen (Paketname `pyside6` stimmt schon)

## Schritt 3: weitere Dateien, abgespeckt

| Datei                    | Inhalt                                                    | Vorschlag |
|--------------------------|-----------------------------------------------------------|-----------|
| `docs/troubleshooting.md`| schwarzer Screenshot, kein Fokus, leere Zwischenablage, Alt-Tasten, HiDPI | ja |
| `docs/file-format.md`    | PNG mit JSON im Text-Chunk, was drinsteckt                 | ja, kurz  |
| `CHANGELOG.md`           | 0.1.0 = erste Version, kurze Featureliste                  | ja        |
| `CONTRIBUTING.md`        | Tests, Git-Hook, Sprache, Verweis auf CLAUDE.md            | ja, kurz  |
| `docs/configuration.md`  | `config.example.toml` ist schon vollständig kommentiert    | nein      |
| `docs/integration.md`    | Hotkeys stehen jetzt im README                             | nein      |
| `docs/architecture.md`   | `CLAUDE.md` ist englisch und öffentlich                    | nein      |
| Man page                 | nett fürs AUR-Paket, kein Muss                             | später    |

## Ziele für 0.1.0 (die offene Frage aus `plan-veroeffentlichung.md`)

Gemeint ist: Was versprechen wir im README unter „Limitations“ bzw. „Tested on“, und was
muss vor dem Release in Phase 6 (Testdurchgang in frischer Umgebung) funktionieren?
Vorschlag:
- **Unterstützt und getestet:** Arch Linux, X11, herbstluftwm und i3
- **Sollte gehen, nicht getestet:** andere Fenstermanager und Desktops unter Xorg
  (KDE, Xfce, GNOME on Xorg); dort ist vor allem die Fokus-Rückgabe das Risiko
- **Nicht unterstützt:** Wayland (Meldung, nur Whiteboard)

Damit hält ein Fokus-Problem unter KDE das Release nicht auf, und Bug-Reports von dort sind
willkommen statt peinlich.
