import util
import texttable
from grid import Grid
import math
import time  # for bomb put time
from colorama import Fore
from direction import Direction
from player import Player

NEAR_ERR = 25  # half of the player width


class Map(object):

    def __init__(self):
        self.grids = [Grid() for i in util.grid_gen]  # indexed by pos
        self.safe_map_cache = None

    def setGrids(self, remote_grids, remote_ntp_offset):
        local_ntp_offset = util.getNTPOffset()
        if isinstance(local_ntp_offset, float) and isinstance(remote_ntp_offset, float):
            time_difference = remote_ntp_offset - local_ntp_offset
            print(Fore.MAGENTA+'Got NTP offset: remote=%f, local=%f' % (remote_ntp_offset, local_ntp_offset))
        else:
            print(Fore.MAGENTA+'No valid NTP offsets found. Bomb timing may be inaccurate')
            time_difference = 0

        for i in util.grid_gen:
            grid = self.grids[i]
            remote_grid = remote_grids[i]

            grid.grid_type = remote_grid['type']
            if grid.grid_type == 'tool':
                grid.tool = remote_grid['tool']
                toolname = util.tools_map[grid.tool]
                print('Initial tool %s at %s' % (toolname, util.gridStr(i)))
            elif grid.grid_type == Grid.BOMB:
                grid.bombPower = remote_grid['bombingPower']
                grid.bombPutTime = remote_grid['bombPutTime'] + time_difference
                print('Initial bomb at %s, power = %d, time put = %f' % (util.gridStr(i), grid.bombPower, grid.bombPutTime))
        self.dumpGrids()

    def gridIs(self, gridPos, grid_type):
        return self.grids[gridPos].grid_type == grid_type

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

    def bombPut(self, gridX, gridY, power):
        pos = util.gridToPos(gridX, gridY)
        print('Bomb put at %s' % util.gridStr(pos))
        grid = self.grids[pos]
        grid.grid_type = Grid.BOMB
        grid.bombPower = power
        grid.bombCanPass = True
        grid.bombPutTime = time.time()
        self.invalidateSafeMap()
        self.dumpGrids()

    def bombing(self, pos):
        self.invalidateSafeMap()

    def gridBombed(self, pos):
        print('Grid at %s bombed' % util.gridStr(pos))
        self.grids[pos].grid_type = 'empty'
        self.dumpGrids()
        self.invalidateSafeMap()

    def wallBombed(self, pos):
        print('Wall at %s bombed' % util.gridStr(pos))
        # Grid settings already done in gridBombed()
        self.invalidateSafeMap()

    def bombsGen(self):
        for i in range(0, len(self.grids)):
            grid = self.grids[i]
            if grid.grid_type == Grid.BOMB:
                yield (i, grid)

    def toolsGen(self):
        for i in range(0, len(self.grids)):
            grid = self.grids[i]
            if grid.grid_type == Grid.Tool:
                yield (i, grid)

    def bombCount(self):
        count = 0
        for i, grid in self.bombsGen():
            count += 1
        return count

    def eight_corners(self, x, y, half_side):
        corners = [
            (0, -half_side),
            (0, +half_side),
            (-half_side, 0),
            (+half_side, 0),
            (-half_side, -half_side),
            (+half_side, -half_side),
            (-half_side, +half_side),
            (+half_side, +half_side)
        ]
        return [(x+distance[0], y+distance[1]) for distance in corners]

    def near(self, x, y, passWall=False, half_side=NEAR_ERR):
        for newX, newY in self.eight_corners(x, y, half_side):
            if not self.coordInMap(newX, newY):
                return True
            grid = self.grids[util.coordToPos(newX, newY)]
            grid_type = grid.grid_type
            if grid_type == Grid.BOMB and grid.bombCanPass:
                continue
            if (grid_type == 'nvwall' or grid_type == 'vwall') and passWall:
                continue
            if grid_type != 'empty' and grid_type != 'tool':
                return True
        return False

    def nearPos(self, x, y, pos, half_side=NEAR_ERR):
        for newX, newY in self.eight_corners(x, y, half_side):
            if util.coordToPos(newX, newY) == pos:
                return True
        return False

    @staticmethod
    def gridInMap(gridX, gridY):
        return ((gridX >= 0 and gridX < util.map_dimension) and
                (gridY >= 0 and gridY < util.map_dimension))

    @staticmethod
    def coordInMap(x, y):
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

    # XXX
    """
    Currently on when a bomb put and a bomb vanishing
    Possibly race conditions?
    """
    def invalidateSafeMap(self):
        self.safe_map_cache = None

    def safeMap(self):
        if self.safe_map_cache:
            return self.safe_map_cache

        safe_map = util.linearGridToMap([True for i in util.grid_gen])

        def __markAsUnsafe(gridX, gridY):
            if not self.gridInMap(gridX, gridY):
                return
            safe_map[gridX][gridY] = False

        for i, grid in self.bombsGen():
            gridX, gridY = util.posToGrid(i)
            for direction in Direction.ALL:
                if direction == Direction.STOP:
                    __markAsUnsafe(gridX, gridY)
                else:
                    for i in range(0, grid.bombPower):
                        distance = Direction.distances[direction]
                        newX = gridX + distance[0] * (i+1)
                        newY = gridY + distance[1] * (i+1)
                        newP = util.gridToPos(newX, newY)
                        if Map.gridInMap(newX, newY) and self.gridIs(newP, Grid.NVWALL):
                            break
                        __markAsUnsafe(newX, newY)

        self.safe_map_cache = safe_map
        return safe_map

    def safeMapAroundPos(self, pos):
        safe_map = self.safeMap()
        gridX, gridY = util.posToGrid(pos)
        plusAndMinus = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
        pointAroundMe = \
        [(gridX + x, gridY + y) for x, y in plusAndMinus if self.gridInMap(gridX + x, gridY + y)]
        for x, y in pointAroundMe:
            if not safe_map[x][y]:
                return False
        return True

    def safeMapAround(self,pos):
        '''return list of action leading to safe place
        '''
        safe_map = self.safeMap()
        gridX, gridY = util.posToGrid(pos)
        plusAndMinus = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
        Move = [Direction.LEFT,Direction.RIGHT,Direction.DOWN,Direction.UP,Direction.STOP]
        MoveList=[]
        pointAroundMe = \
        [(gridX + x, gridY + y) for x, y in plusAndMinus if self.gridInMap(gridX + x, gridY + y)]
        for item in range(len( pointAroundMe)):
            if safe_map[pointAroundMe[item][0]][pointAroundMe[item][1]]:
                MoveList.append(Move[item])
        return MoveList


    def wayAroundPos(self, pos, player = Player(-1, "test")):
        safe_map = self.safeMap()
        gridX, gridY = util.posToGrid(pos)
        plusAndMinus = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        pointAroundMe = \
        [(gridX + x, gridY + y) for x, y in plusAndMinus if Map.gridInMap(gridX + x, gridY + y)]
        wayCount = 0
        for x, y in pointAroundMe:
            position = util.gridToPos(x, y)
            if safe_map[x][y] and\
               (self.grids[position].canPass() and not self.gridIs(position, Grid.BOMB) or player.penetrate):
                wayCount += 1
        return wayCount
    def moreWayAroundPos(self, pos, player = Player(-1, "test")):
        safe_map = self.safeMap()
        gridX, gridY = util.posToGrid(pos)
        plusAndMinus = [(-1, 0), (1, 0), (0, -1), (0, 1),(-2, 0), (2, 0), (0, -2), (0, 2)]
        pointAroundMe = \
        [(gridX + x, gridY + y) for x, y in plusAndMinus if Map.gridInMap(gridX + x, gridY + y)]
        wayCount = 0
        for x, y in pointAroundMe:
            position = util.gridToPos(x, y)
            if safe_map[x][y] and\
               (self.grids[position].canPass() and not self.gridIs(position, Grid.BOMB) or player.penetrate):
                wayCount += 1
        return wayCount
