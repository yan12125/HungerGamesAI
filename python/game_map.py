import util
import texttable

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

class Map(object):
    grids = [ Grid() for i in util.grid_generator ] # indexed by pos

    def __init__(self):
        pass

    def setGrids(self, remote_grids):
        for i in util.grid_generator:
            grid = self.grids[i]
            remote_grid = remote_grids[i]

            grid.grid_type = remote_grid['type']
            if grid.grid_type == 'tool':
                grid.tool = remote_grid['tool']
                print('Initial tool %s at %s' % (util.tools_map[grid.tool], util.posToGridStr(i)))
        self.dumpGrids()

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
        strings = self.gridStrings()
        def _transform(string):
            if len(string) > 4:
                return string[0:2] + '\n' + string[2:4]
            elif len(string) > 2:
                return string[0:2] + '\n' + string[2:]
            else:
                return string
        table = texttable.Texttable()
        table.add_rows([ [ _transform(strings[util.gridToPos(x, y)]) for x in util.map_generator ] for y in util.map_generator ])
        print(table.draw())

    def gridStrings(self):
        return [ str(self.grids[pos]) for pos in util.grid_generator ]
