# Plan: Fokus zurückgeben ohne herbstluftwm (Veröffentlichung 2.4)

Stand: 2026-10-17, **umgesetzt**. Gesamtplan: `plan-veroeffentlichung.md`, Phase 2.4.

## Problem

Das Overlay umgeht den WM (Bypass-Fenster) und holt sich den Fokus selbst
(`activateWindow()`). Der WM merkt davon nichts. Beim Schließen gibt `wm.restore_focus()` den
Fokus zurück, aber nur über `herbstclient attr clients.focus.winid`. Unter jedem anderen WM
passiert nichts, danach hat evtl. kein Fenster den Fokus (Tippen geht ins Leere, bis man
klickt).

## Idee

Fast alle WMs auf X11 (i3, bspwm, awesome, Openbox, Xfce, KDE, GNOME) pflegen nach EWMH die
Root-Eigenschaft `_NET_ACTIVE_WINDOW`: das Fenster, das sie für fokussiert halten. Das
Bypass-Fenster kennen sie nicht, also zeigt die Eigenschaft beim Schließen genau das Fenster,
dem der Fokus zurückgegeben werden soll. Auch wenn man währenddessen per Hotkey den
Arbeitsbereich oder das Fenster gewechselt hat, so wie heute bei herbstluftwm.

Abfrage beim Schließen: `xdotool getactivewindow`. Zurückgeben: `xdotool windowfocus <id>`
(setzt den X-Fokus direkt, wie heute). Ohne xdotool: `wmctrl -i -a <id>` (aktiviert über den
WM). Ohne beides: Hinweis auf stderr, einmal.

Rückfall: Liefert die Abfrage beim Schließen nichts (z. B. leerer Arbeitsbereich), passiert
nichts, wie heute bei herbstluftwm. Kein Merken beim Start: Das Fenster vom Start kann auf
einem anderen Arbeitsbereich liegen, und ihm den Fokus zu geben, wäre falsch.

## Config

```toml
[wm]
# Give the keyboard focus back after the screenshot overlay: "auto" = herbstluftwm if
# herbstclient answers, otherwise the window manager's active window (EWMH, needs xdotool or
# wmctrl); "herbstluftwm", "ewmh" to force one; "off" = do nothing.
focus = "auto"
```

- Ungültiger Wert: Hinweis, `auto`
- `auto`: herbstluftwm-Weg wie bisher, wenn `herbstclient` da ist und antwortet, sonst EWMH.
  Für dich ändert sich also nichts

## Code

- `wm.py`: `restore_focus(method="auto")`, intern `herbstluftwm_window()` (heutiges
  `focused_window`) und `ewmh_window()` (`xdotool getactivewindow`, sonst `xprop -root
  _NET_ACTIVE_WINDOW`), `give_focus(winid)` (xdotool, wmctrl, herbstclient jumpto). Weiterhin:
  ohne Bildschirm (`offscreen`) nie externe Programme
- `settings.py`: `FOCUS_METHODS`, `Settings.focus_method` aus `[wm] focus`
- `canvas.py`: `restore_focus(self.settings.focus_method)` in `closeEvent`, Docstrings
- `config.example.toml`: Abschnitt `[wm]`; README: xdotool ist außerhalb von herbstluftwm für
  den Fokus nötig, nicht nur optional (Requirements). Modul-Docstring `wm.py`
- `tests/test_settings.py`: `[wm] focus` gültig, ungültig, fehlend

## GUI-Test mit i3

i3 ist installiert, damit prüft der Harness den EWMH-Weg unter einem zweiten WM:
- `Session(name, wm="herbstluftwm" | "i3")`, Umgebungsvariable `GRIFFEL_TEST_WM` wählt den WM
  für ein ganzes Szenario. i3 mit minimaler Config (Temp-Ordner, keine Leiste), bereit, wenn
  `i3-msg -t get_version` antwortet. Testhotkey `super+j` unter i3 per `xdotool windowactivate`
- `run.py`: `test_overlay` und `test_board` laufen zusätzlich mit i3 (Ausgabe in
  `tests/gui/out/<name>-i3/`). Ohne i3: Hinweis, übersprungen
- Geprüft wird damit auch, dass das Bypass-Fenster unter i3 den Fokus bekommt, über allem
  liegt und Hotkeys durchlässt. Falls etwas hakt, schreibe ich es hier rein und frage dich,
  bevor ich etwas umbaue

## Gefunden beim Test mit i3 (entschieden 2026-10-17)

Nach Esc kam der Fokus unter i3 sofort richtig zurück. Aber: Holt ein Hotkey bei offenem
Overlay den Fokus weg, nahm sich das Overlay ihn nicht zurück, obwohl die Maus darüber lag,
erst nach einem Klick. Ursache: Qt setzt den Fokus eines Bypass-Fensters mit dem Zeitstempel
des letzten Ereignisses, das Qt gesehen hat. i3 vergibt den Fokus mit einem neueren, der
X-Server ignoriert dann Qts Anfrage (unter herbstluftwm zufällig nicht). Lösung:
`refocus_if_hovered` prüft nach `FOCUS_RETRY_MS` noch einmal und setzt den Fokus dann per
`wm.force_focus` (`xdotool windowfocus`, ohne Zeitstempel).

## Nicht in diesem Schritt

- Xfce, KDE, GNOME (Flackern, Panels über dem Overlay): kein Harness dafür, das kommt in die
  Generalprobe (Phase 6, VM). `[ui] overlay = "fullscreen"` nur, wenn es dort hakt
- Lauf ganz ohne WM: kein `_NET_ACTIVE_WINDOW`, es passiert nichts (wie heute)

## Handtest bei dir

- Overlay öffnen (Alt+Escape), Esc: Fokus wieder im vorherigen Fenster (wie bisher)
- Mit `[wm] focus = "ewmh"` dasselbe, auch nach Tag-Wechsel per Hotkey währenddessen.
  Danach den Eintrag wieder entfernen
