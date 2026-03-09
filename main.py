"""
Главный модуль шахматного эмулятора.

Реализованы дополнительные задания: 1, 5, 6, 7, 8 (Суммарная сложность: 5).
Обеспечивает логику шахматной игры, включая стандартный режим и "сказочные"
шахматы с новыми фигурами, а также пользовательский интерфейс в консоли.
"""

import copy
import os
import sys
from typing import List, Tuple, Optional, Dict, Any, Set

# Цветовые константы для вывода текста
GREEN_COLOR: str = "\033[92m"
BLUE_COLOR: str = "\033[94m"
YELLOW_COLOR: str = "\033[93m"
RED_COLOR: str = "\033[91m"
CYAN_COLOR: str = "\033[96m"
MAGENTA_COLOR: str = "\033[95m"
RESET_COLOR: str = "\033[0m"

# Фоновые цвета для шахматной доски и подсветки
BG_LIGHT: str = "\033[47m"
BG_DARK: str = "\033[100m"
BG_GREEN: str = "\033[42m"
BG_RED: str = "\033[41m"
BG_MAGENTA: str = "\033[45m"


class Piece:
    """
    Класс, представляющий шахматную фигуру.

    Поддерживает как классические фигуры, так и новые из Задания 1
    (чемпион, колдун, прыгун).
    """

    def __init__(self, color: str, type_: str) -> None:
        """
        Инициализирует шахматную фигуру.

        :param color: Цвет фигуры ('white' или 'black').
        :param type_: Тип фигуры (например, 'king', 'champion', 'pawn').
        """
        self.color = color
        self.type = type_

    def __repr__(self) -> str:
        """Возвращает техническое строковое представление фигуры."""
        return f"{self.color}_{self.type}"

    def symbol(self) -> str:
        """
        Возвращает юникод-символ фигуры с соответствующим цветом.

        :return: Строка с ANSI-кодом цвета и символом фигуры.
        """
        symbols: Dict[str, Dict[str, str]] = {
            "white": {
                "king": "♔", "queen": "♕", "rook": "♖", "bishop": "♗",
                "knight": "♘", "pawn": "♙", "champion": "★", "wizard": "✧",
                "jumper": "⚶",
            },
            "black": {
                "king": "♚", "queen": "♛", "rook": "♜", "bishop": "♝",
                "knight": "♞", "pawn": "♟", "champion": "★", "wizard": "✧",
                "jumper": "⚶",
            },
        }

        sym = symbols[self.color].get(self.type, "?")
        if self.color == "white":
            return f"{YELLOW_COLOR}{sym}{RESET_COLOR}"
        return f"{BLUE_COLOR}{sym}{RESET_COLOR}"


class ChessEngine:
    """
    Движок шахматной игры.

    Обрабатывает логику перемещений, правила взятия на проходе,
    превращения пешек, проверку шахов и матов, а также историю ходов.
    """

    def __init__(self, mode: str = "standard") -> None:
        """
        Инициализирует состояние игры и шахматную доску.

        :param mode: Режим игры ('standard' или 'fairy').
        """
        self.mode = mode
        self.board: List[List[Optional[Piece]]] = self.create_board(mode)
        self.turn: str = "white"
        self.move_log: List[Dict[str, Any]] = []
        self.game_over: bool = False
        self.winner: Optional[str] = None
        self.move_count: int = 0
        self.en_passant_target: Optional[Tuple[int, int]] = None

    def create_board(self, mode: str) -> List[List[Optional[Piece]]]:
        """
        Создает начальную расстановку фигур на доске.

        :param mode: Режим игры (стандартный или с новыми фигурами).
        :return: Двумерный список 8x8 с объектами Piece и пустыми клетками (None).
        """
        board: List[List[Optional[Piece]]] = [
            [None for _ in range(8)] for _ in range(8)
        ]

        # Расстановка пешек
        for c in range(8):
            board[1][c] = Piece("black", "pawn")
            board[6][c] = Piece("white", "pawn")

        # Определение расстановки первого ряда
        if mode == "fairy":
            placement = [
                "rook", "jumper", "wizard", "champion",
                "king", "wizard", "jumper", "rook"
            ]
        else:
            placement = [
                "rook", "knight", "bishop", "queen",
                "king", "bishop", "knight", "rook"
            ]

        # Расстановка тяжелых фигур
        for c, type_ in enumerate(placement):
            board[0][c] = Piece("black", type_)
            board[7][c] = Piece("white", type_)

        return board

    def switch_turn(self) -> None:
        """Передает ход следующему игроку."""
        self.turn = "black" if self.turn == "white" else "white"

    def get_valid_moves_for_piece(
        self, r: int, c: int, board: List[List[Optional[Piece]]]
    ) -> List[Tuple[int, int]]:
        """
        Генерирует все возможные (псевдолегальные) ходы для фигуры.

        Игнорирует проверку на шах собственному королю. Поддерживает
        сложные правила пешек и кастомных фигур.

        :param r: Строка расположения фигуры.
        :param c: Столбец расположения фигуры.
        :param board: Текущее состояние доски для анализа.
        :return: Список координат (строка, столбец) доступных ходов.
        """
        piece = board[r][c]
        if not piece:
            return []

        moves: List[Tuple[int, int]] = []
        directions: Dict[str, List[Tuple[int, int]]] = {
            "rook": [(-1, 0), (1, 0), (0, -1), (0, 1)],
            "bishop": [(-1, -1), (-1, 1), (1, -1), (1, 1)],
            "knight": [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1),
            ],
            "king": [
                (-1, -1), (-1, 0), (-1, 1), (0, -1),
                (0, 1), (1, -1), (1, 0), (1, 1),
            ],
            "champion": [
                (-2, 0), (2, 0), (0, -2), (0, 2),
                (-1, 0), (1, 0), (0, -1), (0, 1),
            ],
            "wizard": [
                (-3, -3), (-3, 3), (3, -3), (3, 3),
                (-1, -1), (-1, 1), (1, -1), (1, 1),
            ],
            "jumper": [
                (-2, -2), (-2, 2), (2, -2), (2, 2),
                (-2, 0), (2, 0), (0, -2), (0, 2),
            ],
        }
        directions["queen"] = directions["rook"] + directions["bishop"]

        # Правила движения пешки
        if piece.type == "pawn":
            direction = -1 if piece.color == "white" else 1
            next_row = r + direction

            # Ход вперед
            if 0 <= next_row < 8 and board[next_row][c] is None:
                moves.append((next_row, c))
                start_row = 6 if piece.color == "white" else 1

                # Двойной ход со стартовой позиции
                if r == start_row and board[next_row + direction][c] is None:
                    moves.append((next_row + direction, c))

            # Диагональные взятия
            for dc in [-1, 1]:
                if 0 <= next_row < 8 and 0 <= c + dc < 8:
                    target = board[next_row][c + dc]
                    # Обычное взятие
                    if target and target.color != piece.color:
                        moves.append((next_row, c + dc))
                    # Взятие на проходе
                    elif self.en_passant_target == (next_row, c + dc):
                        moves.append((next_row, c + dc))

        # Прыгающие фигуры (конь, король и новые сказочные фигуры)
        elif piece.type in ["knight", "king", "champion", "wizard", "jumper"]:
            for dr, dc in directions[piece.type]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board[nr][nc]
                    if target is None or target.color != piece.color:
                        moves.append((nr, nc))

        # Дальнобойные фигуры (ладья, слон, ферзь)
        elif piece.type in ["rook", "bishop", "queen"]:
            for dr, dc in directions[piece.type]:
                for i in range(1, 8):
                    nr, nc = r + dr * i, c + dc * i
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        target = board[nr][nc]
                        if target is None:
                            moves.append((nr, nc))
                        elif target.color != piece.color:
                            moves.append((nr, nc))
                            break
                        else:
                            break
                    else:
                        break
        return moves

    def is_check(self, color: str, board: List[List[Optional[Piece]]]) -> bool:
        """
        Проверяет, находится ли король указанного цвета под шахом.

        :param color: Цвет короля для проверки ('white' или 'black').
        :param board: Состояние доски.
        :return: True, если королю объявлен шах, иначе False.
        """
        king_pos: Optional[Tuple[int, int]] = None

        # Поиск короля
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and p.type == "king" and p.color == color:
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        if not king_pos:
            return False

        opponent = "black" if color == "white" else "white"

        # Проверка всех ходов оппонента
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and p.color == opponent:
                    moves = self.get_valid_moves_for_piece(r, c, board)
                    if king_pos in moves:
                        return True
        return False

    def get_legal_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """
        Возвращает список полностью легальных ходов для фигуры.

        Отфильтровывает ходы, которые приводят к шаху собственному королю.

        :param r: Строка расположения фигуры.
        :param c: Столбец расположения фигуры.
        :return: Список легальных конечных координат.
        """
        piece = self.board[r][c]
        if not piece or piece.color != self.turn:
            return []

        pseudo_moves = self.get_valid_moves_for_piece(r, c, self.board)
        legal_moves: List[Tuple[int, int]] = []

        for move in pseudo_moves:
            # Создаем временную копию доски для симуляции хода
            temp_board = [row[:] for row in self.board]
            temp_board[move[0]][move[1]] = temp_board[r][c]
            temp_board[r][c] = None

            # Эмуляция взятия на проходе для корректной проверки шаха
            if piece.type == "pawn" and move == self.en_passant_target:
                temp_board[r][move[1]] = None

            # Если после хода королю не шах, ход легален
            if not self.is_check(self.turn, temp_board):
                legal_moves.append(move)

        return legal_moves

    def get_all_possible_moves(
        self, color: str, board_state: Optional[List[List[Optional[Piece]]]] = None
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Собирает абсолютно все легальные ходы для указанного цвета.

        :param color: Цвет фигур ('white' или 'black').
        :param board_state: Опциональное состояние доски (по умолчанию текущее).
        :return: Список пар координат ((откуда), (куда)).
        """
        board = board_state if board_state else self.board
        moves: List[Tuple[Tuple[int, int], Tuple[int, int]]] = []

        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.color == color:
                    valid_moves = self.get_valid_moves_for_piece(r, c, board)
                    for move in valid_moves:
                        moves.append(((r, c), move))
        return moves

    def is_checkmate(self) -> bool:
        """
        Проверяет, поставлен ли мат текущему игроку.

        :return: True, если мат поставлен, иначе False.
        """
        if not self.is_check(self.turn, self.board):
            return False

        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color == self.turn:
                    if len(self.get_legal_moves(r, c)) > 0:
                        return False
        return True

    def make_move(self, start: Tuple[int, int], end: Tuple[int, int], promote_to: str = "queen") -> bool:
        """
        Осуществляет ход фигурой, обновляя состояние игры.

        Сохраняет историю ходов, обрабатывает взятие на проходе и превращение пешки.

        :param start: Координаты начала (строка, столбец).
        :param end: Координаты конца (строка, столбец).
        :param promote_to: Тип фигуры, в которую превращается пешка.
        :return: True, если ход выполнен успешно, иначе False.
        """
        r1, c1 = start
        r2, c2 = end
        piece = self.board[r1][c1]

        if not piece or piece.color != self.turn:
            return False

        legal_moves = self.get_legal_moves(r1, c1)
        if (r2, c2) not in legal_moves:
            return False

        # Сохранение снимка текущего состояния для возможности отката (undo)
        state_snapshot = {
            "board": copy.deepcopy(self.board),
            "turn": self.turn,
            "move_count": self.move_count,
            "game_over": self.game_over,
            "en_passant_target": self.en_passant_target,
        }
        self.move_log.append(state_snapshot)

        # Выполняем взятие на проходе
        if piece.type == "pawn" and (r2, c2) == self.en_passant_target:
            self.board[r1][c2] = None

        # Установка флага для возможного взятия на проходе на следующем ходу
        if piece.type == "pawn" and abs(r1 - r2) == 2:
            self.en_passant_target = ((r1 + r2) // 2, c1)
        else:
            self.en_passant_target = None

        # Перемещение фигуры
        self.board[r2][c2] = self.board[r1][c1]
        self.board[r1][c1] = None

        # Превращение пешки при достижении края доски
        if piece.type == "pawn" and (r2 == 0 or r2 == 7):
            promoted_piece = self.board[r2][c2]
            if promoted_piece:  # Защита типов
                promoted_piece.type = promote_to

        self.switch_turn()
        self.move_count += 1

        if self.is_checkmate():
            self.game_over = True
            self.winner = "black" if self.turn == "white" else "white"

        return True

    def undo_move(self) -> bool:
        """
        Отменяет последний сделанный ход, возвращая игру к предыдущему состоянию.

        :return: True, если отмена прошла успешно, иначе False.
        """
        if not self.move_log:
            return False

        state = self.move_log.pop()
        self.board = state["board"]
        self.turn = state["turn"]
        self.move_count = state["move_count"]
        self.game_over = state["game_over"]
        self.en_passant_target = state["en_passant_target"]
        self.winner = None

        return True


def parse_square(sq_str: str) -> Optional[Tuple[int, int]]:
    """
    Преобразует строковые координаты шахматной доски в индексы массива.

    :param sq_str: Строка с координатами (например, 'e2').
    :return: Кортеж с индексами (строка, столбец) или None в случае неверного ввода.
    """
    try:
        c = ord(sq_str[0].lower()) - ord("a")
        r = 8 - int(sq_str[1])
        if 0 <= r < 8 and 0 <= c < 8:
            return (r, c)
    except (IndexError, ValueError):
        pass
    return None


class AdvancedChessEmulator:
    """
    Пользовательский интерфейс и машина состояний (State Machine) игры.

    Обеспечивает взаимодействие с пользователем через консоль,
    подсветку ходов, угроз и навигацию по меню.
    """

    def __init__(self) -> None:
        """Инициализирует эмулятор и начальное состояние UI."""
        self.engine = ChessEngine()
        self.current_state: str = "main_menu"
        self.selected_square: Optional[Tuple[int, int]] = None
        self.show_threats: bool = False

    def run(self) -> None:
        """Главный цикл приложения."""
        self.print_header()
        while True:
            try:
                if self.current_state == "main_menu":
                    self.show_main_menu()
                elif self.current_state == "play_match":
                    self.play_match()
                else:
                    self.current_state = "main_menu"
            except KeyboardInterrupt:
                print(f"\n\n{RED_COLOR}🔚 Выход из программы...{RESET_COLOR}")
                break
            except Exception as e:
                print(f"\n{RED_COLOR}❌ Ошибка: {e}{RESET_COLOR}")
                self.current_state = "main_menu"

    def print_header(self) -> None:
        """Выводит заголовок программы в консоль."""
        separator = f"{CYAN_COLOR}{'=' * 50}{RESET_COLOR}"
        print(separator)
        print(f"{YELLOW_COLOR}♟️   ПРОДВИНУТЫЙ ЭМУЛЯТОР ШАХМАТ (MAX COMPLEXITY)  ♙{RESET_COLOR}")
        print(separator)

    def show_main_menu(self) -> None:
        """Отрисовывает главное меню и обрабатывает выбор пользователя."""
        print(f"\n{CYAN_COLOR}=== ГЛАВНОЕ МЕНЮ ==={RESET_COLOR}")
        status = (
            "Продолжить"
            if self.engine.move_count > 0 and not self.engine.game_over
            else "Начать"
        )

        print(f"1 - 🎮 {status} классическую партию")
        print("2 - 🌟 Начать СКАЗОЧНЫЕ ШАХМАТЫ (3 новые фигуры)")
        print("0 - 👋 Выход")

        choice = input(f"\n{YELLOW_COLOR}Выберите опцию: {RESET_COLOR}").strip()

        if choice == "1":
            if self.engine.game_over or self.engine.mode != "standard":
                self.engine = ChessEngine("standard")
            self.current_state = "play_match"
        elif choice == "2":
            self.engine = ChessEngine("fairy")
            self.current_state = "play_match"
        elif choice == "0":
            sys.exit()

    def print_board_styled(self) -> None:
        """Выводит шахматную доску с подсветкой доступных ходов и угроз."""
        legal_destinations: Set[Tuple[int, int]] = set()
        if self.selected_square:
            moves = self.engine.get_legal_moves(*self.selected_square)
            legal_destinations = set(moves)

        threatened_squares: Set[Tuple[int, int]] = set()
        if self.show_threats:
            opponent = "black" if self.engine.turn == "white" else "white"
            moves_with_sources = self.engine.get_all_possible_moves(opponent)
            threatened_squares = {end for _, end in moves_with_sources}

        print(f"\n{CYAN_COLOR}    a  b  c  d  e  f  g  h{RESET_COLOR}")

        for r in range(8):
            row_s = f"{CYAN_COLOR}{8 - r} {RESET_COLOR}"
            for c in range(8):
                piece = self.engine.board[r][c]

                is_selected = self.selected_square == (r, c)
                is_legal_dest = (r, c) in legal_destinations
                is_threatened = (
                    (r, c) in threatened_squares
                    and piece is not None
                    and piece.color == self.engine.turn
                )

                # Определение цвета фона клетки
                if is_selected:
                    bg = BG_MAGENTA
                elif is_legal_dest:
                    bg = BG_GREEN
                elif is_threatened:
                    bg = BG_RED
                else:
                    bg = BG_LIGHT if (r + c) % 2 == 0 else BG_DARK

                sym = piece.symbol() if piece else " "
                row_s += f"{bg} {sym} {RESET_COLOR}"

            row_s += f"{CYAN_COLOR} {8 - r}{RESET_COLOR}"
            print(row_s)

        print(f"{CYAN_COLOR}    a  b  c  d  e  f  g  h{RESET_COLOR}\n")

    def play_match(self) -> None:
        """Управляет циклом самой партии, обработкой ходов и команд."""
        if self.engine.game_over:
            winner_str = str(self.engine.winner).upper()
            print(f"\n{YELLOW_COLOR}🏆 МАТ! Победили {winner_str}!{RESET_COLOR}")
            input(f"{CYAN_COLOR}Нажмите Enter для выхода в меню...{RESET_COLOR}")
            self.current_state = "main_menu"
            return

        self.print_board_styled()

        turn_str = (
            f"{YELLOW_COLOR}БЕЛЫЕ{RESET_COLOR}"
            if self.engine.turn == "white"
            else f"{BLUE_COLOR}ЧЕРНЫЕ{RESET_COLOR}"
        )
        print(f"Ход: {turn_str} | Всего ходов: {self.engine.move_count}")
        print(
            f"{CYAN_COLOR}Команды: {RESET_COLOR}'e2' (выбрать), "
            f"'e2e4' (ход), 'undo', 'threats' (угрозы), '0' (в меню)"
        )

        cmd = input(f"{YELLOW_COLOR}Ваш выбор: {RESET_COLOR}").strip().lower()

        if cmd == "0":
            self.current_state = "main_menu"
            return

        if cmd == "undo":
            self.engine.undo_move()
            self.selected_square = None
            return

        if cmd == "threats":
            self.show_threats = not self.show_threats
            return

        # Интерактивный выбор фигуры
        if len(cmd) == 2:
            sq = parse_square(cmd)
            if sq:
                piece = self.engine.board[sq[0]][sq[1]]
                if piece and piece.color == self.engine.turn:
                    self.selected_square = sq
                else:
                    self.selected_square = None
                    print(f"{RED_COLOR}❌ Это не ваша фигура или клетка пуста!{RESET_COLOR}")
            return

        # Совершение хода
        start: Optional[Tuple[int, int]] = None
        end: Optional[Tuple[int, int]] = None

        if len(cmd) == 4:
            start, end = parse_square(cmd[:2]), parse_square(cmd[2:])
        elif len(cmd) == 2 and self.selected_square:
            start, end = self.selected_square, parse_square(cmd)

        if start and end:
            piece = self.engine.board[start[0]][start[1]]
            promote_to = "queen"

            # Проверка на превращение пешки
            if piece and piece.type == "pawn" and (end[0] == 0 or end[0] == 7):
                if end in self.engine.get_legal_moves(*start):
                    print(
                        f"{MAGENTA_COLOR}🌟 Пешка достигла края! "
                        f"В кого превратить? (queen, rook, bishop, knight){RESET_COLOR}"
                    )
                    choice = input("Выбор: ").strip().lower()
                    if choice in ["queen", "rook", "bishop", "knight"]:
                        promote_to = choice

            if self.engine.make_move(start, end, promote_to):
                self.selected_square = None
            else:
                print(f"\n{RED_COLOR}❌ Недопустимый ход!{RESET_COLOR}")
        else:
            print(
                f"\n{RED_COLOR}❌ Неправильный формат! Введите откуда и куда "
                f"(например: e2e4) или кликните e2{RESET_COLOR}"
            )


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    app = AdvancedChessEmulator()
    app.run()