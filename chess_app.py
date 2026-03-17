import copy


class Piece:
    """Represents a single chess piece."""

    def __init__(self, color, type_):
        self.color = color  # 'white' or 'black'
        self.type = type_  # 'pawn', 'rook', 'knight', 'bishop', 'queen', or 'king'

    def __repr__(self):
        return f"{self.color}_{self.type}"

    def symbol(self):
        """Return the Unicode symbol used to render the piece in the console."""
        symbols = {
            "white": {
                "king": "♔",   # White king
                "queen": "♕",  # White queen
                "rook": "♖",   # White rook
                "bishop": "♗",  # White bishop
                "knight": "♘",  # White knight
                "pawn": "♙",   # White pawn
            },
            "black": {
                "king": "♚",   # Black king
                "queen": "♛",  # Black queen
                "rook": "♜",   # Black rook
                "bishop": "♝",  # Black bishop
                "knight": "♞",  # Black knight
                "pawn": "♟",   # Black pawn
            },
        }
        return symbols[self.color][self.type]


class ChessEngine:
    """Main chess game engine class."""

    def __init__(self):
        self.board = self.create_board()  # Create an 8x8 board
        self.turn = "white"  # White moves first
        self.move_log = []  # Move history for undo support
        self.game_over = False  # Indicates whether the game has ended
        self.winner = None  # Winner color, if any
        self.move_count = 0  # Number of completed moves

    def create_board(self):
        """Create the initial piece setup."""
        # Create an empty 8x8 board
        board = [[None for _ in range(8)] for _ in range(8)]

        # Place black pawns on rank 7 (index 1)
        for c in range(8):
            board[1][c] = Piece("black", "pawn")

        # Place white pawns on rank 2 (index 6)
        for c in range(8):
            board[6][c] = Piece("white", "pawn")

        # Back-rank piece order
        placement = [
            "rook",
            "knight",
            "bishop",
            "queen",
            "king",
            "bishop",
            "knight",
            "rook",
        ]

        # Place black pieces on rank 8 (index 0)
        for c, type_ in enumerate(placement):
            board[0][c] = Piece("black", type_)

        # Place white pieces on rank 1 (index 7)
        for c, type_ in enumerate(placement):
            board[7][c] = Piece("white", type_)

        return board

    def switch_turn(self):
        """Switch the active player."""
        self.turn = "black" if self.turn == "white" else "white"

    def get_all_possible_moves(self, color, board_state=None):
        """
        Return all pseudo-legal moves for every piece of the given color.

        These moves do not validate whether the king remains safe.
        """
        # Use the current board unless an alternate state is provided
        board = board_state if board_state else self.board
        moves = []

        # Scan every square on the board
        for r in range(8):
            for c in range(8):
                piece = board[r][c]

                # Process pieces of the requested color only
                if piece and piece.color == color:
                    # Generate all moves for the piece
                    valid_moves = self.get_valid_moves_for_piece(r, c, board)

                    # Store each move together with its source square
                    for move in valid_moves:
                        moves.append(((r, c), move))

        return moves

    def get_valid_moves_for_piece(self, r, c, board):
        """
        Return all pseudo-legal moves for the piece on square (r, c).

        These moves do not validate whether the king remains safe.
        """
        piece = board[r][c]
        moves = []

        # Movement vectors for each piece type
        directions = {
            "rook": [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
            ],  # Rook: up, down, left, right
            "bishop": [
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1)
            ],  # Bishop: four diagonals
            "knight": [
                (-2, -1),
                (-2, 1),
                (-1, -2),
                (-1, 2),
                (1, -2),
                (1, 2),
                (2, -1),
                (2, 1),
            ],  # Knight: L-shaped jumps
            "king": [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            ],  # King: adjacent squares
        }

        # Queen = rook + bishop
        directions["queen"] = directions["rook"] + directions["bishop"]

        # ==================== PAWN ====================
        if piece.type == "pawn":
            # White pawns move upward (r-1), black pawns downward (r+1)
            direction = -1 if piece.color == "white" else 1

            # Single forward move
            if 0 <= r + direction < 8 and board[r + direction][c] is None:
                moves.append((r + direction, c))

                # Double-step move from the starting rank
                start_row = 6 if piece.color == "white" else 1
                if r == start_row and board[r + direction * 2][c] is None:
                    moves.append((r + direction * 2, c))

            # Diagonal captures
            for dc in [-1, 1]:
                if 0 <= r + direction < 8 and 0 <= c + dc < 8:
                    target = board[r + direction][c + dc]
                    # Capture only enemy pieces
                    if target and target.color != piece.color:
                        moves.append((r + direction, c + dc))

        # ==================== KNIGHT AND KING ====================
        elif piece.type in ["knight", "king"]:
            for dr, dc in directions[piece.type]:
                nr, nc = r + dr, c + dc  # New position

                # Stay within board boundaries
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board[nr][nc]

                    # The move is valid if the square is empty or occupied by an enemy
                    if target is None or target.color != piece.color:
                        moves.append((nr, nc))

        # ==================== ROOK, BISHOP, QUEEN ====================
        elif piece.type in ["rook", "bishop", "queen"]:
            for dr, dc in directions[piece.type]:
                # Walk as far as possible in the selected direction
                for i in range(1, 8):
                    nr, nc = r + dr * i, c + dc * i

                    # Stop once the path leaves the board
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        target = board[nr][nc]

                        if target is None:
                            # Empty square: add it and keep moving
                            moves.append((nr, nc))
                        elif target.color != piece.color:
                            # Enemy piece: capture is allowed, but movement stops here
                            moves.append((nr, nc))
                            break
                        else:
                            # Friendly piece blocks the path
                            break
                    else:
                        break

        return moves

    def is_check(self, color, board):
        """
        Check whether the king of the given color is in check.

        color: 'white' or 'black'
        board: current board state
        """
        # Locate the king of the requested color
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and p.type == "king" and p.color == color:
                    king_pos = (r, c)
                    break

        if not king_pos:
            # The king is missing, which should not happen in a real game
            return False

        # Determine the opponent color
        opponent = "black" if color == "white" else "white"

        # Check whether any opponent move attacks the king
        for r in range(8):
            for c in range(8):
                p = board[r][c]

                # Only consider opponent pieces
                if p and p.color == opponent:
                    # Generate all moves for the piece
                    moves = self.get_valid_moves_for_piece(r, c, board)

                    # If the king square is attacked, the king is in check
                    if king_pos in moves:
                        return True

        return False

    def get_legal_moves(self, r, c):
        """
        Return only legal moves for the piece on square (r, c).

        A legal move is one that does not leave the king in check.
        """
        piece = self.board[r][c]

        # Validate that a piece exists and that it belongs to the active player
        if not piece or piece.color != self.turn:
            return []

        # Generate pseudo-legal moves
        pseudo_moves = self.get_valid_moves_for_piece(r, c, self.board)
        legal_moves = []

        # Validate each move by simulating it on a copied board
        for move in pseudo_moves:
            temp_board = [row[:] for row in self.board]  # Shallow-copy each row
            temp_board[move[0]][move[1]] = temp_board[r][c]  # Move the piece
            temp_board[r][c] = None  # Clear the original square

            # Keep only moves that leave the king safe
            if not self.is_check(self.turn, temp_board):
                legal_moves.append(move)

        return legal_moves

    def make_move(self, start, end):
        """
        Execute a move from start to end.

        Returns True on success and False if the move is invalid.
        """
        r1, c1 = start  # Source square
        r2, c2 = end  # Destination square
        piece = self.board[r1][c1]

        # Ensure there is a piece on the source square
        if not piece:
            return False

        # Prevent moving the opponent's piece
        if piece.color != self.turn:
            return False

        # Generate legal moves for the selected piece
        legal_moves = self.get_legal_moves(r1, c1)

        # Reject the move if it is not legal
        if (r2, c2) not in legal_moves:
            return False

        # Save the current state for undo
        state_snapshot = {
            "board": copy.deepcopy(self.board),  # Deep copy of the board
            "turn": self.turn,
            "move_count": self.move_count,
            "game_over": self.game_over,
        }
        self.move_log.append(state_snapshot)

        # Execute the move
        self.board[r2][c2] = self.board[r1][c1]  # Move the piece
        self.board[r1][c1] = None  # Clear the original square

        # Promote a pawn to a queen when it reaches the last rank
        if piece.type == "pawn" and (r2 == 0 or r2 == 7):
            self.board[r2][c2].type = "queen"

        # Pass the turn to the other player
        self.switch_turn()
        self.move_count += 1

        # Check for checkmate
        if self.is_checkmate():
            self.game_over = True
            # The winner is the player who just moved
            self.winner = "black" if self.turn == "white" else "white"

        return True

    def is_checkmate(self):
        """
        Check whether the current player is in checkmate.

        Checkmate = king is in check and no legal move can resolve it.
        """
        # If there is no check, there is no checkmate
        if not self.is_check(self.turn, self.board):
            return False

        # Generate all moves for the current player
        all_moves = self.get_all_possible_moves(self.turn, self.board)

        # If any move removes the check, it is not checkmate
        for start, end in all_moves:
            temp_board = [row[:] for row in self.board]
            temp_board[end[0]][end[1]] = temp_board[start[0]][start[1]]
            temp_board[start[0]][start[1]] = None

            if not self.is_check(self.turn, temp_board):
                return False

        return True

    def undo_move(self):
        """Undo the last move and restore the previous game state."""
        # Ensure that move history is not empty
        if not self.move_log:
            return False

        # Restore the most recent saved state
        state = self.move_log.pop()

        self.board = state["board"]
        self.turn = state["turn"]
        self.move_count = state["move_count"]
        self.game_over = state["game_over"]
        self.winner = None

        return True


# ==========================
# Console interface
# ==========================


def print_board(board):
    """Print the board with coordinates and Unicode piece symbols."""
    # Print file labels across the top
    print("    a  b  c  d  e  f  g  h")

    # Print each rank
    for r in range(8):
        # Rank label on the left
        row_s = f"{8 - r} |"

        # Print every square in the current rank
        for c in range(8):
            piece = board[r][c]

            if piece:
                # Render the piece symbol
                row_s += f" {piece.symbol()} "
            else:
                # Render an empty square marker
                row_s += " . "

        # Duplicate the rank label on the right
        row_s += f"| {8 - r}"
        print(row_s)

    # Print file labels across the bottom
    print("    a  b  c  d  e  f  g  h\n")


def parse_move(move_str):
    """
    Parse a move string such as 'e2e4' into board coordinates.

    Returns ((r1, c1), (r2, c2)) or None if the format is invalid.
    """
    try:
        # The move string must be exactly 4 characters long
        if len(move_str) != 4:
            return None

        # Parse the first square (for example, "e2")
        c1 = ord(move_str[0].lower()) - ord("a")
        r1 = 8 - int(move_str[1])

        # Parse the second square (for example, "e4")
        c2 = ord(move_str[2].lower()) - ord("a")
        r2 = 8 - int(move_str[3])

        # Reject coordinates outside the board range
        if any(x < 0 or x > 7 for x in [r1, r2, c1, c2]):
            return None

        return (r1, c1), (r2, c2)

    except Exception:
        # Invalid numeric or indexing input
        return None


def main():
    """Run the main game loop."""
    # Create a new game with the initial setup
    engine = ChessEngine()

    print("=" * 50)
    print("Welcome to console chess!")
    print("=" * 50)
    print("To move, enter a command like 'e2e4' (from square, to square).")
    print("Commands: 'undo' to revert the last move, 'q' to quit.")
    print("=" * 50)
    print()

    # Show the initial position
    print_board(engine.board)

    # Main game loop
    while True:
        # Check whether the game has ended
        if engine.game_over:
            print("=" * 50)
            print(f"CHECKMATE! {engine.winner.upper()} wins!")
            print("=" * 50)

            # Ask whether the user wants to start a new game
            cmd = input("Start a new game? (y/n): ").strip()

            if cmd.lower().startswith("y"):
                # Reset the game
                engine = ChessEngine()
                print_board(engine.board)
                continue
            else:
                # Exit the program
                print("Thanks for playing!")
                break

        # Show whose turn it is
        current_player = "WHITE" if engine.turn == "white" else "BLACK"
        print(f"Turn: {current_player} | Total moves: {engine.move_count}")

        # Ask the player for input
        move_str = input("Enter move: ").strip()

        # Handle special commands
        if move_str.lower() in ["q", "quit", "exit"]:
            print("Exiting the game. Goodbye!")
            break

        if move_str.lower() == "undo":
            # Revert the last move
            if engine.undo_move():
                print("\n✓ Move undone\n")
                print_board(engine.board)
            else:
                print("\n✗ Cannot undo the move (history is empty)\n")
            continue

        # Parse the move
        move = parse_move(move_str)

        if not move:
            # Invalid input format
            print("\n✗ Invalid format. Example: e2e4\n")
            continue

        # Execute the move
        start, end = move
        if not engine.make_move(start, end):
            # The move is illegal
            print("\n✗ Illegal move. (King in check? Path blocked?)\n")
            continue

        # Show the updated board after a successful move
        print()
        print_board(engine.board)


if __name__ == "__main__":
    # Start the game
    main()
