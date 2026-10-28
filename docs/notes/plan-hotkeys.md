# Plan: Tastenkürzel und globale Hotkeys dokumentieren (Veröffentlichung 2.7)

Stand: 2026-10-28, **umgesetzt**. Gesamtplan: `plan-veroeffentlichung.md`, Phase 2.7.

Reine Doku, kein Code. Zwei Teile: (1) wo griffels eigene Kürzel mit dem Fenstermanager
kollidieren, (2) wie man griffel auf einen globalen Hotkey legt.

## 1. Kollisionen mit dem Fenstermanager

### Warum es kollidiert
Das Overlay greift die Tastatur bewusst nicht (kein `grabKeyboard`), damit globale Hotkeys
weiter gehen. Die Kehrseite: Was der WM global bindet, kommt nie bei griffel an. Das betrifft
alle Kürzel mit Alt, wenn Alt die Mod-Taste des WM ist.

### griffels Alt-Kürzel
- Alt+A S D F: Größenstufe 1–4 (`size_1` … `size_4`)
- Alt+V: Monospace an/aus (`text_font`)
- Alt+Rad: Feineinstellung der Größe (fest im Code, nicht über `[keys]` änderbar)

### Konkreter Fall i3 (Mod1 = Alt, häufige Wahl)
Die i3-Standardconfig bindet genau diese: `$mod+a` focus parent, `$mod+s` layout stacking,
`$mod+d` dmenu, `$mod+f` fullscreen, `$mod+v` split vertical. Mit Alt als Mod gehen alle
fünf griffel-Kürzel verloren. Ähnlich bei Openbox/awesome/dwm-Setups mit Alt als Mod.
Das Whiteboard ist ein normales Fenster: dort verschiebt Alt+Ziehen bei i3 das Fenster
(`floating_modifier`), griffel nutzt Alt+Ziehen aber nicht, also kein Problem.

### Abhilfe (für README)
```toml
[keys]
size_1 = "ctrl+1"
size_2 = "ctrl+2"
size_3 = "ctrl+3"
size_4 = "ctrl+4"
text_font = "ctrl+m"
```
Alle fünf sind in griffel frei (geprüft gegen `DEFAULT_KEYS`). Die Tastenübersicht (?) zeigt
danach die neuen Tasten.

Alt+Rad bleibt; die meisten WMs binden Alt+Rad nicht. Falls doch: offene Frage unten.

## 2. Globale Hotkeys

Drei Befehle lohnen einen Hotkey: `griffel` (Screenshot), `griffel --board`, `griffel --last`.
Als Beispieltasten nicht deine Alt+Escape / Alt+Delete (Alt ist bei vielen die Mod-Taste),
sondern **Super+Shift+S** (Screenshot) und **Super+Shift+W** (Whiteboard), weil Super selten
mit Programmen kollidiert. Jeweils als aufklappbares `<details>` im README:

- **sxhkd** (auch bspwm): `super + shift + s` / `griffel`; danach `pkill -USR1 sxhkd`
- **i3**: `bindsym $mod+Shift+s exec --no-startup-id griffel` (`--no-startup-id`, sonst zeigt
  i3 bis zum Timeout den Warte-Cursor, weil griffel keine Startup-Notification schickt).
  Achtung: `$mod+Shift+s` ist in i3 nicht belegt, aber in manchen Configs schon – prüfen
- **herbstluftwm**: `hc keybind Mod4-Shift-s spawn griffel`
- **awesome**: `awful.key({ modkey, "Shift" }, "s", function () awful.spawn("griffel") end)`
- **Openbox**: `<keybind key="W-S-s"><action name="Execute"><command>griffel</command></action></keybind>`
- **xbindkeys**: `"griffel"` + `Mod4+Shift + s`
- **KDE Plasma (X11-Sitzung)**: Systemeinstellungen → Tastatur → Kurzbefehle → Neu → Befehl
- **GNOME/Xfce/Cinnamon (X11-Sitzung)**: Einstellungen → Tastatur → Eigene Tastenkürzel.
  Hinweis: GNOME und KDE starten heute standardmäßig Wayland, dort verweigert griffel den
  Screenshot (2.6); beim Anmelden „Xorg“-Sitzung wählen

Wichtig für alle: `griffel` muss im `PATH` des WM liegen. `~/.local/bin` ist das bei vielen
WMs nicht, wenn sie nicht aus einer Login-Shell starten → im Zweifel absoluter Pfad.

Die Beispiele schreibe ich aus der jeweiligen Doku, getestet habe ich nur sxhkd/herbstluftwm
(im Harness) und i3 (Harness startet mit i3, nutzt aber sxhkd für den Hotkey). Ich prüfe
die Syntax der anderen gegen deren Doku, ausprobieren kann ich sie nicht.

## Wo es hinkommt

- README, Abschnitt „Getting started“: nach dem Codeblock ein Unterabschnitt
  **„Global hotkey“** mit den `<details>`-Blöcken
- README, Abschnitt „Configuration“: Absatz **„Clashes with your window manager“** mit Erklärung
  und dem `[keys]`-Beispiel (neben dem schon vorhandenen QWERTZ-Hinweis)
- `config.example.toml`, `[keys]`: ein Kommentar „Alt as the modifier of your window manager
  (e.g. i3): see README, e.g. size_1 = "ctrl+1"“
- `docs/usage.md`: bei Alt+A S D F / Alt+V ein Halbsatz mit Verweis

Phase 3 (README-Umbau) übernimmt das später in den Quick Start; deshalb jetzt schon im
README und nicht in einer eigenen Datei.

## Tests

Kein Code. Nur prüfen, dass das `[keys]`-Beispiel gültig ist und nichts doppelt belegt:
ein Fall in `test_settings.py` (KeyMap mit diesen fünf Werten → keine Warnung, `size_1` auf
Ctrl+1). Und `sync_config` vertragen die neuen Kommentare in `config.example.toml`.

## Handtest bei dir

Nichts zu bedienen. README auf GitHub-Vorschau lesen geht erst nach dem Push; lokal reicht
ein Blick in die Markdown-Vorschau deines Editors, ob die `<details>` aufklappen.

## Offene Frage

- Alt+Rad über `[keys]` änderbar machen? Wäre Code (das Rad läuft nicht über die KeyMap).
  Vorschlag: nein, erst wenn sich jemand meldet
