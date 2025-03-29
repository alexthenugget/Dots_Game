from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from leaderboard import (
    _DEFAULT_NAME,
    _DEFAULT_SCORE,
    _LEADERBOARD_SIZE,
    LeaderboardEntry,
    load_leaderboard,
    save_leaderboard,
    update_leaderboard,
)
import pytest


@pytest.fixture
def temp_leaderboard_file(tmp_path: Path) -> Path:
    """Фикстура: создает временный файл для хранения таблицы лидеров."""
    return tmp_path / "leaderboard.json"


@pytest.fixture
def sample_leaderboard() -> list[LeaderboardEntry]:
    """Фикстура: возвращает тестовые данные таблицы лидеров с 3 записями."""
    return [
        LeaderboardEntry(place=1, name="Alice", score=100),
        LeaderboardEntry(place=2, name="Bob", score=80),
        LeaderboardEntry(place=3, name="Charlie", score=50),
    ]


@patch("leaderboard.Path")
def test_load_leaderboard_no_file(mock_path: MagicMock, temp_leaderboard_file: Path) -> None:
    """
    Загрузка таблицы лидеров при отсутствии файла.
    Проверяет, что создается таблица с записями по умолчанию.
    """
    mock_path.return_value = temp_leaderboard_file

    result = load_leaderboard()

    assert len(result) == _LEADERBOARD_SIZE
    for i, entry in enumerate(result, 1):
        assert entry.place == i
        assert entry.name == _DEFAULT_NAME
        assert entry.score == _DEFAULT_SCORE


@patch("leaderboard.Path")
def test_load_leaderboard_existing_file(
    mock_path: MagicMock, temp_leaderboard_file: Path, sample_leaderboard: list[LeaderboardEntry]
) -> None:
    """
    Загрузка таблицы лидеров из существующего файла.
    Проверяет корректность чтения и формат данных.
    """
    mock_path.return_value = temp_leaderboard_file

    with open(temp_leaderboard_file, "w", encoding="utf-8") as f:
        json.dump([entry.model_dump() for entry in sample_leaderboard], f)

    result = load_leaderboard()

    assert len(result) == _LEADERBOARD_SIZE
    assert result[0].name == "Alice"
    assert result[1].score == 80
    assert result[2].place == 3


@patch("leaderboard.Path")
def test_save_leaderboard(
    mock_path: MagicMock, temp_leaderboard_file: Path, sample_leaderboard: list[LeaderboardEntry]
) -> None:
    """
    Сохранение таблицы лидеров в файл.
    Проверяет создание файла и корректность сохраненных данных.
    """
    mock_path.return_value = temp_leaderboard_file

    save_leaderboard(sample_leaderboard)

    assert temp_leaderboard_file.exists()
    with open(temp_leaderboard_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert len(data) == _LEADERBOARD_SIZE
        assert data[0]["name"] == "Alice"
        assert data[1]["score"] == 80


@patch("leaderboard.Path")
def test_update_leaderboard_new_high_score(
    mock_path: MagicMock, temp_leaderboard_file: Path, sample_leaderboard: list[LeaderboardEntry]
) -> None:
    """
    Обновление таблицы при попадании нового результата в топ.
    Проверяет корректность обновления и сортировки записей.
    """
    mock_path.return_value = temp_leaderboard_file

    with open(temp_leaderboard_file, "w", encoding="utf-8") as f:
        json.dump([entry.model_dump() for entry in sample_leaderboard], f)

    updated = update_leaderboard("Dave", 90)

    assert updated is True
    leaderboard = load_leaderboard()
    assert leaderboard[0].name == "Alice"
    assert leaderboard[1].name == "Dave"
    assert leaderboard[1].score == 90
    assert leaderboard[2].name == "Bob"


@patch("leaderboard.Path")
def test_update_leaderboard_low_score(
    mock_path: MagicMock, temp_leaderboard_file: Path, sample_leaderboard: list[LeaderboardEntry]
) -> None:
    """
    Попытка обновления с результатом ниже минимального в таблице.
    Проверяет, что таблица не изменяется при низком результате.
    """
    mock_path.return_value = temp_leaderboard_file

    with open(temp_leaderboard_file, "w", encoding="utf-8") as f:
        json.dump([entry.model_dump() for entry in sample_leaderboard], f)

    updated = update_leaderboard("Eve", 40)

    assert updated is False
    leaderboard = load_leaderboard()
    assert leaderboard[0].name == "Alice"
    assert leaderboard[1].name == "Bob"
    assert leaderboard[2].name == "Charlie"


@patch("leaderboard.Path")
def test_update_leaderboard_empty_slot(mock_path: MagicMock, temp_leaderboard_file: Path) -> None:
    """
    Обновление пустой таблицы (все записи по умолчанию).
    Проверяет добавление первой записи в таблицу.
    """
    mock_path.return_value = temp_leaderboard_file

    initial_leaderboard = [
        LeaderboardEntry(place=i + 1, name=_DEFAULT_NAME, score=_DEFAULT_SCORE) for i in range(_LEADERBOARD_SIZE)
    ]
    save_leaderboard(initial_leaderboard)

    updated = update_leaderboard("FirstPlayer", 10)

    assert updated is True
    leaderboard = load_leaderboard()
    assert leaderboard[0].name == "FirstPlayer"
    assert leaderboard[0].score == 10
    assert leaderboard[1].name == _DEFAULT_NAME
    assert leaderboard[2].name == _DEFAULT_NAME


@patch("leaderboard.Path")
def test_leaderboard_size_maintained(mock_path: MagicMock, temp_leaderboard_file: Path) -> None:
    """
    Проверка сохранения размера таблицы при множественных обновлениях.
    Проверяет, что таблица никогда не превышает заданный размер.
    """
    mock_path.return_value = temp_leaderboard_file

    for i in range(_LEADERBOARD_SIZE * 2):
        update_leaderboard(f"Player{i}", i * 10)
    leaderboard = load_leaderboard()
    assert len(leaderboard) == _LEADERBOARD_SIZE
    assert leaderboard[0].score == (_LEADERBOARD_SIZE * 2 - 1) * 10
    assert leaderboard[-1].score >= (_LEADERBOARD_SIZE - 1) * 10
