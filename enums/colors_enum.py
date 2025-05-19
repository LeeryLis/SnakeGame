from enum import Enum


class ColorsEnum(Enum):
    SNAKE = (0, 1, 0, 1)
    FOOD = (1, 0, 0, 1)
    WALL = (0.5, 0.5, 0.5, 1)
    DEFEAT = (1, 0.25, 0, 1)
