from __future__ import division
import math
import re
import ntplib
import grid
from task_loop import TaskLoop
from compat import queue

BASE_INTERVAL = 1/60

DEBUG = False

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
map_pixelwidth = map_dimension * grid_dimension
grid_count = map_dimension * map_dimension
grid_gen = range(0, grid_count)
empty_linear_grid = [grid.Grid() for i in grid_gen]

loop = TaskLoop()

packet_queue = queue.Queue()
commute_packet_queue=queue.Queue()

ntp_offset = None
client = ntplib.NTPClient()


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
    # Note: math.floor returns floats in python 2
    gridX = int(math.floor(x / grid_dimension))
    gridY = int(math.floor(y / grid_dimension))
    return (gridX, gridY)


def gridToCoord(gridX, gridY):
    """
    Transform (gridX, gridY) to coordinates
    """
    x = grid_dimension * gridX + grid_dimension / 2
    y = grid_dimension * gridY + grid_dimension / 2
    return (x, y)


def coordToPos(x, y):
    """
    Transform coordinate (x, y) to linear position
    """
    return gridToPos(*coordToGrid(x, y))


def posToCoord(pos):
    return gridToCoord(*posToGrid(pos))


def coordStr(x, y):
    """
    Transform coordinate (x, y) to string representation
    """
    return "(%d, %d)" % (x, y)


def gridStr(pos):
    """
    Transform pos to string "(gridX, gridY)"
    """
    return '(%d, %d)' % posToGrid(pos)


def strToGrid(data):
    matches = re.match(r'\((\d+),(\d+)\)', data.replace(" ", ""))
    if matches:
        return [int(coord) for coord in matches.groups()]
    else:
        raise Exception("Invalid position: %s" % data)


def linearGridToMap(linearGrid):
    """
    Transform linear grids, one dimensional list with length n*n to
    two dimensional map with dimensions n and n
    """
    return [[linearGrid[gridToPos(x, y)] for x in map_gen] for y in map_gen]


def empty_map():
    return linearGridToMap(empty_linear_grid)


def mark_finished():
    loop.add_finished_task()
    packet_queue.put(None)


def manhattanDistance(xy1, xy2):
    "Returns the Manhattan distance between points xy1 and xy2"
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


def getNTPOffset():
    global ntp_offset
    try:
        response = client.request('pool.ntp.org', version=3)
        ntp_offset = response.offset
    except NTPException:
        print(Fore.RED+'Warning: failed to get NTP time. Bomb timer may be inaccurate')
