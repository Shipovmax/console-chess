"""
Тесты для Задания 1: Новые виды фигур ("Сказочные шахматы").
Сложность: 1
"""

import pytest
from main import ChessEngine, Piece


@pytest.fixture
def empty_engine():
    """Фикстура: движок с пустой доской для удобного тестирования ходов."""
    engine = ChessEngine()
    engine.board = [[None for _ in range(8)] for _ in range(8)]
    return engine


def test_fairy_board_initialization():
    """Проверка правильности расстановки сказочных фигур."""
    engine = ChessEngine(mode="fairy")

    # Проверяем первый ряд черных (строка 0)
    assert engine.board[0][1].type == "jumper"
    assert engine.board[0][2].type == "wizard"
    assert engine.board[0][3].type == "champion"


def test_champion_moves(empty_engine):
    """Проверка ходов Чемпиона (1-2 клетки по прямой)."""
    engine = empty_engine
    engine.board[4][4] = Piece("white", "champion")

    moves = engine.get_valid_moves_for_piece(4, 4, engine.board)
    expected_moves = [
        (2, 4), (6, 4), (4, 2), (4, 6),  # на 2 клетки
        (3, 4), (5, 4), (4, 3), (4, 5)  # на 1 клетку
    ]

    assert len(moves) == len(expected_moves)
    for move in expected_moves:
        assert move in moves


def test_wizard_moves(empty_engine):
    """Проверка ходов Колдуна (1 или 3 клетки по диагонали)."""
    engine = empty_engine
    engine.board[3][3] = Piece("black", "wizard")

    moves = engine.get_valid_moves_for_piece(3, 3, engine.board)
    expected_moves = [
        (0, 0), (0, 6), (6, 0), (6, 6),  # на 3 клетки
        (2, 2), (2, 4), (4, 2), (4, 4)  # на 1 клетку
    ]

    assert len(moves) == len(expected_moves)
    for move in expected_moves:
        assert move in moves


def test_jumper_moves(empty_engine):
    """Проверка ходов Прыгуна (ровно 2 клетки в любом направлении)."""
    engine = empty_engine
    engine.board[4][4] = Piece("white", "jumper")

    moves = engine.get_valid_moves_for_piece(4, 4, engine.board)
    expected_moves = [
        (2, 2), (2, 6), (6, 2), (6, 6),  # диагонали на 2
        (2, 4), (6, 4), (4, 2), (4, 6)  # прямые на 2
    ]

    assert len(moves) == len(expected_moves)
    for move in expected_moves:
        assert move in moves