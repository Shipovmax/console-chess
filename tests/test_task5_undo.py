"""
Тесты для Задания 5: «Откат» ходов.
Сложность: 1
"""

from main import ChessEngine


def test_undo_move():
    """Проверка возврата состояния доски и параметров после хода."""
    engine = ChessEngine()

    # Запоминаем начальное состояние
    initial_piece = engine.board[6][4]  # Белая пешка e2
    assert initial_piece is not None
    assert initial_piece.type == "pawn"

    # Делаем ход e2-e4
    success = engine.make_move((6, 4), (4, 4))
    assert success is True
    assert engine.board[6][4] is None
    assert engine.board[4][4].type == "pawn"
    assert engine.turn == "black"
    assert engine.move_count == 1

    # Откатываем ход
    undo_success = engine.undo_move()
    assert undo_success is True

    # Проверяем, что все вернулось назад
    assert engine.board[6][4].type == "pawn"
    assert engine.board[4][4] is None
    assert engine.turn == "white"
    assert engine.move_count == 0
    assert len(engine.move_log) == 0


def test_undo_empty_log():
    """Проверка поведения при попытке отката в самом начале партии."""
    engine = ChessEngine()
    assert engine.undo_move() is False