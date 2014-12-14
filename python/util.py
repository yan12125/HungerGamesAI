import math

tools_map = {
    1: "speed_up", 
    2: "speed_change", 
    3: "water_ball", 
    4: "bombpower", 
    5: "ufo_tool", 
    6: "alive"
}

def posToGrid(pos):
    return (pos % 13, pos // 13)

def gridToPos(gridX, gridY):
    return gridX + gridY * 13

def coordToGrid(x, y):
    return (math.floor(x / 60), math.floor(y / 60))

def posToGridStr(pos):
    return '(%d, %d)' % posToGrid(pos)
