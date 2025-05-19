from typing import Tuple, List, Set, Optional
from kivy.input.motionevent import MotionEvent
from kivy.core.audio import Sound

from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Rectangle, Color
from kivy.core.audio import SoundLoader
from kivy.core.window import Window, WindowBase

from random import randint

from tools.signal_bus import SignalBus
from enums.direction import Direction
from enums.colors_enum import ColorsEnum

from config import SOUND_DIR, FPS
from config import START_SNAKE_SIZE, START_SNAKE_DIRECTION
from config import USE_WALLS, USE_WALL_MAP, WALL_MAP, WALL_CHAR, COLS, ROWS


class SnakeGame(Widget):
    def __init__(self, **kwargs) -> None:
        super(SnakeGame, self).__init__(**kwargs)

        self.snake, self.snake_direction = self.init_snake()
        self.new_snake_direction = self.snake_direction

        self.walls: Set[Tuple[int, int]] = self.init_walls()
        self.food: Optional[Tuple[int, int]] = self.spawn_food()

        self.score: int = 0
        self.cell_size: int = 20  # Устанавливается по умолчанию, но обновляется внешним сигналом
        self.defeat: bool = False

        Window.bind(on_key_down=self.on_key_down)
        self.bind(size=self.update_canvas)
        self.bind(pos=self.update_canvas)
        Clock.schedule_interval(self.update, 1 / FPS)
        
        SignalBus.subscribe('cell_size_updated', self.update_cell_size)

        self.eat_sound: Optional[Sound] = SoundLoader.load(f"{SOUND_DIR}/EatSound.ogg")
        self.defeat_sound: Optional[Sound] = SoundLoader.load(f"{SOUND_DIR}/DieSound.ogg")

    @staticmethod
    def init_walls() -> Set[Tuple[int, int]]:
        walls = set()
        if not USE_WALLS:
            return walls
        if not USE_WALL_MAP:
            for x in range(COLS):
                walls.add((x, 0))
                walls.add((x, ROWS - 1))
            for y in range(ROWS):
                walls.add((0, y))
                walls.add((COLS - 1, y))
        else:
            for y, row in enumerate(WALL_MAP):
                for x, cell in enumerate(row):
                    if cell == WALL_CHAR:
                        walls.add((x, ROWS-1-y))
        return walls

    @staticmethod
    def init_snake() -> Tuple[List[Tuple[int, int]], Direction]:
        x, y = COLS // 2 - 1, ROWS // 2 + 1  # Начальная позиция змейки в центре игрового поля
        snake_direction = START_SNAKE_DIRECTION
        dx, dy = snake_direction.get_opposite().value
        snake = list(reversed([(x + i * dx, y + i * dy) for i in range(START_SNAKE_SIZE)]))
        return snake, snake_direction

    def update_cell_size(self, new_cell_size: int) -> None:
        self.cell_size = new_cell_size

    def on_key_down(self, window: WindowBase, key: int, scancode: int, codepoint: str, modifier: list) -> None:
        if self.snake_direction != self.new_snake_direction:
            return

        keymap = {
            'w': Direction.UP,
            's': Direction.DOWN,
            'a': Direction.LEFT,
            'd': Direction.RIGHT
        }

        if not codepoint:
            return

        key_char = codepoint.lower()
        if key_char in keymap:
            new_direction = keymap[key_char]
            if not self.snake_direction.is_opposite(new_direction):
                self.new_snake_direction = new_direction

    def on_touch_up(self, touch: MotionEvent) -> None:
        if self.snake_direction != self.new_snake_direction:
            return
        if not self.collide_point(touch.x, touch.y):
            return

        dx = touch.x - touch.ox
        dy = touch.y - touch.oy

        if abs(dx) > abs(dy):
            new_direction = Direction.RIGHT if dx > 0 else Direction.LEFT
        else:
            new_direction = Direction.UP if dy > 0 else Direction.DOWN

        if not self.snake_direction.is_opposite(new_direction):
            self.new_snake_direction = new_direction

    def update(self, dt: float) -> None:
        if self.defeat:
            return

        self.snake_direction = self.new_snake_direction

        head = self.snake[-1]
        direction = self.snake_direction.value
        new_head_cell = self.fix_snake_position((head[0] + direction[0], head[1] + direction[1]))

        if self.is_defeated(new_head_cell):
            self.end_game()
            self.update_canvas()
            return

        self.check_eating(new_head_cell)

        self.update_canvas()

    def check_eating(self, new_head_cell: Tuple[int, int]) -> None:
        if new_head_cell == self.food:
            self.snake.append(new_head_cell)
            self.food = self.spawn_food()
            self.score += 1
            SignalBus.emit('score_updated', self.score)
            if self.eat_sound:
                self.eat_sound.play()
        else:
            self.snake = self.snake[1:] + [new_head_cell]

    def is_defeated(self, head_cell: Tuple[int, int]) -> bool:
        return head_cell in self.snake[:-1] or head_cell in self.walls

    @staticmethod
    def fix_snake_position(head_cell: Tuple[int, int]) -> Tuple[int, int]:
        x, y = head_cell
        return x % COLS, y % ROWS

    def update_canvas(self, *args) -> None:
        self.canvas.clear()
        with self.canvas:
            Color(*ColorsEnum.SNAKE.value)
            self.snake_rects = [
                Rectangle(pos=self.cell_to_pos(part), size=(self.cell_size, self.cell_size)) for part in self.snake]

            Color(*ColorsEnum.FOOD.value)
            self.food_rect = Rectangle(pos=self.cell_to_pos(self.food), size=(self.cell_size, self.cell_size))

            Color(*ColorsEnum.WALL.value)
            self.wall_rects = [
                Rectangle(pos=self.cell_to_pos(pos), size=(self.cell_size, self.cell_size)) for pos in self.walls]

            if self.defeat:
                head = self.snake[-1]
                Color(*ColorsEnum.DEFEAT.value)
                Rectangle(pos=self.cell_to_pos(head), size=(self.cell_size, self.cell_size))

    def reset_game(self) -> None:
        self.defeat = False
        self.snake, self.snake_direction = self.init_snake()
        self.new_snake_direction = self.snake_direction
        self.food = self.spawn_food()
        self.score = 0
        SignalBus.emit('score_updated', self.score)

        self.defeat_sound.stop()

    def end_game(self) -> None:
        self.defeat = True
        if self.defeat_sound:
            self.defeat_sound.play()

    def spawn_food(self) -> Optional[Tuple[int, int]]:
        empty_cells = [(x, y) for x in range(COLS) for y in range(ROWS)
                       if (x, y) not in self.snake and (x, y) not in self.walls]
        if not empty_cells:
            return None
        return empty_cells[randint(0, len(empty_cells) - 1)]

    def cell_to_pos(self, cell: Tuple[int, int]) -> Tuple[float, float]:
        return (self.x + cell[0] * self.cell_size, self.y + cell[1] * self.cell_size)

    def pos_to_cell(self, pos: Tuple[float, float]) -> Tuple[int, int]:
        return ((self.x + pos[0]) // self.cell_size, (self.y + pos[1]) // self.cell_size)
