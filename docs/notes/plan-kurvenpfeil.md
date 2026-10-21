# Plan: Geschwungener Pfeil (Roadmap 21)

Entschieden im Interview am 2026-10-21.

## Bedienung
- Die Pfeil-Taste (Standard `d`, Slot aus `[tools] order`) bei schon aktivem Pfeil-Werkzeug schaltet gerade ↔ geschwungen um (wie `c` beim Marker). Klick auf das Pfeil-Feld in der Leiste nur auswählen, wie beim Marker
- Icon in der Leiste, Mauszeiger und Übersicht (?) zeigen die aktive Variante
- Die Sitzung merkt sich die Variante, Startwert aus `[arrow] default = "straight" | "curve"`
- Ein ausgewählter Pfeil wird durch die Taste nicht umgewandelt
- Screenshot und Whiteboard

## Form
- Aus dem Freihandstrich wird eine kubische Bézierkurve eingepasst: Start und Ende fest (erster/letzter Mauspunkt), die zwei Kontrollpunkte per kleinster Quadrate bei Sehnenlängen-Parametrisierung (`tools.fit_cubic`, Qt-frei)
- Live: bei jeder Mausbewegung neu eingepasst (die Rohpunkte merkt sich das Element nur während des Zeichnens)
- Fast gerade (größte Abweichung der Rohpunkte von der Sehne unter `CURVE_STRAIGHT_PX` Bildschirm-Pixeln, über `screen_px`): Kontrollpunkte auf die Drittelpunkte der Sehne, also exakt gerade
- Zu kurz (wie beim geraden Pfeil): verworfen
- Spitze nur am Ende, Richtung = Tangente am Ende (c2 → Ende, fällt c2 auf das Ende: c1, dann Start), Größe wie beim geraden Pfeil

## Bearbeiten
- 4 Griffe: Start, c1, c2, Ende; Hilfslinien Start–c1 und c2–Ende, kein Rahmen
- Drehbar mit Q / Shift+Q und mit dem Dreh-Griff (über dem Begrenzungsrahmen)
- Farbe, Stärke, Kopieren, Undo, Speichern, Verlauf wie sonst

## Datenmodell
- `Tool.ARROW` mit `arrow_kind = "straight" | "curve"`, Kurve: `points = [start, c1, c2, end]`
- Gespeichert als `"kind": "curve"` (nur bei Kurven), fehlt es: gerade
- Nicht andockbar (`connectors.is_connector` schließt Kurven aus), keine Beschriftung

## Nicht enthalten
- Andocken samt Mitverformen, Beschriftung auf der Kurve: später denkbar
- Freihand glätten: eigener Roadmap-Punkt 22

## Schritte
1. `fit_cubic` + Pfad in `tools.py`, `arrow_kind` in `ShapeElement` (Zeichnen, Speichern, Laden, Griffe), Test in `test_document.py`
2. Canvas: Umschalten per Taste, Icon, Mauszeiger, Config `[arrow] default`, Übersicht
3. Auswahl: Hilfslinien, Dreh-Griff
4. GUI-Szenario `test_curve.py`, Regressionsszene, `docs/usage.md`, Roadmap abhaken
