"""
Тесты для Заданий 6 и 7: Подсказки доступных ходов и угроз.
Сложность: 2 (1 + 1)
"""

from main import ChessEngine, Piece


def test_legal_destinations_hint():
    """Задание 6: Проверка генерации легальных полей для фигуры."""
    engine = ChessEngine()

    # Для пешки e2 (6, 4) доступно 2 хода со старта: e3 (5, 4) и e4 (4, 4)
    legal_moves = engine.get_legal_moves(6, 4)
    assert len(legal_moves) == 2
    assert (5, 4) in legal_moves
    assert (4, 4) in legal_moves

    # Для коня g1 (7, 6) доступны f3 (5, 5) и h3 (5, 7)
    knight_moves = engine.get_legal_moves(7, 6)
    assert (5, 5) in knight_moves
    assert (5, 7) in knight_moves


def test_threats_detection():
    """Задание 7: Проверка обнаружения фигур под боем (угроз)."""
    engine = ChessEngine()
    # Очищаем доску для чистоты эксперимента
    engine.board = [[None for _ in range(8)] for _ in range(8)]

    # Ставим белую ладью на e4 (4, 4)
    engine.board[4][4] = Piece("white", "rook")
    # Ставим черную пешку на d5 (3, 3) - она бьет по диагонали на e4
    engine.board[3][3] = Piece("black", "pawn")

    # Ход белых. Проверяем, находится ли белая фигура под ударом
    opponent = "black"
    moves_with_sources = engine.get_all_possible_moves(opponent)

    threatened_squares = {end for _, end in moves_with_sources}

    # Белая ладья на (4, 4) должна быть под ударом черной пешки
    assert (4, 4) in threatened_squares