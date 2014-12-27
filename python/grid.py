import util


class Grid(object):
    # Static
    EMPTY = 'empty'
    BOMB = 'bomb'
    VWALL = 'vwall'  # volatile walls, which can be destroyed by bombs
    NVWALL = 'nvwall'  # non-volatile walls
    TOOL = 'tool'

    def __init__(self):
        self.grid_type = None
        self.tool = None
        self.willBeBomb = False
        self.bombPower = None

    def __str__(self):
        if self.grid_type == 'tool':
            return util.tools_map[self.tool]
        elif self.grid_type == 'empty':
            return ''
        else:
            return self.grid_type

    def isWall(self):
        return self.grid_type == Grid.VWALL or self.grid_type == Grid.NVWALL

    def canPass(self):
        return self.grid_type == Grid.TOOL or self.grid_type == Grid.EMPTY
