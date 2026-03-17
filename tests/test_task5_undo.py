"""
Tests for Task 5: Move undo.
Complexity: 1
"""

from main import ChessEngine


def test_undo_move():
    """Verify board state and counters after undoing a move."""
    engine = ChessEngine()

    # Store the initial state
    initial_piece = engine.board[6][4]  # White pawn on e2
    assert initial_piece is not None
    assert initial_piece.type == "pawn"

    # Play e2-e4
    success = engine.make_move((6, 4), (4, 4))
    assert success is True
    assert engine.board[6][4] is None
    assert engine.board[4][4].type == "pawn"
    assert engine.turn == "black"
    assert engine.move_count == 1

    # Undo the move
    undo_success = engine.undo_move()
    assert undo_success is True

    # Verify that everything returned to its original state
    assert engine.board[6][4].type == "pawn"
    assert engine.board[4][4] is None
    assert engine.turn == "white"
    assert engine.move_count == 0
    assert len(engine.move_log) == 0


def test_undo_empty_log():
    """Verify undo behavior at the very start of the game."""
    engine = ChessEngine()
    assert engine.undo_move() is False
