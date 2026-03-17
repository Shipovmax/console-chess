"""
Tests for Task 1: New piece types ("Fairy Chess").
Complexity: 1
"""

import pytest
from main import ChessEngine, Piece


@pytest.fixture
def empty_engine():
    """Fixture: engine with an empty board for convenient move testing."""
    engine = ChessEngine()
    engine.board = [[None for _ in range(8)] for _ in range(8)]
    return engine


def test_fairy_board_initialization():
    """Verify the fairy-piece opening setup."""
    engine = ChessEngine(mode="fairy")

    # Validate the black back rank (row 0)
    assert engine.board[0][1].type == "jumper"
    assert engine.board[0][2].type == "wizard"
    assert engine.board[0][3].type == "champion"


def test_champion_moves(empty_engine):
    """Verify Champion moves (1 or 2 squares orthogonally)."""
    engine = empty_engine
    engine.board[4][4] = Piece("white", "champion")

    moves = engine.get_valid_moves_for_piece(4, 4, engine.board)
    expected_moves = [
        (2, 4), (6, 4), (4, 2), (4, 6),  # 2-square moves
        (3, 4), (5, 4), (4, 3), (4, 5)  # 1-square moves
    ]

    assert len(moves) == len(expected_moves)
    for move in expected_moves:
        assert move in moves


def test_wizard_moves(empty_engine):
    """Verify Wizard moves (1 or 3 squares diagonally)."""
    engine = empty_engine
    engine.board[3][3] = Piece("black", "wizard")

    moves = engine.get_valid_moves_for_piece(3, 3, engine.board)
    expected_moves = [
        (0, 0), (0, 6), (6, 0), (6, 6),  # 3-square moves
        (2, 2), (2, 4), (4, 2), (4, 4)  # 1-square moves
    ]

    assert len(moves) == len(expected_moves)
    for move in expected_moves:
        assert move in moves


def test_jumper_moves(empty_engine):
    """Verify Jumper moves (exactly 2 squares in any direction)."""
    engine = empty_engine
    engine.board[4][4] = Piece("white", "jumper")

    moves = engine.get_valid_moves_for_piece(4, 4, engine.board)
    expected_moves = [
        (2, 2), (2, 6), (6, 2), (6, 6),  # diagonal 2-square moves
        (2, 4), (6, 4), (4, 2), (4, 6)  # straight 2-square moves
    ]

    assert len(moves) == len(expected_moves)
    for move in expected_moves:
        assert move in moves
