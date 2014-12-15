import util

class Grid(object):
    grid_symbol = {
        'empty': ' ', 
        'bomb': 'b', 
        'vwall': 'w', 
        'nvwall': 'n'
    }

    grid_type = None
    tool = None

    def __str__(self):
       if self.grid_type in self.grid_symbol:
           return self.grid_symbol[self.grid_type]
       elif self.grid_type == 'tool':
           return str(self.tool)
       else:
           raise Exception('Unknown grid type', self.grid_type)

class Map(object):
    grids = [ Grid() for i in range(0, util.grid_count) ] # indexed by pos

    def __init__(self):
        pass

    def setGrids(self, remote_grids):
        for i in range(0, util.grid_count):
            grid = self.grids[i]
            remote_grid = remote_grids[i]

            grid.grid_type = remote_grid['type']
            if grid.grid_type == 'tool':
                grid.tool = remote_grid['tool']
                print('Initial tool %s at %s' % (util.tools_map[grid.tool], util.posToGridStr(i)))

    def toolAppeared(self, pos, tooltype):
        grid = self.grids[pos]

        grid.grid_type = 'tool'
        grid.tool = tooltype

        print('Tool %s appeared at %s' % (util.tools_map[grid.tool], util.posToGrid(pos)))

        self.dumpGrids()

    def toolDisappeared(self, eater, tooltype, pos):
        grid = self.grids[pos]

        print('Tool %s at %s disappeared' % (util.tools_map[grid.tool], util.posToGrid(pos)))

        grid.grid_type = 'empty'
        grid.tool = None

        self.dumpGrids()

    def bombPut(self, pos):
        print('Bomb put at %s' % util.posToGridStr(pos))
        self.grids[pos].grid_type = 'bomb'
        self.dumpGrids()

    def gridBombed(self, pos):
        print('Grid at %s bombed' % util.posToGridStr(pos))
        self.grids[pos].grid_type = 'empty'
        self.dumpGrids()

    def wallBombed(self, pos):
        print('Wall at %s bombed' % util.posToGridStr(pos))
        # Grid settings already done in gridBombed()

    def dumpGrids(self):
        print(str(self))

    def __str__(self):
        output_str = ''
        for y in range(0, util.map_dimension):
            for x in range(0, util.map_dimension):
                output_str += str(self.grids[util.gridToPos(x, y)])
            output_str += '\n'
        return output_str
