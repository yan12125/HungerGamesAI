import util

class Grid(object):
    grid_type = None
    tool = None

class Map(object):
    grids = [ Grid() for i in range(0,13*13) ]

    def __init__(self):
        pass

    def setGrids(self, remote_grids):
        for i in range(0, 13*13):
            grid = self.grids[i]
            remote_grid = remote_grids[i]

            grid.grid_type = remote_grid['type']
            if grid.grid_type == 'tool':
                grid.tool = remote_grid['tool']
                print('Initial tool %s at %s' % (util.tools_map[grid.tool], util.posToGridStr(i)))

    def toolAppeared(self, data):
        pos = data['grid']
        grid = self.grids[pos]

        grid.grid_type = 'tool'
        grid.tool = data['tooltype']
        print('Tool %s appeared at %s' % (util.tools_map[grid.tool], util.posToGrid(pos)))

    def toolDisappeared(self, eater, tooltype, pos):
        grid = self.grids[pos]
        grid.grid_type = 'empty'
        grid.tool = None
