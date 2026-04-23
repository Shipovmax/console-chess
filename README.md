# Console Chess

A fully playable console chess implementation in Python — two versions in one repo: a minimal baseline and a feature-rich advanced emulator.

---

## Two Versions

### `main.py` — Baseline engine
Standard chess with full legal move validation, checkmate detection, and undo. Plain console output with Unicode pieces.

### `chess_app.py` — Advanced emulator
Everything in `main.py` plus five extended features, ANSI colour output, and an interactive menu.

---

## Features (`chess_app.py`)

**Standard gameplay**
- Full move legality with check/checkmate validation
- Pseudo-legal + self-check filtering pipeline
- Undo to the beginning of the game (full state snapshots with `copy.deepcopy`)

**Extended features**
- **Fairy Chess mode** — three new piece types with original movement rules:
  - **Champion (★)** — moves 1 or 2 squares orthogonally, can jump
  - **Wizard (✧)** — moves 1 or 3 squares diagonally, can jump
  - **Jumper (⚶)** — moves exactly 2 squares in any direction
- **Legal move highlighting** — select a piece (e.g. `e2`) to highlight its legal destinations in green; selected square in magenta
- **Threat highlighting** — toggle `threats` to highlight the active player's pieces currently under attack in red
- **En passant** — two-square pawn advances tracked via `en_passant_target`; captured pawn correctly removed in legal-move simulation
- **Pawn promotion** — interactive piece selection when a pawn reaches the last rank

---

## Requirements

Python 3.7+, no external dependencies.

---

## Usage

```bash
git clone https://github.com/Shipovmax/chess
cd chess

# Full-featured version
python chess_app.py

# Minimal baseline version
python main.py
```

### Controls (`chess_app.py`)

| Input | Action |
|-------|--------|
| `e2` | Select a piece, show legal moves |
| `e2e4` | Move piece from e2 to e4 |
| `undo` | Revert the last move |
| `threats` | Toggle threat highlighting |
| `0` | Return to main menu |

---

## Tests

```bash
python -m pytest tests/
```

| Test file | Coverage |
|-----------|---------|
| `test_task1_fairy.py` | Fairy piece movement |
| `test_task5_undo.py` | Undo logic and state restoration |
| `test_task8_pawn.py` | En passant and promotion |
| `test_tasks6_7_hints.py` | Legal move and threat highlighting |

---

## Author

- GitHub: [Shipovmax](https://github.com/Shipovmax)
- Email: shipov.max@icloud.com
