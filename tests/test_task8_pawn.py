"""
Tests for Task 8: Advanced pawn rules (en passant and promotion).
Complexity: 1
"""

import pytest
from main import ChessEngine, Piece


def test_en_passant():
    """Verify en passant capture."""
    engine = ChessEngine()
    # Clear the board
    engine.board = [[None for _ in range(8)] for _ in range(8)]

    # Set up the position: white pawn on e5 (3, 4)
    engine.board[3][4] = Piece("white", "pawn")
    # Black pawn on d7 (1, 3)
    engine.board[1][3] = Piece("black", "pawn")

    # 1. Black plays d7-d5 (two squares)
    engine.turn = "black"
    engine.make_move((1, 3), (3, 3))

    # Verify that en_passant_target points to d6 (2, 3)
    assert engine.en_passant_target == (2, 3)

    # 2. White captures en passant: e5xd6
    # The pawn must be allowed to move to (2, 3)
    legal_moves = engine.get_legal_moves(3, 4)
    assert (2, 3) in legal_moves

    engine.make_move((3, 4), (2, 3))

    # Verify the final position: white pawn on d6, black pawn from d5 removed
    assert engine.board[2][3] is not None
    assert engine.board[2][3].color == "white"
    assert engine.board[3][3] is None  # Captured black pawn


def test_pawn_promotion():
    """Verify pawn promotion on the last rank."""
    engine = ChessEngine()
    engine.board = [[None for _ in range(8)] for _ in range(8)]

    # White pawn on a7 (1, 0)
    engine.board[1][0] = Piece("white", "pawn")

    # Move to a8 (0, 0) and promote to a knight
    engine.make_move((1, 0), (0, 0), promote_to="knight")

    # Verify that a white knight now stands on a8
    promoted_piece = engine.board[0][0]
    assert promoted_piece is not None
    assert promoted_piece.type == "knight"
    assert promoted_piece.color == "white"
