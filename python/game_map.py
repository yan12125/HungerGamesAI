import util
import texttable
import grid


class Map(object):
    grids = [grid.Grid() for i in util.grid_gen]  # indexed by pos

    def __init__(self):
        pass

    def setGrids(self, remote_grids):
        for i in util.grid_gen:
            grid = self.grids[i]
            remote_grid = remote_grids[i]

            grid.grid_type = remote_grid['type']
            if grid.grid_type == 'tool':
                grid.tool = remote_grid['tool']
                toolname = util.tools_map[grid.tool]
                print('Initial tool %s at %s' % (toolname, util.gridStr(i)))
        self.dumpGrids()

    def toolAppeared(self, pos, tooltype):
        grid = self.grids[pos]

        grid.grid_type = 'tool'
        grid.tool = tooltype
        toolname = util.tools_map[grid.tool]

        print('Tool %s appeared at %s' % (toolname, util.posToGrid(pos)))

        self.dumpGrids()

    def toolDisappeared(self, eater, tooltype, pos):
        grid = self.grids[pos]
        toolname = util.tools_map[grid.tool]

        print('Tool %s at %s disappeared' % (toolname, util.posToGrid(pos)))

        grid.grid_type = 'empty'
        grid.tool = None

        self.dumpGrids()

    def bombPut(self, pos):
        print('Bomb put at %s' % util.gridStr(pos))
        self.grids[pos].grid_type = 'bomb'
        self.dumpGrids()

    def gridBombed(self, pos):
        print('Grid at %s bombed' % util.gridStr(pos))
        self.grids[pos].grid_type = 'empty'
        self.dumpGrids()

    def wallBombed(self, pos):
        print('Wall at %s bombed' % util.gridStr(pos))
        # Grid settings already done in gridBombed()

    def near(self, x, y, half_side):
        corners = [
            (-half_side, -half_side),
            (0, -half_side),
            (+half_side, -half_side),
            (-half_side, 0),
            (+half_side, 0),
            (-half_side, +half_side),
            (0, +half_side),
            (+half_side, +half_side)
        ]
        for i in range(0, len(corners)):
            newX = x + corners[i][0]
            newY = y + corners[i][1]
            if not self.coordInMap(newX, newY):
                return True
            grid_type = self.grids[util.coordToPos(newX, newY)].grid_type
            if grid_type != 'empty' and grid_type != 'tool':
                return True
        return False

    def coordInMap(self, x, y):
        return ((x >= 0 and x < util.map_pixelwidth) and
                (y >= 0 and y < util.map_pixelwidth))

    def dumpGrids(self):

        def _transform(string):
            if len(string) > 4:
                return string[0:2] + '\n' + string[2:4]
            elif len(string) > 2:
                return string[0:2] + '\n' + string[2:]
            else:
                return string

        strings = self.gridStrings()
        gridStrings = [_transform(strings[pos]) for pos in util.grid_gen]

        table = texttable.Texttable()
        table.add_rows(util.linearGridToMap(gridStrings))
        # print(table.draw())

    def gridStrings(self):
        return [str(self.grids[pos]) for pos in util.grid_gen]
