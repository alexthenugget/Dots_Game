from __future__ import annotations

from tkinter import Canvas, Tk
from unittest.mock import MagicMock, patch

from constants import CELL_SIZE, OFFSET_X, OFFSET_Y
from dots_game import DotsGame, GameResult, determine_result
from game_logic import GameLogic
import pytest


@pytest.fixture
def root() -> Tk:
    """Фикстура: создает корневое окно Tkinter для тестирования."""
    return Tk()


@pytest.fixture
def game(root: Tk) -> DotsGame:
    """Фикстура: создает экземпляр игры DotsGame для тестирования."""
    return DotsGame(root)


@pytest.fixture
def mock_game_logic() -> MagicMock:
    """Фикстура: создает mock-объект для имитации GameLogic."""
    return MagicMock(spec=GameLogic)


def test_game_result_blue_win() -> None:
    """Тест проверяет корректность значений для результата 'победа синего игрока'."""
    result = GameResult.BLUE_WIN
    assert result.winner_text == "Синий игрок"
    assert result.color == "darkblue"


def test_game_result_red_win() -> None:
    """Тест проверяет корректность значений для результата 'победа красного игрока'."""
    result = GameResult.RED_WIN
    assert result.winner_text == "Красный игрок"
    assert result.color == "darkred"


def test_game_result_draw() -> None:
    """Тест проверяет корректность значений для результата 'ничья'."""
    result = GameResult.DRAW
    assert result.winner_text == "Ничья"
    assert result.color == "black"


def test_determine_result_blue_win() -> None:
    """Тест проверяет функцию определения результата при победе синего игрока."""
    assert determine_result(5, 3) == GameResult.BLUE_WIN


def test_determine_result_red_win() -> None:
    """Тест проверяет функцию определения результата при победе красного игрока."""
    assert determine_result(3, 5) == GameResult.RED_WIN


def test_determine_result_draw() -> None:
    """Тест проверяет функцию определения результата при ничьей."""
    assert determine_result(4, 4) == GameResult.DRAW


def test_game_initialization(game: DotsGame) -> None:
    """Тест проверяет корректность инициализации игры (значения по умолчанию)."""
    assert game._grid_width == 30
    assert game._grid_height == 33
    assert game._mode == "PVP"
    assert game._game_logic is None


def test_start_game(game: DotsGame) -> None:
    """Тест проверяет корректность запуска игры (создание canvas и привязка событий)."""
    game.start()
    assert isinstance(game._canvas, Canvas)
    assert game._canvas.bind("<Configure>") is not None
    assert game._canvas.bind("<Button-1>") is not None


@patch('dots_game.GameLogic')
def test_start_new_game_pvp(mock_game_logic: MagicMock, game: DotsGame) -> None:
    """Тест проверяет создание новой игры в режиме PVP."""
    game._start_new_game(10, 10, "PVP")
    assert game._grid_width == 10
    assert game._grid_height == 10
    assert game._mode == "PVP"
    mock_game_logic.assert_called_once_with(10, 10, game)


@patch('dots_game.GameLogic')
def test_start_new_game_pvair(mock_game_logic: MagicMock, game: DotsGame) -> None:
    """Тест проверяет создание новой игры в режиме PVAIR (против ИИ)."""
    game._start_new_game(15, 15, "PVAIR")
    assert game._mode == "PVAIR"
    mock_game_logic.assert_called_once_with(15, 15, game)


def test_create_grid(game: DotsGame) -> None:
    """Тест проверяет корректность создания сетки на canvas."""
    game._grid_width = 5
    game._grid_height = 5
    game._create_grid()
    canvas_items = game._canvas.find_all()
    assert len(canvas_items) == (5 + 1) * 2


def test_draw_dot(game: DotsGame) -> None:
    """Тест проверяет корректность отрисовки точки на canvas."""
    game._draw_dot(50, 50, "red")
    canvas_items = game._canvas.find_all()
    assert len(canvas_items) == 1
    assert game._canvas.itemcget(canvas_items[0], "fill") == "red"


def test_draw_lines(game: DotsGame, mock_game_logic: MagicMock) -> None:
    """Тест проверяет корректность отрисовки линий на canvas."""
    game._game_logic = mock_game_logic
    mock_game_logic.lines = [(10, 10, 20, 20, "blue")]
    game._draw_lines()
    canvas_items = game._canvas.find_withtag("lines")
    assert len(canvas_items) == 1


def test_update_scoreboard(game: DotsGame, mock_game_logic: MagicMock) -> None:
    """Тест проверяет корректность обновления отображения счета."""
    game._game_logic = mock_game_logic
    mock_game_logic.scores = {1: 5, 2: 3}
    game._scoreboard = MagicMock()

    game.update_scoreboard()
    assert game._scoreboard is not None


def test_show_capture_message(game: DotsGame) -> None:
    """Тест проверяет, что сообщение о захвате отображается на заданное время."""
    with patch.object(game._root, 'after') as mock_after:
        game._show_capture_message(1, 3)
        args, kwargs = mock_after.call_args
        assert args[0] == 2000
        assert callable(args[1])


@patch('dots_game.GameLogic')
def test_on_canvas_click_with_game_logic(mock_game_logic: MagicMock, game: DotsGame) -> None:
    """Test canvas click handling with game logic."""
    # Create a proper mock for game logic
    mock_logic = MagicMock()
    mock_logic.place_dot.return_value = False
    mock_logic.current_player = 1
    mock_logic.player_colors = {1: "blue"}
    mock_logic.last_captured = 0
    mock_logic.scores = {1: 0, 2: 0}
    mock_logic.lines = []

    game._game_logic = mock_logic
    game._canvas = MagicMock()
    game._canvas.find_all.return_value = [1]

    event = MagicMock()
    event.x = OFFSET_X + CELL_SIZE
    event.y = OFFSET_Y + CELL_SIZE

    game._on_canvas_click(event)

    game._canvas.create_oval.assert_called_once()


@patch('dots_game.GameLogic')
def test_on_canvas_click_game_ended(mock_game_logic: MagicMock, game: DotsGame) -> None:
    """Test canvas click handling when game ends."""
    # Create a proper mock for game logic
    mock_logic = MagicMock()
    mock_logic.place_dot.return_value = True
    mock_logic.current_player = 1
    mock_logic.player_colors = {1: "blue"}
    mock_logic.last_captured = 1
    mock_logic.scores = {1: 0, 2: 0}
    mock_logic.lines = []
    mock_logic.is_game_over = True

    game._game_logic = mock_logic
    game._canvas = MagicMock()

    with patch.object(game, '_end_game') as mock_end_game:
        event = MagicMock()
        event.x = OFFSET_X + CELL_SIZE
        event.y = OFFSET_Y + CELL_SIZE
        game._on_canvas_click(event)
        mock_end_game.assert_called_once()


def test_on_canvas_click_no_game_logic(game: DotsGame) -> None:
    """Тест проверяет обработку клика по canvas при отсутствии игровой логики."""
    event = MagicMock()
    event.x = 100
    event.y = 100
    game._on_canvas_click(event)
    assert game._game_logic is None


def test_make_ai_move_random(game: DotsGame, mock_game_logic: MagicMock) -> None:
    """
    Тест проверяет, что в режиме "PVAIR" вызывается метод make_ai_move_random
    объекта GameLogic.
    """
    game._mode = "PVAIR"
    game._game_logic = mock_game_logic
    mock_game_logic.make_ai_move_random.return_value = (5, 5)
    mock_game_logic.player_colors = {1: "blue", 2: "red"}
    mock_game_logic.lines = []
    mock_game_logic.last_captured = 0
    mock_game_logic.scores = {1: 0, 2: 0}
    game._make_ai_move()
    mock_game_logic.make_ai_move_random.assert_called_once()


def test_make_ai_move_smart(game: DotsGame, mock_game_logic: MagicMock) -> None:
    """
    Тест проверяет, что в режиме "PVAIS" вызывается метод make_ai_move_smart
    объекта GameLogic.
    """
    game._mode = "PVAIS"
    game._game_logic = mock_game_logic
    mock_game_logic.make_ai_move_smart.return_value = (5, 5)
    game._game_logic.player_colors = {1: "blue", 2: "red"}
    game._game_logic.lines = []
    game._game_logic.last_captured = 0
    mock_game_logic.scores = {1: 0, 2: 0}
    game._make_ai_move()
    mock_game_logic.make_ai_move_smart.assert_called_once()


def test_end_game_no_logic(game: DotsGame) -> None:
    """Тест проверяет, что при отсутствии игровой логики _game_logic становится None."""
    game._end_game()
    assert game._game_logic is None


@patch('dots_game.messagebox')
def test_end_game_with_logic(mock_messagebox: MagicMock, game: DotsGame, mock_game_logic: MagicMock) -> None:
    """
    Тест проверяет поведение _end_game при наличии игровой логики и завершенной игре.
    Ожидается вызов _show_winner_dialog и отсутствие вызова messagebox.
    """
    game._game_logic = mock_game_logic
    mock_game_logic.scores = {1: 5, 2: 3}
    mock_game_logic.is_game_over = True
    with patch.object(game, '_show_winner_dialog') as mock_show_winner:
        game._end_game()
        mock_show_winner.assert_called_once()
        mock_messagebox.assert_not_called()


def test_create_mode_buttons(game: DotsGame) -> None:
    """Тест проверяет создание кнопок выбора режима игры."""
    game._create_mode_buttons()
    assert len(game._root.winfo_children()) > 3


def test_create_size_selection(game: DotsGame) -> None:
    """Тест проверяет создание элементов выбора размера игрового поля."""
    game._create_size_selection()
    assert game._entry1 is not None
    assert game._entry2 is not None


@patch('dots_game.messagebox')
def test_update_grid_size_invalid(mock_messagebox: MagicMock, game: DotsGame) -> None:
    """
    Тест проверяет обработку некорректного ввода размера игрового поля.
    Ожидается отображение сообщения об ошибке.
    """
    game._entry1 = MagicMock()
    game._entry1.get.return_value = "abc"
    game._entry2 = MagicMock()
    game._entry2.get.return_value = "10"

    game._update_grid_size()
    mock_messagebox.showerror.assert_called_once()


@patch('dots_game.messagebox')
def test_update_grid_size_too_large(mock_messagebox: MagicMock, game: DotsGame) -> None:
    """
    Тест проверяет обработку ввода слишком большого размера игрового поля.
    Ожидается отображение сообщения об ошибке.
    """
    game._entry1 = MagicMock()
    game._entry1.get.return_value = "40"
    game._entry2 = MagicMock()
    game._entry2.get.return_value = "40"

    game._update_grid_size()
    mock_messagebox.showerror.assert_called_once()


def test_show_winner_dialog(game: DotsGame) -> None:
    """Тест проверяет создание и вызов диалогового окна с сообщением о победителе."""
    with patch('dots_game.Toplevel') as mock_toplevel:
        game._show_winner_dialog(GameResult.BLUE_WIN, 5, "Test message")
        mock_toplevel.assert_called_once()


def test_create_end_game_button(game: DotsGame) -> None:
    """Тест проверяет создание кнопки завершения игры с корректным текстом."""
    game._create_end_game_button()
    assert game._end_button is not None
    assert "Завершить игру" in game._end_button.cget("text")


def test_bind_events(game: DotsGame) -> None:
    """Тест проверяет привязку событий к canvas (изменение размера и клик)."""
    game._bind_events()
    assert game._canvas.bind("<Configure>") is not None
    assert game._canvas.bind("<Button-1>") is not None


def test_init_interface_elements(game: DotsGame) -> None:
    """Тест проверяет инициализацию основных элементов интерфейса (таблица лидеров, счет)."""
    game._init_interface_elements()
    assert game._leaderboard_tree is not None
    assert game._scoreboard is not None


@patch('dots_game.load_leaderboard')
def test_init_leaderboard_data(mock_load: MagicMock, game: DotsGame) -> None:
    """Тест проверяет загрузку данных для таблицы лидеров при инициализации."""
    mock_load.return_value = [MagicMock(place=1, name="Test", score=10)]
    game._init_leaderboard_data()
    assert game._leaderboard is not None
    mock_load.assert_called_once()


def test_update_leaderboard_display(game: DotsGame) -> None:
    """Тест проверяет обновление отображения таблицы лидеров."""
    game._leaderboard_tree = MagicMock()
    game._leaderboard = [MagicMock(place=1, name="Test", score=10)]
    game._update_leaderboard_display()
    game._leaderboard_tree.insert.assert_called_once()


def test_update_grid_size_valid(game: DotsGame) -> None:
    """
    Тест проверяет обновление размеров игрового поля при корректном вводе
    и запуск новой игры с заданными размерами.
    """
    game._entry1 = MagicMock()
    game._entry1.get.return_value = "10"
    game._entry2 = MagicMock()
    game._entry2.get.return_value = "12"

    with patch.object(game, '_start_new_game') as mock_start_new:
        game._update_grid_size()

        mock_start_new.assert_called_once_with(10, 12, game._mode)
        assert game._grid_width == 10
        assert game._grid_height == 12
