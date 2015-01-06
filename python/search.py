from direction import Direction
from game_map import Map
import util
from player import Player
from grid import Grid


def find_successors_grid(game_map, pos, Player):
    gridX, gridY = util.posToGrid(pos)
    successors = []
    for direction in Direction.ALL:
        if direction == Direction.STOP:
            continue
        distance = Direction.distances[direction]
        newX = gridX + distance[0]
        newY = gridY + distance[1]
        if not Map.gridInMap(newX, newY):
            continue

        newPos = util.gridToPos(newX, newY)
        if not Player.penetrate and not game_map.grids[newPos].canPass():
            continue
        elif game_map.gridIs(newPos, Grid.BOMB) and not game_map.grids[newPos].bombCanPass and not Player.penetrate:
            continue

        successors.append((direction, newPos))
    return successors


def find_successors_pixel(game_map, coord, Player):
    x, y = coord
    successors = []
    for direction in Direction.ALL:
        if direction == Direction.STOP:
            continue

        distance = Direction.distances[direction]
        newX = x + distance[0] * Player.speed
        newY = y + distance[1] * Player.speed

        if not Map.coordInMap(newX, newY):
            continue

        if game_map.near(newX, newY, Player.penetrate):
            continue

        successors.append((direction, (newX, newY)))
    return successors

def bfs_common(game_map, startPos, criteria, pathCriteria, Player, N, find_successors):
    count = 0
    frontier = [(startPos, [])]
    visited = set([startPos])
    while frontier:
#        print frontier
        pos, path = frontier.pop(0)
        if criteria(pos):
            count += 1
            if count == N:
                return path
        successors = find_successors(game_map, pos, Player)
        for direction, newPos in successors:
            if newPos in visited:
                continue
            if pathCriteria(newPos):
              newPath = path + [direction]
              frontier.append((newPos, newPath))
              visited.update([newPos])


def bfs(game_map, start, criteria, pathCriteria=lambda pos: True, Player=Player(-1, "test"), N=1):
    return bfs_common(game_map, start, criteria, pathCriteria, Player, N, find_successors_grid)


def bfsPixel(game_map, start, criteria, pathCriteria=lambda pos: True, Player=Player(-1, "test"), N=1):
    return bfs_common(game_map, start, criteria, pathCriteria, Player, N, find_successors_pixel)


def bfs_count(game_map, startPos, criteria,pathCriteria=lambda pos: True, Player= Player(-1, "test"), N=20):
    frontier = [(startPos, [])]
    visited = set([startPos])
    while True:
        if not frontier: return N+60
        pos, path = frontier.pop(0)
        if criteria(pos):
          return len(path)
        if len(path)==N:
          return N+10
        successors = find_successors_grid(game_map, pos,Player)
        for direction, newPos in successors:
            if newPos in visited:
                continue
            if pathCriteria(newPos):
              newPath = path + [direction]
              frontier.append((newPos, newPath))
              visited.update([newPos])
