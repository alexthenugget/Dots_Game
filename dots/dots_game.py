from __future__ import annotations

from enum import Enum
from tkinter import BOTH, Button, Canvas, Entry, Label, Tk, Toplevel, font, messagebox
from tkinter.ttk import Treeview
from typing import Any, Callable, List, Optional

from constants import BLUE_TEAM, CELL_SIZE, OFFSET_X, OFFSET_Y, RED_TEAM
from game_logic import GameLogic
from interface import create_leaderboard, create_rules, create_scoreboard
from leaderboard import load_leaderboard, update_leaderboard


class GameResult(Enum):
    """
    Перечисление возможных результатов игры.
    """

    BLUE_WIN = 1
    RED_WIN = 2
    DRAW = 3

    @property
    def winner_text(self) -> str:
        texts = {GameResult.BLUE_WIN: "Синий игрок", GameResult.RED_WIN: "Красный игрок", GameResult.DRAW: "Ничья"}
        return texts[self]

    @property
    def color(self) -> str:
        colors = {GameResult.BLUE_WIN: "darkblue", GameResult.RED_WIN: "darkred", GameResult.DRAW: "black"}
        return colors[self]


def determine_result(blue_score: int, red_score: int) -> GameResult:
    """
    Определяет результат игры на основе количества очков игроков.
    """
    if blue_score > red_score:
        return GameResult.BLUE_WIN
    if red_score > blue_score:
        return GameResult.RED_WIN
    return GameResult.DRAW


class DotsGame:
    def __init__(self, root: Tk) -> None:
        """
        Инициализирует игру.
        """
        self._root: Tk = root
        self._canvas: Canvas = Canvas(root, bg="white")
        self._canvas.pack(fill=BOTH, expand=True)

        self._grid_width: int = 30
        self._grid_height: int = 33
        self._mode: str = "PVP"
        self._game_logic: Optional[GameLogic] = None
        self._leaderboard: Optional[List[Any]] = None
        self._leaderboard_tree: Optional[Treeview] = None
        self._scoreboard: Optional[Treeview] = None
        self._end_button: Optional[Button] = None
        self._entry1: Optional[Entry] = None
        self._entry2: Optional[Entry] = None

    def start(self) -> None:
        """
        Запускает игру, инициализируя пользовательский интерфейс и игровое поле.
        """
        self._setup_ui()
        self._create_grid()

    def _setup_ui(self) -> None:
        """
        Настраивает пользовательский интерфейс.
        """
        self._bind_events()
        self._init_interface_elements()
        self._init_leaderboard_data()

    def _bind_events(self) -> None:
        """
        Привязывает обработчики событий к элементам интерфейса.
        """
        self._canvas.bind("<Configure>", lambda e: self._create_grid())
        self._canvas.bind("<Button-1>", self._on_canvas_click)

    def _init_interface_elements(self) -> None:
        """
        Инициализирует все элементы интерфейса.
        """
        self._leaderboard_tree = create_leaderboard(self._root)
        self._scoreboard = create_scoreboard(self._root)
        create_rules(self._root)
        self._create_mode_buttons()
        self._create_size_selection()
        self._create_end_game_button()

    def _init_leaderboard_data(self) -> None:
        """
        Загружает данные таблицы лидеров.
        """
        self._leaderboard = load_leaderboard()
        self._update_leaderboard_display()

    def _update_leaderboard_display(self) -> None:
        """
        Обновляет отображение таблицы лидеров.
        """
        if self._leaderboard_tree is None or self._leaderboard is None:
            return

        for row in self._leaderboard_tree.get_children():
            self._leaderboard_tree.delete(row)
        for entry in self._leaderboard:
            self._leaderboard_tree.insert("", "end", values=(entry.place, entry.name, entry.score))

    def _create_end_game_button(self) -> None:
        """
        Создает кнопку для досрочного завершения игры.
        """
        self._end_button = Button(
            self._root,
            text="Завершить игру",
            command=self._end_game,
            fg="white",
            bg="red",
            font=("Arial", 11, "bold"),
            width=17,
            height=1,
        )
        self._end_button.place(x=700, y=60)

    def _end_game(self) -> None:
        """
        Завершает текущую игру.
        """
        if self._game_logic is None:
            return

        scores = self._game_logic.scores
        blue_score = scores[BLUE_TEAM]
        red_score = scores[RED_TEAM]

        result = determine_result(blue_score, red_score)
        board_full = hasattr(self._game_logic, "is_board_full") and self._game_logic.is_board_full()

        message = (
            f"{'Доска заполнена' if board_full else 'Игра завершена досрочно'}! " f"Игра окончена! {result.winner_text}"
        )
        winning_score_mapping = {
            GameResult.BLUE_WIN: blue_score,
            GameResult.RED_WIN: red_score,
            GameResult.DRAW: max(blue_score, red_score),
        }
        winning_score = winning_score_mapping[result]

        if result != GameResult.DRAW:
            self._show_winner_dialog(result, winning_score, message)
        else:
            self._show_game_over_message(message, result.color)

    def _show_winner_dialog(self, result: GameResult, winning_score: int, message: str) -> None:
        """
        Показывает диалог победителя.
        """
        name_window = Toplevel(master=self._root)
        name_window.title("Поздравляем!")
        name_window.geometry("400x200")
        name_window.resizable(width=False, height=False)

        Label(
            master=name_window,
            text=f"Вы набрали {winning_score} очков!\nВведите ваше имя:",
            font=("Arial", 12),
            wraplength=380,
        ).pack(pady=10)

        name_entry = Entry(master=name_window, font=("Arial", 12), width=30)
        name_entry.pack(pady=5)

        def save_and_close() -> None:
            player_name = name_entry.get().strip()
            if player_name:
                updated = update_leaderboard(player_name, winning_score)
                if updated:
                    self._leaderboard = load_leaderboard()
                    self._update_leaderboard_display()
                    messagebox.showinfo("Успех", "Вы попали в таблицу лидеров!")
                else:
                    messagebox.showinfo("Сожалеем", "Ваш результат не попал в топ-3.")
                name_window.destroy()
                self._show_game_over_message(message, result.color)
            else:
                messagebox.showerror("Ошибка", "Пожалуйста, введите имя!")

        Button(name_window, text="Сохранить", command=save_and_close, font=("Arial", 12)).pack(pady=10)

    def _show_game_over_message(self, message: str, color: str) -> None:
        """
        Показывает окно с результатом игры.
        """
        game_over_window = Toplevel(self._root)
        game_over_window.title("Игра окончена")
        game_over_window.geometry("400x150")
        game_over_window.resizable(False, False)

        Label(
            game_over_window,
            text=message,
            font=("Arial", 14, "bold"),
            fg="white",
            bg=color,
            wraplength=380,
        ).pack(expand=True, fill=BOTH)

        Button(
            game_over_window,
            text="OK",
            command=game_over_window.destroy,
            font=("Arial", 12),
        ).pack(pady=10)

        self._game_logic = None

    def _create_grid(self) -> None:
        """
        Отрисовывает игровое поле.
        """
        self._canvas.delete("grid_line")

        start_x = OFFSET_X
        start_y = OFFSET_Y
        end_x = self._grid_width * CELL_SIZE + OFFSET_X + 1
        end_y = self._grid_height * CELL_SIZE + OFFSET_Y + 1

        for coord in range(start_x, end_x, CELL_SIZE):
            self._canvas.create_line(coord, start_y, coord, end_y, tags="grid_line", fill="lightblue")
        for coord in range(start_y, end_y, CELL_SIZE):
            self._canvas.create_line(start_x, coord, end_x, coord, tags="grid_line", fill="lightblue")

    def _on_canvas_click(self, event: Any) -> None:
        """
        Обрабатывает клик по игровому полю.
        """
        if self._game_logic is None:
            return

        offset_x = (event.x - OFFSET_X) % CELL_SIZE
        offset_y = (event.y - OFFSET_Y) % CELL_SIZE

        grid_x = (event.x - OFFSET_X) // CELL_SIZE + (1 if offset_x >= CELL_SIZE / 2 else 0)
        grid_y = (event.y - OFFSET_Y) // CELL_SIZE + (1 if offset_y >= CELL_SIZE / 2 else 0)

        grid_x = max(0, min(grid_x, self._grid_width))
        grid_y = max(0, min(grid_y, self._grid_height))

        if 0 <= grid_x <= self._grid_width and 0 <= grid_y <= self._grid_height:
            current_player_before = self._game_logic.current_player
            if not self._game_logic.is_valid_move(grid_x, grid_y):
                return

            game_ended = self._game_logic.place_dot(grid_x, grid_y)

            x = grid_x * CELL_SIZE + OFFSET_X
            y = grid_y * CELL_SIZE + OFFSET_Y
            color = self._game_logic.player_colors[current_player_before]
            self._draw_dot(x, y, color)
            self._draw_lines()

            if self._game_logic.last_captured > 0:
                self._show_capture_message(current_player_before, self._game_logic.last_captured)

            self.update_scoreboard()

            if game_ended:
                self._end_game()
                return

            self._game_logic.switch_player()

            if self._mode != "PVP" and self._game_logic.current_player == 2:
                self._root.after(500, self._make_ai_move)

    def _make_ai_move(self) -> None:
        """
        Выполняет ход компьютера.
        """
        if self._game_logic is None:
            return
        if self._mode == "PVAIR":
            move = self._game_logic.make_ai_move_random()
        else:
            move = self._game_logic.make_ai_move_smart()

        if move:
            grid_x, grid_y = move
            game_ended = self._game_logic.place_dot(grid_x, grid_y)

            x = grid_x * CELL_SIZE + OFFSET_X
            y = grid_y * CELL_SIZE + OFFSET_Y
            color = self._game_logic.player_colors[2]
            self._draw_dot(x, y, color)
            self._draw_lines()

            if self._game_logic.last_captured > 0:
                self._show_capture_message(2, self._game_logic.last_captured)

            self.update_scoreboard()

            if game_ended:
                self._end_game()
                return

            self._game_logic.switch_player()

    def _draw_dot(self, x: int, y: int, color: str) -> None:
        """
        Рисует точку на поле.
        """
        self._canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline=color)

    def _draw_lines(self) -> None:
        """
        Рисует линии между точками.
        """
        self._canvas.delete("lines")

        if self._game_logic is not None:
            for line in self._game_logic.lines:
                x1, y1, x2, y2, color = line
                self._canvas.create_line([x1, y1, x2, y2], fill=color, width=2, tags="lines")

    def update_scoreboard(self) -> None:
        """
        Обновляет счет на экране.
        """
        if self._game_logic is None or self._scoreboard is None:
            return

        if hasattr(self._game_logic, 'scores'):
            for row in self._scoreboard.get_children():
                self._scoreboard.delete(row)

            self._scoreboard.insert(
                "",
                "end",
                values=(
                    f"Синий: {self._game_logic.scores.get(1, 0)}",
                    f"Красный: {self._game_logic.scores.get(2, 0)}",
                ),
                tags=("blue", "red"),
            )

            self._scoreboard.tag_configure("blue", foreground="darkblue")
            self._scoreboard.tag_configure("red", foreground="darkred")

    def _show_capture_message(self, player: int, count: int) -> None:
        """
        Показывает сообщение о захвате точек.
        """
        color = "синий" if player == 1 else "красный"
        message = f"Игрок {player} ({color}) захватил {count} точек!"

        msg_label = Label(
            self._root,
            text=message,
            font=("Arial", 12, "bold"),
            fg="white",
            bg="darkblue" if player == 1 else "darkred",
        )
        msg_label.place(relx=0.5, rely=0.95, anchor="center")

        self._root.after(2000, msg_label.destroy)

    def _start_new_game(self, width: int, height: int, mode: str) -> None:
        """
        Запускает новую игру.
        """
        self._grid_width = width
        self._grid_height = height
        self._mode = mode
        self._game_logic = GameLogic(width, height, self)
        self._game_logic.player_colors = {1: "darkblue", 2: "darkred"}

        if not hasattr(self._game_logic, 'scores'):
            self._game_logic.scores = {1: 0, 2: 0}

        self._canvas.delete("all")
        self._create_grid()
        self.update_scoreboard()

    def _create_mode_buttons(self) -> None:
        """
        Создает кнопки выбора режима.
        """
        header_label = Label(
            self._root,
            text="Выбор режима",
            font=("Arial", 12, "bold"),
            bg="white",
            highlightthickness=0,
        )
        header_label.place(relx=1.0, rely=0.0, x=-350, y=247, anchor="ne")

        buttons = [
            ("Игрок1 / Игрок2", 280, "PVP"),
            ("Игрок1 / Компьютер рандом", 340, "PVAIR"),
            ("Игрок1 / Компьютер умный", 400, "PVAIS"),
        ]

        for text, y_pos, mode in buttons:
            button = Button(
                self._root,
                text=text,
                command=self._create_mode_handler(mode),
                fg="black",
                bg="white",
                font=("Arial", 10),
                width=25,
                height=2,
            )
            button.place(x=680, y=y_pos)

    def _create_mode_handler(self, mode: str) -> Callable[[], None]:
        """
        Создает обработчик для кнопок режима.
        """
        return lambda: self._start_new_game(self._grid_width, self._grid_height, mode)

    def _create_size_selection(self) -> None:
        """
        Создает элементы выбора размера поля.
        """
        header_label = Label(
            self._root,
            text="Выбор размера поля",
            font=("Arial", 12, "bold"),
            bg="white",
            highlightthickness=0,
        )
        header_label.place(relx=1.0, rely=0.0, x=-70, y=250, anchor="ne")

        info_label = Label(
            self._root,
            text="Максимальные wxh (30x33) клеток",
            font=("Arial", 10),
            bg="white",
            highlightthickness=0,
        )
        info_label.place(relx=1.0, rely=0.0, x=-50, y=270, anchor="ne")

        custom_font = font.Font(size=14)
        self._entry1 = Entry(self._root, width=15, font=custom_font)
        self._entry1.place(relx=1.0, rely=0.0, x=-70, y=310, anchor="ne")

        self._entry2 = Entry(self._root, width=15, font=custom_font)
        self._entry2.place(relx=1.0, rely=0.0, x=-70, y=360, anchor="ne")

        button_select = Button(
            self._root,
            text="Выбрать",
            command=self._update_grid_size,
            fg="black",
            bg="white",
            font=("Arial", 10),
            width=23,
            height=1,
        )
        button_select.place(x=950, y=420)

    def _update_grid_size(self) -> None:
        """
        Обновляет размер поля.
        """
        if self._entry1 is None or self._entry2 is None:
            return

        try:
            new_width = int(self._entry1.get())
            new_height = int(self._entry2.get())

            if new_width > 30 or new_height > 33:
                messagebox.showerror("Ошибка", "Размеры не должны превышать 30x33")
                return

            self._grid_width = new_width
            self._grid_height = new_height
            self._start_new_game(new_width, new_height, self._mode)
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа")
