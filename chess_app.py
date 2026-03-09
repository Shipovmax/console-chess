import copy


class Piece:
    """Класс, который представляет одну шахматную фигуру"""

    def __init__(self, color, type_):
        self.color = color  # 'white' (белая) или 'black' (черная)
        self.type = type_   # 'pawn' (пешка), 'rook' (ладья), 'knight' (конь),
                            # 'bishop' (слон), 'queen' (королева), 'king' (король)

    def __repr__(self):
        return f"{self.color}_{self.type}"

    def symbol(self):
        """Возвращает Unicode символ фигуры для красивого вывода в консоль"""
        symbols = {   
            "white": {
                "king": "♔",   # Белый король
                "queen": "♕",  # Белая королева
                "rook": "♖",   # Белая ладья
                "bishop": "♗", # Белый слон
                "knight": "♘", # Белый конь
                "pawn": "♙",   # Белая пешка
            },
            "black": {
                "king": "♚",   # Черный король
                "queen": "♛",  # Черная королева
                "rook": "♜",   # Черная ладья
                "bishop": "♝", # Черный слон
                "knight": "♞", # Черный конь
                "pawn": "♟",   # Черная пешка
            },    
        }
        return symbols[self.color][self.type]


class ChessEngine:
    """Главный класс игрового движка шахмат"""

    def __init__(self):
        self.board = self.create_board()    # Создаем доску 8х8
        self.turn = "white"                 # Белые ходят первыми
        self.move_log = []                  # Список всех ходов (для отката)
        self.game_over = False              # Флаг, что игра закончилась
        self.winner = None                  # Кто выиграл (белые или черные)
        self.move_count = 0                 # Количество сделанных ходов

    def create_board(self):
        """Создает начальную расстановку фигур на доске"""
        # Создаем пустую 8x8 доску (8 строк, 8 столбцов)
        board = [[None for _ in range(8)] for _ in range(8)]

        # Расставляем черные пешки на 2-ю строку (индекс 1)
        for c in range(8):
            board[1][c] = Piece("black", "pawn")

        # Расставляем белые пешки на 7-ю строку (индекс 6)
        for c in range(8):
            board[6][c] = Piece("white", "pawn")

        # Порядок расстановки фигур в ряду
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

        # Расставляем черные фигуры на 1-ю строку (индекс 0)
        for c, type_ in enumerate(placement):
            board[0][c] = Piece("black", type_)

        # Расставляем белые фигуры на 8-ю строку (индекс 7)
        for c, type_ in enumerate(placement):
            board[7][c] = Piece("white", type_)

        return board

    def switch_turn(self):
        """Переключает ход с одного игрока на другого"""
        self.turn = "black" if self.turn == "white" else "white"

    def get_all_possible_moves(self, color, board_state=None):
        """
        Получает все возможные ходы для всех фигур заданного цвета.
        Это ходы БЕЗ проверки на оставление короля под шахом.
        """
        # Используем текущую доску или переданное состояние
        board = board_state if board_state else self.board
        moves = []

        # Проходим по каждой клетке доски
        for r in range(8):
            for c in range(8):
                piece = board[r][c]

                # Если на клетке есть фигура нужного цвета
                if piece and piece.color == color:
                    # Получаем все возможные ходы для этой фигуры
                    valid_moves = self.get_valid_moves_for_piece(r, c, board)

                    # Добавляем каждый ход в список вместе с начальной позицией
                    for move in valid_moves:
                        moves.append(((r, c), move))

        return moves

    def get_valid_moves_for_piece(self, r, c, board):
        """
        Получает все возможные ходы для фигуры, стоящей на позиции (r, c).
        Это ходы БЕЗ проверки на оставление короля под шахом.
        """
        piece = board[r][c]
        moves = []

        # Определяем направления движения для разных фигур
        directions = {
            "rook": [
                (-1, 0),
                (1, 0),
                (0, -1),
                (0, 1),
            ],  # Ладья: вверх, вниз, влево, вправо
            "bishop": [
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1)
            ],  # Слон: 4 диагонали
            "knight": [
                (-2, -1),
                (-2, 1),
                (-1, -2),
                (-1, 2),  
                (1, -2),
                (1, 2),
                (2, -1),
                (2, 1),
            ],  # Конь: буква L
            "king": [
                (-1, -1),
                (-1, 0),
                (-1, 1),  
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            ],  # Король: все соседние клетки
        }
        
        # Королева = ладья + слон
        directions["queen"] = directions["rook"] + directions["bishop"]

        # ==================== ПЕШКА ====================
        if piece.type == "pawn":
            # Белые пешки ходят вверх (r-1), черные вниз (r+1)
            direction = -1 if piece.color == "white" else 1

            # Ход пешки на одну клетку вперед
            if 0 <= r + direction < 8 and board[r + direction][c] is None:
                moves.append((r + direction, c))

                # Первый ход пешки - может ходить на две клетки
                start_row = 6 if piece.color == "white" else 1
                if r == start_row and board[r + direction * 2][c] is None:
                    moves.append((r + direction * 2, c))

            # Взятие пешки по диагонали
            for dc in [-1, 1]:  # Влево или вправо
                if 0 <= r + direction < 8 and 0 <= c + dc < 8:
                    target = board[r + direction][c + dc]
                    # Если там враг, можем его взять
                    if target and target.color != piece.color:
                        moves.append((r + direction, c + dc))

        # ==================== КОНЬ И КОРОЛЬ ====================
        elif piece.type in ["knight", "king"]:
            for dr, dc in directions[piece.type]:
                nr, nc = r + dr, c + dc  # Новая позиция

                # Проверяем, что новая позиция на доске
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board[nr][nc]

                    # Можем ходить на пустую клетку или бить врага
                    if target is None or target.color != piece.color:
                        moves.append((nr, nc))

        # ==================== ЛАДЬЯ, СЛОН, КОРОЛЕВА ====================
        elif piece.type in ["rook", "bishop", "queen"]:
            for dr, dc in directions[piece.type]:
                # Идем в каждом направлении максимально далеко
                for i in range(1, 8):
                    nr, nc = r + dr * i, c + dc * i

                    # Проверяем границы доски
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        target = board[nr][nc]

                        if target is None:
                            # Пустая клетка - добавляем и продолжаем в этом направлении
                            moves.append((nr, nc))
                        elif target.color != piece.color:
                            # Враг - добавляем и СТОПИМ (не идем дальше)
                            moves.append((nr, nc))
                            break
                        else:
                            # Своя фигура - это преграда, СТОПИМ
                            break
                    else:
                        # За границей доски - СТОПИМ
                        break

        return moves

    def is_check(self, color, board):
        """
        Проверяет, находится ли король заданного цвета под шахом.
        color: 'white' или 'black'
        board: текущее состояние доски
        """
        # Находим короля нашего цвета
        king_pos = None
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and p.type == "king" and p.color == color:
                    king_pos = (r, c)
                    break

        if not king_pos:
            # Король не найден (теоретически невозможно в реальной игре)
            return False

        # Определяем цвет противника
        opponent = "black" if color == "white" else "white"

        # Проверяем может ли противник атаковать нашего короля
        for r in range(8):
            for c in range(8):
                p = board[r][c]

                # Если это фигура противника
                if p and p.color == opponent:
                    # Получаем все ходы этой фигуры
                    moves = self.get_valid_moves_for_piece(r, c, board)

                    # Если король в списке ходов - это шах!
                    if king_pos in moves:
                        return True

        return False

    def get_legal_moves(self, r, c):
        """
        Получает только ЛЕГАЛЬНЫЕ ходы для фигуры на позиции (r, c).
        Легальный ход - это тот, после которого король не остается под шахом.
        """
        piece = self.board[r][c]

        # Проверяем есть ли фигура и чей это ход
        if not piece or piece.color != self.turn:
            return []

        # Получаем все возможные ходы (без проверки на шах)
        pseudo_moves = self.get_valid_moves_for_piece(r, c, self.board)
        legal_moves = []

        # Для каждого хода проверяем не оставляет ли он короля под шахом
        for move in pseudo_moves:
            # Симулируем ход на копии доски
            temp_board = [row[:] for row in self.board]  # Копируем доску
            temp_board[move[0]][move[1]] = temp_board[r][c]  # Переносим фигуру
            temp_board[r][c] = None  # Очищаем старую позицию

            # Проверяем остался ли наш король под шахом
            if not self.is_check(self.turn, temp_board):
                # Ход легален!
                legal_moves.append(move)

        return legal_moves

    def make_move(self, start, end):
        """
        Выполняет ход от позиции start к позиции end.
        Возвращает True если ход успешен, False если ход недопустим.
        """
        r1, c1 = start  # Откуда ходим
        r2, c2 = end  # Куда ходим
        piece = self.board[r1][c1]

        # Проверяем есть ли фигура на начальной позиции
        if not piece:
            return False

        # Проверяем чей это ход (нельзя ходить фигурой другого цвета)
        if piece.color != self.turn:
            return False

        # Получаем легальные ходы для этой фигуры
        legal_moves = self.get_legal_moves(r1, c1)

        # Проверяем легален ли желаемый ход
        if (r2, c2) not in legal_moves:
            return False

        # Сохраняем текущее состояние для отката
        state_snapshot = {
            "board": copy.deepcopy(self.board),  # Глубокая копия доски
            "turn": self.turn,
            "move_count": self.move_count,
            "game_over": self.game_over,
        }
        self.move_log.append(state_snapshot)

        # Выполняем ход
        self.board[r2][c2] = self.board[r1][c1]  # Перемещаем фигуру
        self.board[r1][c1] = None  # Очищаем старую позицию

        # Превращение пешки в королеву при достижении конца доски
        if piece.type == "pawn" and (r2 == 0 or r2 == 7):
            self.board[r2][c2].type = "queen"

        # Переключаемся на следующего игрока
        self.switch_turn()
        self.move_count += 1

        # Проверяем наступил ли мат
        if self.is_checkmate():
            self.game_over = True
            # Победил тот, кто только что ходил (противник текущего игрока)
            self.winner = "black" if self.turn == "white" else "white"

        return True

    def is_checkmate(self):
        """
        Проверяет наступил ли мат.
        Мат = король под шахом И нет ни одного легального хода
        """
        # Сначала проверяем есть ли шах вообще
        if not self.is_check(self.turn, self.board):
            return False  # Нет шаха = нет мата

        # Получаем все возможные ходы текущего игрока
        all_moves = self.get_all_possible_moves(self.turn, self.board)

        # Проверяем есть ли хоть один ход, который спасает от шаха
        for start, end in all_moves:
            # Симулируем ход
            temp_board = [row[:] for row in self.board]
            temp_board[end[0]][end[1]] = temp_board[start[0]][start[1]]
            temp_board[start[0]][start[1]] = None

            # Если после этого хода король не под шахом - это спасение!
            if not self.is_check(self.turn, temp_board):
                return False  # Не мат, есть спасительный ход

        return True  # МАТ! Нет ни одного спасительного хода

    def undo_move(self):
        """
        Отменяет последний ход и восстанавливает предыдущее состояние игры.
        """
        # Проверяем есть ли ходы в истории
        if not self.move_log:
            return False

        # Берем последнее сохраненное состояние и удаляем его из истории
        state = self.move_log.pop()

        # Восстанавливаем все параметры из сохраненного состояния
        self.board = state["board"]
        self.turn = state["turn"]
        self.move_count = state["move_count"]
        self.game_over = state["game_over"]
        self.winner = None

        return True


# ==========================
# Консольный интерфейс
# ==========================


def print_board(board):
    """Красиво выводит доску в консоль с координатами и Unicode символами"""
    # Выводим буквы столбцов сверху (a-h)
    print("    a  b  c  d  e  f  g  h")

    # Проходимся по каждой строке доски
    for r in range(8):
        # Номер ряда слева (8, 7, 6, ..., 1)
        row_s = f"{8 - r} |"

        # Проходимся по каждому столбцу (a-h)
        for c in range(8):
            piece = board[r][c]

            if piece:
                # Выводим символ фигуры
                row_s += f" {piece.symbol()} "
            else:
                # Выводим точку (пустая клетка)
                row_s += " . "

        # Номер ряда справа (дублируем для удобства)
        row_s += f"| {8 - r}"
        print(row_s)

    # Выводим буквы столбцов снизу (a-h)
    print("    a  b  c  d  e  f  g  h\n")


def parse_move(move_str):
    """
    Парсит строку хода типа 'e2e4' в координаты доски.
    Возвращает ((r1, c1), (r2, c2)) или None если формат неправильный.
    """
    try:
        # Проверяем длину строки (должна быть ровно 4 символа)
        if len(move_str) != 4:
            return None

        # Парсим первую позицию (например, "e2")
        # ord('a') = 97, ord('e') = 101, поэтому ord('e') - ord('a') = 4 (столбец e)
        c1 = ord(move_str[0].lower()) - ord("a")
        # ord('2') = 50, int('2') = 2, поэтому 8 - 2 = 6 (строка 2 в индексе массива это 6)
        r1 = 8 - int(move_str[1])

        # Парсим вторую позицию (например, "e4")
        c2 = ord(move_str[2].lower()) - ord("a")
        r2 = 8 - int(move_str[3])

        # Проверяем все координаты в пределах доски (0-7)
        if any(x < 0 or x > 7 for x in [r1, r2, c1, c2]):
            return None

        return (r1, c1), (r2, c2)

    except Exception:
        # Если произошла ошибка (например, не число вместо цифры)
        return None


def main():
    """Главная функция - основной игровой цикл"""
    # Создаем новый движок (начальная расстановка)
    engine = ChessEngine()

    print("=" * 50)
    print("Добро пожаловать в консольные шахматы!")
    print("=" * 50)
    print("Как ходить: введите ход в формате 'e2e4' (от куда, куда)")
    print("Команды: 'undo' - отменить ход, 'q' - выход")
    print("=" * 50)
    print()

    # Выводим начальную позицию
    print_board(engine.board)

    # Основной игровой цикл
    while True:
        # Проверяем наступил ли мат
        if engine.game_over:
            print("=" * 50)
            print(f"МАТ! Победили {engine.winner.upper()}!")
            print("=" * 50)

            # Спрашиваем хочет ли игрок новую партию
            cmd = input("Хотите новую игру? (y/n): ").strip()

            if cmd.lower().startswith("y"):
                # Создаем новую игру
                engine = ChessEngine()
                print_board(engine.board)
                continue
            else:
                # Выходим из программы
                print("Спасибо за игру!")
                break

        # Показываем чей ход
        current_player = "БЕЛЫЕ" if engine.turn == "white" else "ЧЕРНЫЕ"
        print(f"Ход: {current_player} | Всего ходов: {engine.move_count}")

        # Запрашиваем ход у игрока
        move_str = input("Введите ход: ").strip()

        # Проверяем специальные команды
        if move_str.lower() in ["q", "quit", "exit"]:
            print("Выход из игры. До свидания!")
            break  # Выходим из игры

        if move_str.lower() == "undo":
            # Отменяем последний ход
            if engine.undo_move():
                print("\n✓ Ход отменен\n")
                print_board(engine.board)
            else:
                print("\n✗ Нельзя отменить ход (история пуста)\n")
            continue  # Переходим к следующей итерации

        # Парсим ход
        move = parse_move(move_str)

        if not move:
            # Неправильный формат
            print("\n✗ Неправильный формат! Пример: e2e4\n")
            continue  # Просим ввести снова

        # Выполняем ход
        start, end = move
        if not engine.make_move(start, end):
            # Ход не сработал (недопустим)
            print("\n✗ Неверный ход! (Король под шахом? Свой путь закрыт?)\n")
            continue  # Ход не сработал, пробуем снова

        # Ход выполнен успешно - показываем обновленную доску
        print()
        print_board(engine.board)


if __name__ == "__main__":
    # Запускаем игру
    main()
