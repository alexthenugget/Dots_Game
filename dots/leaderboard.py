from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel


_LEADERBOARD_SIZE = 3
_DEFAULT_NAME = "None"
_DEFAULT_SCORE = 0


class LeaderboardEntry(BaseModel):
    """
    Модель записи в таблице лидеров.
    """

    place: int
    name: str
    score: int


def load_leaderboard() -> list[LeaderboardEntry]:
    """
    Загружает таблицу лидеров из файла JSON.
    """
    _leaderboard_file = Path("leaderboard.json")

    if not _leaderboard_file.exists():
        return [
            LeaderboardEntry(place=i + 1, name=_DEFAULT_NAME, score=_DEFAULT_SCORE) for i in range(_LEADERBOARD_SIZE)
        ]

    with _leaderboard_file.open("r", encoding="utf-8") as _f:
        _data = json.load(_f)
        return [LeaderboardEntry(**entry) for entry in _data]


def save_leaderboard(leaderboard: list[LeaderboardEntry]) -> None:
    """
    Сохраняет таблицу лидеров в файл JSON.
    """
    _leaderboard_file = Path("leaderboard.json")
    with _leaderboard_file.open("w", encoding="utf-8") as _f:
        json.dump([entry.model_dump() for entry in leaderboard], _f, indent=4, ensure_ascii=False)


def update_leaderboard(new_name: str, new_score: int) -> bool:
    """
    Обновляет таблицу лидеров новым результатом.
    """
    _leaderboard = load_leaderboard()

    if new_score <= _leaderboard[-1].score and _leaderboard[-1].name != _DEFAULT_NAME:
        return False

    _leaderboard.append(LeaderboardEntry(place=0, name=new_name, score=new_score))
    _leaderboard.sort(key=lambda x: x.score if x.name != _DEFAULT_NAME else -1, reverse=True)
    _leaderboard = _leaderboard[:_LEADERBOARD_SIZE]

    for i, entry in enumerate(_leaderboard, 1):
        entry.place = i

    save_leaderboard(_leaderboard)
    return True
