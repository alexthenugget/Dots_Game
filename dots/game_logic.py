from __future__ import annotations

from collections import deque
import random
from typing import Any

from constants import CELL_SIZE, OFFSET_X, OFFSET_Y


class GameLogic:
    """
    Класс для реализации логики игры, которая управляет игровым полем, движением
    игроков, захватами и состоянием игры.
    """

    PLAYER_1 = 1
    PLAYER_2 = 2
    EMPTY_CELL = 0

    FOUR_DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    EIGHT_DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    INITIAL_FILLED_CELLS = 0
    MAX_ATTEMPTS = 500

    def __init__(self, width: int, height: int, game_ui: Any) -> None:
        """Инициализация класса GameLogic."""
        self._grid_width: int = width
        self._grid_height: int = height
        self._game_ui: Any = game_ui
        self.scores: dict[int, int] = {
            self.PLAYER_1: self.INITIAL_FILLED_CELLS,
            self.PLAYER_2: self.INITIAL_FILLED_CELLS,
        }
        self.player_colors: dict[int, str] = {self.PLAYER_1: "darkblue", self.PLAYER_2: "darkred"}
        self._grid: list[list[int]] = [[self.EMPTY_CELL for _ in range(width + 1)] for _ in range(height + 1)]
        self.current_player: int = self.PLAYER_1
        self.lines: list[tuple[int, int, int, int, str]] = []
        self.last_captured: int = self.INITIAL_FILLED_CELLS
        self._total_cells: int = (width + 1) * (height + 1)
        self._filled_cells: int = self.INITIAL_FILLED_CELLS
        self._controlled_areas: dict[int, list[tuple[int, int]]] = {self.PLAYER_1: [], self.PLAYER_2: []}

    def _is_board_full(self) -> bool:
        """Проверяет, заполнено ли игровое поле."""
        return self._filled_cells >= self._total_cells

    def is_valid_move(self, grid_x: int, grid_y: int) -> bool:
        """Проверяет, является ли указанный ход допустимым."""
        if not (0 <= grid_x <= self._grid_width and 0 <= grid_y <= self._grid_height):
            return False
        return self._grid[grid_y][grid_x] == self.EMPTY_CELL

    def place_dot(self, grid_x: int, grid_y: int) -> bool:
        """Помещает точку игрока на поле."""
        if not self._validate_move(grid_x, grid_y):
            return False

        self._execute_move(grid_x, grid_y)

        if self._is_board_full():
            return True

        self._check_neighbors(grid_x, grid_y)
        self._handle_captures(grid_x, grid_y)
        self._check_self_capture(grid_x, grid_y)

        return self._is_board_full()

    def _validate_move(self, grid_x: int, grid_y: int) -> bool:
        """Validate if move is possible."""
        if not (0 <= grid_x <= self._grid_width and 0 <= grid_y <= self._grid_height):
            return False
        return self._grid[grid_y][grid_x] == self.EMPTY_CELL

    def _execute_move(self, grid_x: int, grid_y: int) -> None:
        """Execute the move on the grid."""
        self._grid[grid_y][grid_x] = self.current_player
        self._filled_cells += 1

    def _handle_captures(self, grid_x: int, grid_y: int) -> None:
        """Handle opponent captures after move."""
        captures = self._check_captures(grid_x, grid_y)
        if captures > self.INITIAL_FILLED_CELLS:
            self.scores[self.current_player] += captures
            self._game_ui.update_scoreboard()

    def _check_self_capture(self, grid_x: int, grid_y: int) -> None:
        """Check if move causes self-capture."""
        opponent = self.PLAYER_2 if self.current_player == self.PLAYER_1 else self.PLAYER_1
        for dx, dy in self.FOUR_DIRECTIONS:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx <= self._grid_width and 0 <= ny <= self._grid_height:
                if self._grid[ny][nx] == self.current_player:
                    group, is_surrounded = self._get_group_with_status(nx, ny, self.current_player)
                    if is_surrounded:
                        self_captures = sum(1 for gx, gy in group if self._grid[gy][gx] == self.current_player)
                        if self_captures > 0:
                            self.scores[opponent] += self_captures
                            self._game_ui.update_scoreboard()

    def _check_neighbors(self, grid_x: int, grid_y: int) -> None:
        """
        Проверяет соседей текущей клетки и добавляет линии между соседними
        клетками одного игрока.
        """
        color = self.player_colors[self.current_player]
        for dx, dy in self.EIGHT_DIRECTIONS:
            nx, ny = grid_x + dx, grid_y + dy
            if 0 <= nx <= self._grid_width and 0 <= ny <= self._grid_height:
                if self._grid[ny][nx] == self.current_player:
                    x1 = grid_x * CELL_SIZE + OFFSET_X
                    y1 = grid_y * CELL_SIZE + OFFSET_Y
                    x2 = nx * CELL_SIZE + OFFSET_X
                    y2 = ny * CELL_SIZE + OFFSET_Y
                    line = (x1, y1, x2, y2, color)
                    if line not in self.lines:
                        self.lines.append(line)

    def _check_captures(self, x: int, y: int) -> int:
        """
        Проверяет захват окруженных групп противника.
        Возвращает количество захваченных точек (без удаления их с поля).
        """
        opponent = self.PLAYER_2 if self.current_player == self.PLAYER_1 else self.PLAYER_1
        captured = 0
        for dx, dy in self.FOUR_DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx <= self._grid_width and 0 <= ny <= self._grid_height:
                if self._grid[ny][nx] == opponent:
                    group, is_surrounded = self._get_group_with_status(nx, ny, opponent)
                    if is_surrounded:
                        captured += sum(1 for gx, gy in group if self._grid[gy][gx] == opponent)

        self.last_captured = captured
        return captured

    def _get_group_with_status(self, x: int, y: int, player: int) -> tuple[list[tuple[int, int]], bool]:
        """
        Получает группу точек игрока и пустых клеток, начиная с координат (x, y),
        и определяет, окружена ли она точками противника или границей поля.
        """
        visited = [[False for _ in range(self._grid_width + 1)] for _ in range(self._grid_height + 1)]
        queue = deque([(x, y)])
        visited[y][x] = True
        group = []
        is_surrounded = True
        opponent = self.PLAYER_2 if player == self.PLAYER_1 else self.PLAYER_1

        while queue:
            cx, cy = queue.popleft()
            group.append((cx, cy))

            for dx, dy in self.FOUR_DIRECTIONS:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx <= self._grid_width and 0 <= ny <= self._grid_height:
                    if not visited[ny][nx]:
                        if self._grid[ny][nx] == player or self._grid[ny][nx] == self.EMPTY_CELL:
                            visited[ny][nx] = True
                            queue.append((nx, ny))
                else:
                    is_surrounded = False
        for cx, cy in group:
            for dx, dy in self.FOUR_DIRECTIONS:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx <= self._grid_width and 0 <= ny <= self._grid_height:
                    if (nx, ny) not in group and self._grid[ny][nx] != opponent:
                        is_surrounded = False
                        break
            if not is_surrounded:
                break

        return group, is_surrounded

    def switch_player(self) -> None:
        """Меняет текущего игрока."""
        self.current_player = self.PLAYER_2 if self.current_player == self.PLAYER_1 else self.PLAYER_1

    def make_ai_move_random(self) -> tuple[int, int] | None:
        """Выполняет случайный ход для ИИ."""
        attempts = 0
        while attempts < self.MAX_ATTEMPTS:
            grid_x = random.randint(0, self._grid_width)
            grid_y = random.randint(0, self._grid_height)
            if self.is_valid_move(grid_x, grid_y):
                if self.place_dot(grid_x, grid_y):
                    return None
                return grid_x, grid_y
            attempts += 1
        return None

    def make_ai_move_smart(self) -> tuple[int, int] | None:
        """Smart AI move: tries to capture player dots first, then plays strategically."""
        capture_move = self._find_capture_move()
        if capture_move:
            return self._execute_ai_move(capture_move[0], capture_move[1])

        strategic_move = self._find_strategic_move()
        if strategic_move:
            return self._execute_ai_move(strategic_move[0], strategic_move[1])

        return self.make_ai_move_random()

    def _find_capture_move(self) -> tuple[int, int] | None:
        """Find a move that would capture player dots."""
        for y in range(self._grid_height + 1):
            for x in range(self._grid_width + 1):
                if self.is_valid_move(x, y) and self._would_capture_player(x, y):
                    return x, y
        return None

    def _find_strategic_move(self) -> tuple[int, int] | None:
        """Find a strategic move near player dots."""
        player_dots = self._get_player_dots()
        if not player_dots:
            return None

        candidate_moves = self._get_candidate_moves(player_dots)
        if not candidate_moves:
            return None

        return self._select_best_move(candidate_moves)

    def _get_player_dots(self) -> list[tuple[int, int]]:
        """Get all player dots on the board."""
        dots = []
        for y in range(self._grid_height + 1):
            for x in range(self._grid_width + 1):
                if self._grid[y][x] == self.PLAYER_1:
                    dots.append((x, y))
        return dots

    def _get_candidate_moves(self, player_dots: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Get all valid moves near player dots."""
        candidates = []
        for x, y in player_dots:
            for dx, dy in self.EIGHT_DIRECTIONS:
                nx, ny = x + dx, y + dy
                if 0 <= nx <= self._grid_width and 0 <= ny <= self._grid_height:
                    if self.is_valid_move(nx, ny):
                        candidates.append((nx, ny))
        return candidates

    def _select_best_move(self, candidates: list[tuple[int, int]]) -> tuple[int, int]:
        """Select best move from candidates based on scoring. If no candidates, return a random move."""
        if not candidates:
            return self.make_ai_move_random() or (0, 0)

        best_move = candidates[0]
        best_score = -1

        for x, y in candidates:
            score = self._calculate_move_score(x, y)
            if score > best_score or (score == best_score and random.random() < 0.5):
                best_score = score
                best_move = (x, y)
        return best_move

    def _calculate_move_score(self, x: int, y: int) -> int:
        """Calculate score for a potential move."""
        score = 0
        for dx, dy in self.EIGHT_DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx <= self._grid_width and 0 <= ny <= self._grid_height:
                if self._grid[ny][nx] == self.PLAYER_1:
                    score += 3
                elif self._grid[ny][nx] == self.PLAYER_2:
                    score += 1
        return score

    def _execute_ai_move(self, x: int, y: int) -> tuple[int, int] | None:
        """Execute the AI move and return coordinates or None if game ends."""
        if self.place_dot(x, y):
            return None
        return x, y

    def _would_capture_player(self, x: int, y: int) -> bool:
        """Проверяет, приведет ли ход к захвату области игрока."""
        for dx, dy in self.FOUR_DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx <= self._grid_width and 0 <= ny <= self._grid_height:
                if self._grid[ny][nx] == self.PLAYER_1:
                    group, is_surrounded = self._get_group_with_status(nx, ny, self.PLAYER_1)
                    if is_surrounded:
                        return True
        return False
