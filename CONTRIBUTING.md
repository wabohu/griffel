# Contributing

griffel is a personal project, built for my own desktop. Bug reports, ideas and
pull requests are welcome all the same; I may be slow to answer.

## Reporting a bug

Please include:

- `griffel --version`, your distribution, window manager or desktop
- X11 or Wayland (`echo $XDG_SESSION_TYPE`)
- what you did, what you expected, what happened
- the terminal output: start griffel from a terminal to see its messages

## Working on the code

```sh
git clone https://github.com/wabohu/griffel.git
cd griffel
./run.py                                   # runs straight from src/
git config core.hooksPath scripts/git-hooks
```

The git hook updates your own `~/.config/griffel/config.toml` from
`config.example.toml` before each commit (new options added, your values kept,
a backup in `config.toml.bak`). Preview it with
`python scripts/sync_config.py --dry-run`.

How the code is organized, and the rules it follows, are described in
[CLAUDE.md](CLAUDE.md). It is written for an AI coding assistant, but it is the
architecture documentation for people too.

## Tests

Run all of them before a pull request:

```sh
python tests/test_settings.py    # config values and fallbacks, Qt-free parts
python tests/test_document.py    # saving, loading, editing without a screen
python tests/regress.py          # draws a fixed scene and compares pixels
python tests/gui/run.py          # GUI scenarios in an invisible X server
```

The GUI tests need Xvfb, herbstluftwm, sxhkd and xdotool (optionally i3); they
never touch your real desktop and leave screenshots in `tests/gui/out/`. If the
look changes on purpose, `python tests/regress.py --update` rewrites the
reference image. `python tests/gui/demo.py` makes the pictures in the README
(also needs alacritty and bat).

## Releasing

1. Set `__version__` in `src/griffel/__init__.py` to the new version (e.g. `0.1.0`,
   during development it is `0.1.0.dev0`)
2. In `CHANGELOG.md`, replace "unreleased" in its heading with the date
3. Run all tests, commit, then tag and push:
   ```sh
   git tag -a v0.1.0 -m "griffel 0.1.0"
   git push origin main v0.1.0
   ```
4. The `release` workflow runs the tests, checks that tag and `__version__` match, and
   creates the GitHub release with that CHANGELOG section as its notes. The source
   tarball of the release is what the AUR package builds from
5. Afterwards set `__version__` to the next `.dev0` version and start a new
   "unreleased" section in `CHANGELOG.md`

## Conventions

- Small steps; the program must start after each one
- Everything in the repository is English, except the German working notes in
  `docs/notes/`
- No new dependencies without asking first
- New keys: `keymap.py`, the handler in the canvas, a description in
  `shortcuts.py`, and [docs/usage.md](docs/usage.md) (a test checks the key
  reference)
- Every change to the drawing goes through the undo stack
