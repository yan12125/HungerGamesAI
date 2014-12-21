import util


class Grid(object):
    def __init__(self):
        self.grid_type = None
        self.tool = None

    def __str__(self):
        if self.grid_type == 'tool':
            return util.tools_map[self.tool]
        elif self.grid_type == 'empty':
            return ''
        else:
            return self.grid_type
