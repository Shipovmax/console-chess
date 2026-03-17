"""
Main module for the chess emulator.

Implements additional tasks 1, 5, 6, 7, and 8 (total complexity: 5).
Provides the chess game logic, including the standard mode and "fairy"
chess with new piece types, along with a console user interface.
"""

import copy
import os
import sys
from typing import List, Tuple, Optional, Dict, Any, Set

# Color constants for text output
GREEN_COLOR: str = "\033[92m"
BLUE_COLOR: str = "\033[94m"
YELLOW_COLOR: str = "\033[93m"
RED_COLOR: str = "\033[91m"
CYAN_COLOR: str = "\033[96m"
MAGENTA_COLOR: str = "\033[95m"
RESET_COLOR: str = "\033[0m"

# Background colors for the chessboard and move highlighting
BG_LIGHT: str = "\033[47m"
BG_DARK: str = "\033[100m"
BG_GREEN: str = "\033[42m"
BG_RED: str = "\033[41m"
BG_MAGENTA: str = "\033[45m"


class Piece:
    """
    Represents a chess piece.

    Supports both classic pieces and the custom Task 1 pieces
    (champion, wizard, jumper).
    """

    def __init__(self, color: str, type_: str) -> None:
        """
        Initialize a chess piece.

        :param color: Piece color ('white' or 'black').
        :param type_: Piece type (for example, 'king', 'champion', 'pawn').
        """
        self.color = color
        self.type = type_

    def __repr__(self) -> str:
        """Return the technical string representation of the piece."""
        return f"{self.color}_{self.type}"

    def symbol(self) -> str:
        """
        Return the colored Unicode symbol for the piece.

        :return: A string with ANSI color codes and a Unicode symbol.
        """
        symbols: Dict[str, Dict[str, str]] = {
            "white": {
                "king": "♔", "queen": "♕", "rook": "♖", "bishop": "♗",
                "knight": "♘", "pawn": "♙", "champion": "★", "wizard": "✧",
                "jumper": "⚶",
            },
            "black": {
                "king": "♚", "queen": "♛", "rook": "♜", "bishop": "♝",
                "knight": "♞", "pawn": "♟", "champion": "★", "wizard": "✧",
                "jumper": "⚶",
            },
        }

        sym = symbols[self.color].get(self.type, "?")
        if self.color == "white":
            return f"{YELLOW_COLOR}{sym}{RESET_COLOR}"
        return f"{BLUE_COLOR}{sym}{RESET_COLOR}"


class ChessEngine:
    """
    Chess game engine.

    Handles movement rules, en passant, pawn promotion,
    check/checkmate validation, and move history.
    """

    def __init__(self, mode: str = "standard") -> None:
        """
        Initialize the game state and chessboard.

        :param mode: Game mode ('standard' or 'fairy').
        """
        self.mode = mode
        self.board: List[List[Optional[Piece]]] = self.create_board(mode)
        self.turn: str = "white"
        self.move_log: List[Dict[str, Any]] = []
        self.game_over: bool = False
        self.winner: Optional[str] = None
        self.move_count: int = 0
        self.en_passant_target: Optional[Tuple[int, int]] = None

    def create_board(self, mode: str) -> List[List[Optional[Piece]]]:
        """
        Create the initial board setup.

        :param mode: Game mode (standard or fairy pieces).
        :return: An 8x8 matrix containing Piece objects and empty squares (None).
        """
        board: List[List[Optional[Piece]]] = [
            [None for _ in range(8)] for _ in range(8)
        ]

        # Place pawns
        for c in range(8):
            board[1][c] = Piece("black", "pawn")
            board[6][c] = Piece("white", "pawn")

        # Define the back-rank setup
        if mode == "fairy":
            placement = [
                "rook", "jumper", "wizard", "champion",
                "king", "wizard", "jumper", "rook"
            ]
        else:
            placement = [
                "rook", "knight", "bishop", "queen",
                "king", "bishop", "knight", "rook"
            ]

        # Place major pieces
        for c, type_ in enumerate(placement):
            board[0][c] = Piece("black", type_)
            board[7][c] = Piece("white", type_)

        return board

    def switch_turn(self) -> None:
        """Pass the turn to the other player."""
        self.turn = "black" if self.turn == "white" else "white"

    def get_valid_moves_for_piece(
        self, r: int, c: int, board: List[List[Optional[Piece]]]
    ) -> List[Tuple[int, int]]:
        """
        Generate all pseudo-legal moves for a piece.

        Ignores self-check validation. Supports advanced pawn rules
        and custom fairy pieces.

        :param r: Piece row.
        :param c: Piece column.
        :param board: Current board state to analyze.
        :return: A list of available destination coordinates.
        """
        piece = board[r][c]
        if not piece:
            return []

        moves: List[Tuple[int, int]] = []
        directions: Dict[str, List[Tuple[int, int]]] = {
            "rook": [(-1, 0), (1, 0), (0, -1), (0, 1)],
            "bishop": [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            "knight": [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1),
            ],
            "king": [
                (-1, -1), (-1, 0), (-1, 1), (0, -1),
                (0, 1), (1, -1), (1, 0), (1, 1),
            ],
            "champion": [
                (-2, 0), (2, 0), (0, -2), (0, 2),
                (-1, 0), (1, 0), (0, -1), (0, 1),
            ],
            "wizard": [
                (-3, -3), (-3, 3), (3, -3), (3, 3),
                (-1, -1), (-1, 1), (1, -1), (1, 1),
            ],
            "jumper": [
                (-2, -2), (-2, 2), (2, -2), (2, 2),
                (-2, 0), (2, 0), (0, -2), (0, 2),
            ],
        }
        directions["queen"] = directions["rook"] + directions["bishop"]

        # Pawn movement rules
        if piece.type == "pawn":
            direction = -1 if piece.color == "white" else 1
            next_row = r + direction

            # Single forward move
            if 0 <= next_row < 8 and board[next_row][c] is None:
                moves.append((next_row, c))
                start_row = 6 if piece.color == "white" else 1

                # Double-step move from the starting rank
                if r == start_row and board[next_row + direction][c] is None:
                    moves.append((next_row + direction, c))

            # Diagonal captures
            for dc in [-1, 1]:
                if 0 <= next_row < 8 and 0 <= c + dc < 8:
                    target = board[next_row][c + dc]
                    # Standard capture
                    if target and target.color != piece.color:
                        moves.append((next_row, c + dc))
                    # En passant capture
                    elif self.en_passant_target == (next_row, c + dc):
                        moves.append((next_row, c + dc))

        # Jumping pieces (knight, king, and new fairy pieces)
        elif piece.type in ["knight", "king", "champion", "wizard", "jumper"]:
            for dr, dc in directions[piece.type]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board[nr][nc]
                    if target is None or target.color != piece.color:
                        moves.append((nr, nc))

        # Sliding pieces (rook, bishop, queen)
        elif piece.type in ["rook", "bishop", "queen"]:
            for dr, dc in directions[piece.type]:
                for i in range(1, 8):
                    nr, nc = r + dr * i, c + dc * i
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        target = board[nr][nc]
                        if target is None:
                            moves.append((nr, nc))
                        elif target.color != piece.color:
                            moves.append((nr, nc))
                            break
                        else:
                            break
                    else:
                        break
        return moves

    def is_check(self, color: str, board: List[List[Optional[Piece]]]) -> bool:
        """
        Check whether the specified king is in check.

        :param color: King color to validate ('white' or 'black').
        :param board: Board state.
        :return: True if the king is in check, otherwise False.
        """
        king_pos: Optional[Tuple[int, int]] = None

        # Locate the king
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and p.type == "king" and p.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        opponent = "black" if color == "white" else "white"

        # Check all opponent moves
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and p.color == opponent:
                    moves = self.get_valid_moves_for_piece(r, c, board)
                    if king_pos in moves:
                        return True
        return False

    def get_legal_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """
        Return the list of fully legal moves for a piece.

        Filters out moves that would leave the player's own king in check.

        :param r: Piece row.
        :param c: Piece column.
        :return: A list of legal destination coordinates.
        """
        piece = self.board[r][c]
        if not piece or piece.color != self.turn:
            return []

        pseudo_moves = self.get_valid_moves_for_piece(r, c, self.board)
        legal_moves: List[Tuple[int, int]] = []

        for move in pseudo_moves:
            # Create a temporary board copy to simulate the move
            temp_board = [row[:] for row in self.board]
            temp_board[move[0]][move[1]] = temp_board[r][c]
            temp_board[r][c] = None

            # Simulate en passant capture for proper self-check validation
            if piece.type == "pawn" and move == self.en_passant_target:
                temp_board[r][move[1]] = None

            # If the king is safe after the move, the move is legal
            if not self.is_check(self.turn, temp_board):
                legal_moves.append(move)

        return legal_moves

    def get_all_possible_moves(
        self, color: str, board_state: Optional[List[List[Optional[Piece]]]] = None
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Collect all pseudo-legal moves for the specified color.

        :param color: Piece color ('white' or 'black').
        :param board_state: Optional board state override.
        :return: A list of coordinate pairs ((from), (to)).
        """
        board = board_state if board_state else self.board
        moves: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []

        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.color == color:
                    valid_moves = self.get_valid_moves_for_piece(r, c, board)
                    for move in valid_moves:
                        moves.append(((r, c), move))
        return moves

    def is_checkmate(self) -> bool:
        """
        Check whether the current player is in checkmate.

        :return: True if checkmate is present, otherwise False.
        """
        if not self.is_check(self.turn, self.board):
            return False

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == self.turn:
                    if len(self.get_legal_moves(r, c)) > 0:
                        return False
        return True

    def make_move(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        promote_to: str = "queen",
    ) -> bool:
        """
        Execute a move and update the game state.

        Saves move history and handles en passant and pawn promotion.

        :param start: Starting coordinates (row, column).
        :param end: Destination coordinates (row, column).
        :param promote_to: Piece type used for pawn promotion.
        :return: True if the move succeeds, otherwise False.
        """
        r1, c1 = start
        r2, c2 = end
        piece = self.board[r1][c1]

        if not piece or piece.color != self.turn:
            return False

        legal_moves = self.get_legal_moves(r1, c1)
        if (r2, c2) not in legal_moves:
            return False

        # Save the current state so undo remains available
        state_snapshot = {
            "board": copy.deepcopy(self.board),
            "turn": self.turn,
            "move_count": self.move_count,
            "game_over": self.game_over,
            "en_passant_target": self.en_passant_target,
        }
        self.move_log.append(state_snapshot)

        # Execute en passant capture
        if piece.type == "pawn" and (r2, c2) == self.en_passant_target:
            self.board[r1][c2] = None

        # Set the target square for a possible en passant capture next turn
        if piece.type == "pawn" and abs(r1 - r2) == 2:
            self.en_passant_target = ((r1 + r2) // 2, c1)
        else:
            self.en_passant_target = None

        # Move the piece
        self.board[r2][c2] = self.board[r1][c1]
        self.board[r1][c1] = None

        # Promote a pawn that reaches the last rank
        if piece.type == "pawn" and (r2 == 0 or r2 == 7):
            promoted_piece = self.board[r2][c2]
            if promoted_piece:  # Type-safety guard
                promoted_piece.type = promote_to

        self.switch_turn()
        self.move_count += 1

        if self.is_checkmate():
            self.game_over = True
            self.winner = "black" if self.turn == "white" else "white"

        return True

    def undo_move(self) -> bool:
        """
        Revert the last move and restore the previous game state.

        :return: True if undo succeeds, otherwise False.
        """
        if not self.move_log:
            return False

        state = self.move_log.pop()
        self.board = state["board"]
        self.turn = state["turn"]
        self.move_count = state["move_count"]
        self.game_over = state["game_over"]
        self.en_passant_target = state["en_passant_target"]
        self.winner = None

        return True


def parse_square(sq_str: str) -> Optional[Tuple[int, int]]:
    """
    Convert chessboard coordinates to matrix indices.

    :param sq_str: Coordinate string (for example, 'e2').
    :return: A tuple (row, column) or None for invalid input.
    """
    try:
        c = ord(sq_str[0].lower()) - ord("a")
        r = 8 - int(sq_str[1])
        if 0 <= r < 8 and 0 <= c < 8:
            return (r, c)
    except (IndexError, ValueError):
        pass
    return None


class AdvancedChessEmulator:
    """
    Console UI and game state machine.

    Handles user interaction, move highlighting,
    threat highlighting, and menu navigation.
    """

    def __init__(self) -> None:
        """Initialize the emulator and its initial UI state."""
        self.engine = ChessEngine()
        self.current_state: str = "main_menu"
        self.selected_square: Optional[Tuple[int, int]] = None
        self.show_threats: bool = False

    def run(self) -> None:
        """Run the main application loop."""
        self.print_header()
        while True:
            try:
                if self.current_state == "main_menu":
                    self.show_main_menu()
                elif self.current_state == "play_match":
                    self.play_match()
                else:
                    self.current_state = "main_menu"
            except KeyboardInterrupt:
                print(f"\n\n{RED_COLOR}🔚 Exiting the program...{RESET_COLOR}")
                break
            except Exception as e:
                print(f"\n{RED_COLOR}❌ Error: {e}{RESET_COLOR}")
                self.current_state = "main_menu"

    def print_header(self) -> None:
        """Print the program header to the console."""
        separator = f"{CYAN_COLOR}{'=' * 50}{RESET_COLOR}"
        print(separator)
        print(f"{YELLOW_COLOR}♟️   ADVANCED CHESS EMULATOR (MAX COMPLEXITY)  ♙{RESET_COLOR}")
        print(separator)

    def show_main_menu(self) -> None:
        """Render the main menu and process the user choice."""
        print(f"\n{CYAN_COLOR}=== MAIN MENU ==={RESET_COLOR}")
        status = (
            "Resume"
            if self.engine.move_count > 0 and not self.engine.game_over
            else "Start"
        )

        print(f"1 - 🎮 {status} a standard game")
        print("2 - 🌟 Start FAIRY CHESS (3 new pieces)")
        print("0 - 👋 Exit")

        choice = input(f"\n{YELLOW_COLOR}Select an option: {RESET_COLOR}").strip()

        if choice == "1":
            if self.engine.game_over or self.engine.mode != "standard":
                self.engine = ChessEngine("standard")
            self.current_state = "play_match"
        elif choice == "2":
            self.engine = ChessEngine("fairy")
            self.current_state = "play_match"
        elif choice == "0":
            sys.exit()

    def print_board_styled(self) -> None:
        """Print the board with legal-move and threat highlights."""
        legal_destinations: Set[Tuple[int, int]] = set()
        if self.selected_square:
            moves = self.engine.get_legal_moves(*self.selected_square)
            legal_destinations = set(moves)

        threatened_squares: Set[Tuple[int, int]] = set()
        if self.show_threats:
            opponent = "black" if self.engine.turn == "white" else "white"
            moves_with_sources = self.engine.get_all_possible_moves(opponent)
            threatened_squares = {end for _, end in moves_with_sources}

        print(f"\n{CYAN_COLOR}    a  b  c  d  e  f  g  h{RESET_COLOR}")

        for r in range(8):
            row_s = f"{CYAN_COLOR}{8 - r} {RESET_COLOR}"
            for c in range(8):
                piece = self.engine.board[r][c]

                is_selected = self.selected_square == (r, c)
                is_legal_dest = (r, c) in legal_destinations
                is_threatened = (
                    (r, c) in threatened_squares
                    and piece is not None
                    and piece.color == self.engine.turn
                )

                # Determine the square background color
                if is_selected:
                    bg = BG_MAGENTA
                elif is_legal_dest:
                    bg = BG_GREEN
                elif is_threatened:
                    bg = BG_RED
                else:
                    bg = BG_LIGHT if (r + c) % 2 == 0 else BG_DARK

                sym = piece.symbol() if piece else " "
                row_s += f"{bg} {sym} {RESET_COLOR}"

            row_s += f"{CYAN_COLOR} {8 - r}{RESET_COLOR}"
            print(row_s)

        print(f"{CYAN_COLOR}    a  b  c  d  e  f  g  h{RESET_COLOR}\n")

    def play_match(self) -> None:
        """Run the match loop and process moves and commands."""
        if self.engine.game_over:
            winner_str = str(self.engine.winner).upper()
            print(f"\n{YELLOW_COLOR}🏆 CHECKMATE! {winner_str} wins!{RESET_COLOR}")
            input(f"{CYAN_COLOR}Press Enter to return to the menu...{RESET_COLOR}")
            self.current_state = "main_menu"
            return

        self.print_board_styled()

        turn_str = (
            f"{YELLOW_COLOR}WHITE{RESET_COLOR}"
            if self.engine.turn == "white"
            else f"{BLUE_COLOR}BLACK{RESET_COLOR}"
        )
        print(f"Turn: {turn_str} | Total moves: {self.engine.move_count}")
        print(
            f"{CYAN_COLOR}Commands: {RESET_COLOR}'e2' (select), "
            f"'e2e4' (move), 'undo', 'threats', '0' (menu)"
        )

        cmd = input(f"{YELLOW_COLOR}Your choice: {RESET_COLOR}").strip().lower()

        if cmd == "0":
            self.current_state = "main_menu"
            self.selected_square = None
            return

        if cmd == "undo":
            if self.engine.undo_move():
                self.selected_square = None
            return

        if cmd == "threats":
            self.show_threats = not self.show_threats
            return

        # Interactive piece selection
        if len(cmd) == 2:
            square = parse_square(cmd)
            if square:
                piece = self.engine.board[square[0]][square[1]]
                if piece and piece.color == self.engine.turn:
                    self.selected_square = square
                else:
                    print(f"{RED_COLOR}❌ That is not your piece, or the square is empty!{RESET_COLOR}")
            return

        # Execute a move
        if len(cmd) == 4:
            start = parse_square(cmd[:2])
            end = parse_square(cmd[2:])
            if start and end:
                promote_to = "queen"

                # Check for pawn promotion
                piece = self.engine.board[start[0]][start[1]]
                if piece and piece.type == "pawn" and end[0] in [0, 7]:
                    print(
                        f"{MAGENTA_COLOR}🌟 Pawn reached the final rank! "
                        f"Promote to? (queen, rook, bishop, knight){RESET_COLOR}"
                    )
                    choice = input("Choice: ").strip().lower()
                    if choice in ["queen", "rook", "bishop", "knight"]:
                        promote_to = choice

                if self.engine.make_move(start, end, promote_to):
                    self.selected_square = None
                    return
                print(f"\n{RED_COLOR}❌ Illegal move!{RESET_COLOR}")
                return

        print(
            f"\n{RED_COLOR}❌ Invalid format! Enter a source and destination "
            f"(for example: e2e4) or select a square like e2.{RESET_COLOR}"
        )


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    AdvancedChessEmulator().run()
