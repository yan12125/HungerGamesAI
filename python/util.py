import math
import grid

tools_map = {
    1: "speed_up",
    2: "speed_change",
    3: "water_ball",
    4: "bombpower",
    5: "ufo_tool",
    6: "alive"
}

map_dimension = 13
map_gen = range(0, map_dimension)
grid_dimension = 60
grid_count = map_dimension * map_dimension
grid_gen = range(0, grid_count)
empty_linear_grid = [grid.Grid() for i in grid_gen]

loop = None  # will be a TaskLoop object


def posToGrid(pos):
    """
    Transform pos to (x, y)
    """
    return (pos % map_dimension, pos // map_dimension)


def gridToPos(gridX, gridY):
    """
    Transform (gridX, gridY) to pos
    """
    return gridX + gridY * map_dimension


def coordToGrid(x, y):
    """
    Transform coordinate (x, y) to (gridX, gridY)
    """
    return (math.floor(x / grid_dimension), math.floor(y / grid_dimension))


def posToGridStr(pos):
    """
    Transform pos to string "(gridX, gridY)"
    """
    return '(%d, %d)' % posToGrid(pos)


def linearGridToMap(linearGrid):
    """
    Transform linear grids, one dimensional list with length n*n to
    two dimensional map with dimensions n and n
    """
    return [[linearGrid[gridToPos(x, y)] for x in map_gen] for y in map_gen]


def empty_map():
    return linearGridToMap(empty_linear_grid)
