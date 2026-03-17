"""
Tests for Tasks 6 and 7: legal move and threat hints.
Complexity: 2 (1 + 1)
"""

from main import ChessEngine, Piece


def test_legal_destinations_hint():
    """Task 6: verify legal destination generation for a piece."""
    engine = ChessEngine()

    # Pawn on e2 (6, 4) has two opening moves: e3 (5, 4) and e4 (4, 4)
    legal_moves = engine.get_legal_moves(6, 4)
    assert len(legal_moves) == 2
    assert (5, 4) in legal_moves
    assert (4, 4) in legal_moves

    # Knight on g1 (7, 6) can move to f3 (5, 5) and h3 (5, 7)
    knight_moves = engine.get_legal_moves(7, 6)
    assert (5, 5) in knight_moves
    assert (5, 7) in knight_moves


def test_threats_detection():
    """Task 7: verify detection of threatened pieces."""
    engine = ChessEngine()
    # Clear the board for an isolated scenario
    engine.board = [[None for _ in range(8)] for _ in range(8)]

    # Place a white rook on e4 (4, 4)
    engine.board[4][4] = Piece("white", "rook")
    # Place a black pawn on d5 (3, 3) so it attacks e4 diagonally
    engine.board[3][3] = Piece("black", "pawn")

    # White to move. Check whether the white piece is under attack
    opponent = "black"
    moves_with_sources = engine.get_all_possible_moves(opponent)

    threatened_squares = {end for _, end in moves_with_sources}

    # The white rook on (4, 4) must be threatened by the black pawn
    assert (4, 4) in threatened_squares
