# Report on the Additional Tasks Implementation

**Total earned complexity:** 5 points.

---

### Task 1: New Piece Types (Complexity: 1)
**Description:** Design 3 new piece types with original movement rules, implement their classes, and create a modified chess mode with minimal disruption to the existing codebase.

**Implementation:**
The game now includes a `"fairy"` mode that replaces standard pieces with new ones:
- **Champion (★):** moves 1 or 2 squares orthogonally and can jump.
- **Wizard (✧):** moves 1 or 3 squares diagonally and can jump.
- **Jumper (⚶):** moves exactly 2 squares in any direction.

**Where to look in the code:**
- In `Piece.symbol`, Unicode symbols were added for `champion`, `wizard`, and `jumper`.
- In `ChessEngine.create_board`, the fairy-mode piece placement logic replaces the queen, bishops, and knights.
- In `ChessEngine.get_valid_moves_for_piece`, movement vectors were added for the new piece types.

---

### Task 5: Move Undo (Complexity: 1)
**Description:** Add the ability to roll back moves all the way to the beginning of the game.

**Implementation:**
The engine uses a `move_log` history stack. Before each move, it stores a snapshot of the current game state, including the board, active player, move counter, game-over flag, and en passant target square. The `undo` command restores the most recent snapshot.

**Where to look in the code:**
- In `ChessEngine.make_move`, `state_snapshot` stores a deep copy of the board (`copy.deepcopy(self.board)`) and the related state fields before the move.
- In `ChessEngine.undo_move`, the last saved state is restored back into the `ChessEngine` instance.
- In `AdvancedChessEmulator.play_match`, the `undo` command is handled and clears the currently selected square.

---

### Task 6: Legal Move Hinting (Complexity: 1)
**Description:** Add a visual hinting feature that shows legal destination squares after selecting a piece.

**Implementation:**
The UI supports interactive piece selection, for example by entering `e2`. The selected square is highlighted in magenta, and all legal moves for that piece are computed by the engine and highlighted in green on the console-rendered board.

**Where to look in the code:**
- In `AdvancedChessEmulator.print_board_styled`, the `legal_destinations` set is built from the legal moves of `self.selected_square`.
- In the same method, the background-color logic uses `BG_MAGENTA` for the selected square and `BG_GREEN` for legal destination squares.
- In `AdvancedChessEmulator.play_match`, two-character input is interpreted as piece selection and stored in `self.selected_square`.

---

### Task 7: Threatened Piece Hinting (Complexity: 1)
**Description:** Show which pieces belonging to the active player are currently under attack and highlight them on the board.

**Implementation:**
The `threats` toggle command was added. When enabled, the engine gathers all possible moves for the opposing side on the current board. If an opponent destination square matches one of the current player's occupied squares, including the king, that square is highlighted in red.

**Where to look in the code:**
- In `AdvancedChessEmulator.print_board_styled`, the `threatened_squares` set is built from `get_all_possible_moves` for the opponent color.
- In the same method, the `is_threatened` check turns on `BG_RED` for threatened friendly pieces.
- In `AdvancedChessEmulator.play_match`, the `threats` command toggles the `self.show_threats` boolean flag.

---

### Task 8: Advanced Pawn Rules (Complexity: 1)
**Description:** Support advanced pawn rules: en passant and promotion to another piece upon reaching the last rank.

**Implementation:**
The engine tracks two-square pawn advances and stores the intermediate capture square in `en_passant_target`. If an opposing pawn attacks that square, en passant capture is performed and the skipped pawn is removed. When a pawn reaches rank 1 or rank 8, the console prompts the user to choose the promotion piece.

**Where to look in the code:**
- In `ChessEngine.get_valid_moves_for_piece`, a move is allowed when its target square matches `self.en_passant_target`.
- In `ChessEngine.get_legal_moves`, the captured pawn is correctly removed from `temp_board` during en passant simulation so self-check detection remains accurate.
- In `ChessEngine.make_move`, en passant execution removes the captured pawn and updates `en_passant_target` after a two-square pawn move.
- In the same method, promotion changes `self.board[r2][c2].type = promote_to`.
- In `AdvancedChessEmulator.play_match`, pawn moves to the last rank trigger a promotion prompt through `input`.
