import util


class Grid(object):
    grid_type = None
    tool = None

    def __str__(self):
        if self.grid_type == 'tool':
            return util.tools_map[self.tool]
        elif self.grid_type == 'empty':
            return ''
        else:
            return self.grid_type
