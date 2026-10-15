# Plan: Gespeicherte Dateien auf den Ausschnitt beschneiden (Veröffentlichung 2.1)

Stand: 2026-10-15. Entschieden: neue Option, Standard „beschneiden“. Gesamtplan:
`plan-veroeffentlichung.md`, Phase 2.1.

## Problem

Strg+S und Shift+Enter speichern im PNG-Text-Chunk den ganzen Rohscreenshot
(`build_document(self.background_to_save(), …, self.crop_rect)` in `canvas_output.save_drawing`).
Der Ausschnitt ist nur ein Rahmen. Die Datei sieht zugeschnitten aus, enthält aber den ganzen
Monitor. Die Unschärfe ist schon sicher, sie wird eingebrannt (`background_to_save`).

## Option

```toml
[output]
# Editable files (Ctrl+S, Shift+Enter) with a crop: false = only the crop is stored, the
# frame cannot be enlarged after opening again. true = the whole screenshot is stored
# (the frame stays changeable), but whoever gets the file can read the whole screen.
keep_full_screenshot = false
```

- `Settings.keep_full_screenshot` (bool, Standard `false`), Test in `test_settings.py`
- Gilt nur für Strg+S und Shift+Enter, **nicht für den Verlauf**: Der liegt nur lokal
  (`~/.local/share/griffel/history`), und dort ist gerade das spätere Vergrößern des Rahmens
  der Nutzen (`griffel --last`, ← / →). Kommentar unter `[history]`: Einträge enthalten den
  ganzen Screenshot
- Ohne Ausschnitt ändert sich nichts. Whiteboard ebenfalls nicht (kein Rohbild)

## Beschneiden beim Speichern

Neu in `document.py`, Qt-unabhängig testbar:
`crop_document(background, elements, crop, factor)` bzw. direkt in `build_document` mit einem
Parameter `cut=True`:

1. Rohbild (Unschärfe schon eingebrannt) auf den Ausschnitt kopieren:
   `image.copy(crop * factor)`, `factor` = Pixel pro Szenen-Einheit (wie in `output_area`)
2. Elemente, die den Ausschnitt **gar nicht** berühren, weglassen (`sceneBoundingRect()`
   schneidet `crop` nicht). Sonst stünde z. B. ein Text neben dem Ausschnitt weiter in der Datei.
   Teilweise drinliegende bleiben ganz erhalten (wie beim Rendern, nur abgeschnitten sichtbar)
3. Alle übrigen Elemente um `-crop.topLeft()` verschieben: nur `"pos"` im Dict ändern, Punkte
   sind relativ dazu, Verbinder hängen per `id` an ihren Zielen. Ein Verbinder, dessen Ziel
   weggelassen wurde, gilt beim Laden als frei (gibt es schon, `connectors.py`)
4. Kein `"crop"`-Schlüssel mehr: Die Datei ist danach einfach ein kleinerer Screenshot

- **Format-Version bleibt 1**: Es kommt kein neues Feld dazu, ältere griffel-Versionen
  öffnen solche Dateien ohne Weiteres
- Im laufenden Programm ändert sich nichts: Rohbild und Rahmen bleiben im Speicher, der
  Rahmen bleibt bis zum Beenden veränderbar. Ein weiteres Strg+S nach Vergrößern speichert den
  größeren Ausschnitt (das Rohbild im Speicher ist ja noch ganz)
- Eine geöffnete Datei mit ganzem Rohbild und Rahmen (alte Datei oder Verlaufseintrag) wird
  beim nächsten Strg+S beschnitten, wenn die Option `false` ist. So gewollt

## Prüfen

- `tests/test_document.py`:
  - Standard: gespeichertes Rohbild hat die Größe des Ausschnitts (300×200), kein Rahmen in
    der Datei, ein Element im Ausschnitt liegt nach dem Laden um den Versatz verschoben an
    derselben Stelle des Bildes, ein Element ganz außerhalb fehlt, Pixelvergleich: das
    gerenderte Bild nach dem Laden gleicht dem vor dem Speichern
  - `keep_full_screenshot = true`: der heutige Test (ganzes Rohbild + Rahmen) unverändert
  - Verlauf: Eintrag enthält weiter das ganze Rohbild und den Rahmen
- `regress.py`, GUI-Tests wie immer
- Handtest bei dir: Ausschnitt ziehen, Strg+S, Datei mit `griffel datei.png` öffnen (nur der
  Ausschnitt da, Markierungen an der richtigen Stelle), einmal mit HiDPI, falls du das nutzt
  (Pixel pro Szenen-Einheit ≠ 1)

## Doku

- `config.example.toml` (Option, Kommentar unter `[history]`)
- `docs/usage.md`, Abschnitt Ausschnitt X: „the editable file keeps the whole screenshot …“
  umschreiben, Strg+E als sauberes PNG zum Weitergeben
- README: kurzer Abschnitt „Privacy“ (gespeicherte Dateien, Verlauf, Strg+E). `file-format.md`
  kommt erst in Phase 3
- `CLAUDE.md`: Satz zu `save_drawing`/`build_document`
