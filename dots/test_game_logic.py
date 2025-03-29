from unittest.mock import MagicMock

from dots_game import GameLogic
import pytest


@pytest.fixture
def game_logic() -> GameLogic:
    """Фикстура для создания экземпляра GameLogic с моком UI"""
    ui_mock = MagicMock()
    return GameLogic(width=5, height=5, game_ui=ui_mock)


def test_initialization(game_logic: GameLogic) -> None:
    """Тест инициализации GameLogic"""
    assert game_logic._grid_width == 5
    assert game_logic._grid_height == 5
    assert game_logic.current_player == GameLogic.PLAYER_1
    assert game_logic.scores == {1: 0, 2: 0}
    assert len(game_logic._grid) == 6
    assert len(game_logic._grid[0]) == 6


def test_is_board_full(game_logic: GameLogic) -> None:
    """Тест проверки заполненности поля"""
    assert not game_logic._is_board_full()

    for y in range(6):
        for x in range(6):
            game_logic._grid[y][x] = GameLogic.PLAYER_1
    game_logic._filled_cells = 36

    assert game_logic._is_board_full()


def test_is_valid_move(game_logic: GameLogic) -> None:
    """Тест проверки валидности хода"""
    assert game_logic.is_valid_move(0, 0)
    assert game_logic.is_valid_move(5, 5)

    assert not game_logic.is_valid_move(-1, 0)
    assert not game_logic.is_valid_move(6, 5)

    game_logic._grid[2][3] = GameLogic.PLAYER_1
    assert not game_logic.is_valid_move(3, 2)


def test_place_dot_invalid_move(game_logic: GameLogic) -> None:
    """Тест размещения точки с невалидным ходом"""
    result = game_logic.place_dot(-1, 0)
    assert not result
    assert game_logic._filled_cells == 0


def test_place_dot_valid_move(game_logic: GameLogic) -> None:
    """Тест размещения точки с валидным ходом"""
    result = game_logic.place_dot(2, 3)
    assert result is False
    assert game_logic._grid[3][2] == GameLogic.PLAYER_1
    assert game_logic._filled_cells == 1


def test_place_dot_board_full(game_logic: GameLogic) -> None:
    """Тест заполнения всего поля"""
    for y in range(6):
        for x in range(6):
            if x != 3 or y != 3:
                game_logic._grid[y][x] = GameLogic.PLAYER_1
                game_logic._filled_cells += 1

    result = game_logic.place_dot(3, 3)
    assert result is True
    assert game_logic._is_board_full()


def test_check_neighbors(game_logic: GameLogic) -> None:
    """Тест проверки соседей и создания линий"""
    game_logic._grid[2][2] = GameLogic.PLAYER_1
    game_logic._check_neighbors(3, 3)

    assert len(game_logic.lines) == 1
    line = game_logic.lines[0]
    assert line[4] == game_logic.player_colors[GameLogic.PLAYER_1]


def test_check_captures_no_capture(game_logic: GameLogic) -> None:
    """Тест проверки захвата без захвата"""
    game_logic._grid[2][3] = GameLogic.PLAYER_2
    captures = game_logic._check_captures(3, 3)
    assert captures == 0


def test_get_group_with_status(game_logic: GameLogic) -> None:
    """Тест получения группы и статуса окружения"""
    game_logic._grid[1][1] = GameLogic.PLAYER_1
    game_logic._grid[1][2] = GameLogic.PLAYER_1

    group, surrounded = game_logic._get_group_with_status(1, 1, GameLogic.PLAYER_1)
    assert len(group) >= 2
    assert not surrounded


def test_switch_player(game_logic: GameLogic) -> None:
    """Тест смены игрока"""
    assert game_logic.current_player == GameLogic.PLAYER_1
    game_logic.switch_player()
    assert game_logic.current_player == GameLogic.PLAYER_2
    game_logic.switch_player()
    assert game_logic.current_player == GameLogic.PLAYER_1


def test_make_ai_move_random_failure(game_logic: GameLogic) -> None:
    """Тест случайного хода ИИ (неудачный случай)"""
    for y in range(6):
        for x in range(6):
            game_logic._grid[y][x] = GameLogic.PLAYER_1

    move = game_logic.make_ai_move_random()
    assert move is None


def test_make_ai_move_smart_capture(game_logic: GameLogic) -> None:
    """Тест умного хода ИИ с захватом"""
    game_logic._grid[1][1] = GameLogic.PLAYER_1
    game_logic._grid[1][2] = GameLogic.PLAYER_1
    game_logic._grid[2][1] = GameLogic.PLAYER_1

    move = game_logic.make_ai_move_smart()
    assert move == (2, 2)


def test_make_ai_move_smart_no_capture(game_logic: GameLogic) -> None:
    """Тест умного хода ИИ без возможности захвата"""
    move = game_logic.make_ai_move_smart()
    assert move is not None


def test_would_capture_player_false(game_logic: GameLogic) -> None:
    """Тест проверки потенциального захвата (False)"""
    assert not game_logic._would_capture_player(0, 0)


def test_place_dot_with_self_capture(game_logic: GameLogic) -> None:
    """Тест размещения точки с самозахватом"""
    game_logic._grid[1][1] = GameLogic.PLAYER_1
    game_logic._grid[1][2] = GameLogic.PLAYER_1
    game_logic._grid[2][1] = GameLogic.PLAYER_2
    game_logic._grid[2][3] = GameLogic.PLAYER_2
    game_logic._grid[3][2] = GameLogic.PLAYER_2

    game_logic.place_dot(2, 2)

    assert game_logic.scores[GameLogic.PLAYER_2] == 0


def test_edge_case_max_board_size() -> None:
    """Тест большого размера поля"""
    ui_mock = MagicMock()
    game = GameLogic(width=30, height=30, game_ui=ui_mock)

    assert game.is_valid_move(30, 30)
    assert not game.is_valid_move(31, 30)


def test_controlled_areas_after_capture(game_logic: GameLogic) -> None:
    """Тест обновления контролируемых областей после захвата"""
    game_logic._grid[1][1] = GameLogic.PLAYER_2
    game_logic._grid[1][2] = GameLogic.PLAYER_2
    game_logic._grid[2][1] = GameLogic.PLAYER_1
    game_logic._grid[2][3] = GameLogic.PLAYER_1
    game_logic._grid[3][2] = GameLogic.PLAYER_1

    game_logic.place_dot(2, 2)

    assert game_logic.scores[GameLogic.PLAYER_1] >= 0


def test_ai_smart_move_prefers_capture(game_logic: GameLogic) -> None:
    """Тест, что умный ИИ предпочитает ходы с захватом"""
    game_logic.current_player = GameLogic.PLAYER_2
    game_logic._grid[1][1] = GameLogic.PLAYER_1
    game_logic._grid[1][2] = GameLogic.PLAYER_1
    game_logic._grid[2][1] = GameLogic.PLAYER_2
    game_logic._grid[2][3] = GameLogic.PLAYER_2
    game_logic._grid[3][2] = GameLogic.PLAYER_2

    game_logic._grid[4][4] = GameLogic.PLAYER_2
    game_logic._grid[4][5] = GameLogic.PLAYER_2

    move = game_logic.make_ai_move_smart()
    assert move == (2, 2)


def test_would_capture_player_true(game_logic: GameLogic) -> None:
    """Тест проверки потенциального захвата (True) - окончательная версия"""
    game_logic.current_player = GameLogic.PLAYER_2
    game_logic._grid[1][1] = GameLogic.PLAYER_1

    game_logic._grid[0][1] = GameLogic.PLAYER_2
    game_logic._grid[2][1] = GameLogic.PLAYER_2
    game_logic._grid[1][0] = GameLogic.PLAYER_2
    game_logic._grid[1][2] = GameLogic.PLAYER_2
    assert game_logic._would_capture_player(1, 2)
    assert game_logic._would_capture_player(0, 1)


def test_edge_cases_for_group_detection(game_logic: GameLogic) -> None:
    """Тест крайних случаев для обнаружения групп"""
    # Проверяем группы на краях поля
    game_logic._grid[0][0] = GameLogic.PLAYER_1
    game_logic._grid[0][1] = GameLogic.PLAYER_1
    game_logic._grid[1][0] = GameLogic.PLAYER_1

    group, surrounded = game_logic._get_group_with_status(0, 0, GameLogic.PLAYER_1)
    assert (0, 0) in group
    assert (0, 1) in group
    assert (1, 0) in group
    assert not surrounded
    game_logic._grid[4][4] = GameLogic.PLAYER_2
    game_logic._grid[4][5] = GameLogic.PLAYER_2
    game_logic._grid[5][4] = GameLogic.PLAYER_2

    group, surrounded = game_logic._get_group_with_status(4, 4, GameLogic.PLAYER_2)
    assert (4, 4) in group
    assert (4, 5) in group
    assert (5, 4) in group
    assert not surrounded
