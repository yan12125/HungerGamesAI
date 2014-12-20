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
