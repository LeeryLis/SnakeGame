from enums.direction import Direction
from wall_maps import wall_maps, Map, WALL_CHAR

USE_WALLS = True
USE_WALL_MAP = True

WALL_MAP = wall_maps[Map.BIG_BOSS]
WALL_CHAR = WALL_CHAR

# Размеры игрового поля
if USE_WALL_MAP:
    COLS = max(len(row) for row in WALL_MAP)
    ROWS = len(WALL_MAP)
else:
    COLS = 20*2
    ROWS = 30*2

# Начальные размеры змейки
START_SNAKE_SIZE = 3

# Начальное направление движения
START_SNAKE_DIRECTION = Direction.RIGHT
    
# Число кадров в секунду
FPS = 5*2

# Директория музыки
MUSIC_DIR = "music"

# Директория звуков
SOUND_DIR = "sounds"
