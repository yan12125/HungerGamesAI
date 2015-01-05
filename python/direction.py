class Direction(object):
    """
    Note: (0, 0) is the left-top corner
    """
    LEFT = 'LEFT'
    RIGHT = 'RIGHT'
    UP = 'UP'
    DOWN = 'DOWN'
    STOP = 'STOP'
    ALL = [UP, DOWN, LEFT, RIGHT, STOP]

    distances = {
        LEFT: (-1, 0),
        RIGHT: (1, 0),
        UP: (0, -1),
        DOWN: (0, 1),
        STOP: (0, 0)
    }

    @classmethod
    def byDistance(cls, dx, dy):
        """
        Return closest direction according to distance vector (dx, dy)
        Ex:
        (0, 0) => STOP
        (1, 0) => RIGHT
        (-3, 2) => LEFT
        (4, -4) => DOWN
        """
        adx = abs(dx)
        ady = abs(dy)
        if adx == 0 and ady == 0:
            return cls.STOP
        if adx > ady:  # indicates adx != 0
            if dx > 0:
                return cls.RIGHT
            else:
                return cls.LEFT
        else:
            if dy > 0:
                return cls.DOWN
            else:
                return cls.UP


def oppDirection(d):
    if d == Direction.UP:
        return Direction.DOWN
    elif d == Direction.DOWN:
        return Direction.UP
    elif d == Direction.LEFT:
        return Direction.RIGHT
    elif d == Direction.RIGHT:
        return Direction.LEFT
    else:
        return Direction.STOP
