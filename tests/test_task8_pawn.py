"""
Тесты для Задания 8: Сложные правила пешки (Взятие на проходе и Превращение).
Сложность: 1
"""

import pytest
from main import ChessEngine, Piece


def test_en_passant():
    """Проверка взятия на проходе."""
    engine = ChessEngine()
    # Очищаем доску
    engine.board = [[None for _ in range(8)] for _ in range(8)]

    # Настраиваем ситуацию: Белая пешка на e5 (3, 4)
    engine.board[3][4] = Piece("white", "pawn")
    # Черная пешка на d7 (1, 3)
    engine.board[1][3] = Piece("black", "pawn")

    # 1. Ход черных d7-d5 (на 2 клетки)
    engine.turn = "black"
    engine.make_move((1, 3), (3, 3))

    # Проверяем, что en_passant_target установился на битое поле d6 (2, 3)
    assert engine.en_passant_target == (2, 3)

    # 2. Ход белых: взятие на проходе e5xd6
    # Пешка должна уметь сходить на (2, 3)
    legal_moves = engine.get_legal_moves(3, 4)
    assert (2, 3) in legal_moves

    engine.make_move((3, 4), (2, 3))

    # Проверяем итог: белая пешка на d6, черная пешка на d5 исчезла
    assert engine.board[2][3] is not None
    assert engine.board[2][3].color == "white"
    assert engine.board[3][3] is None  # Черная пешка уничтожена


def test_pawn_promotion():
    """Проверка превращения пешки на краю доски."""
    engine = ChessEngine()
    engine.board = [[None for _ in range(8)] for _ in range(8)]

    # Белая пешка на a7 (1, 0)
    engine.board[1][0] = Piece("white", "pawn")

    # Делаем ход на a8 (0, 0) и превращаем в коня
    engine.make_move((1, 0), (0, 0), promote_to="knight")

    # Проверяем, что на a8 теперь белый конь
    promoted_piece = engine.board[0][0]
    assert promoted_piece is not None
    assert promoted_piece.type == "knight"
    assert promoted_piece.color == "white"