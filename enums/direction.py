from enum import Enum


class Direction(Enum):
    RIGHT = (1, 0)
    LEFT = (-1, 0)
    UP = (0, 1)
    DOWN = (0, -1)
    
    def get_opposite(self):
        opposites = {
            Direction.RIGHT: Direction.LEFT,
            Direction.LEFT: Direction.RIGHT,
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
        }
        return opposites[self]

    def is_opposite(self, other: 'Direction') -> bool:
        dx1, dy1 = self.value
        dx2, dy2 = other.value
        return dx1 == -dx2 and dy1 == -dy2
