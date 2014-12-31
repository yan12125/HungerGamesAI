from direction import Direction
from game_map import Map
import util
from player import Player
from grid import Grid


def find_successors(game_map, gridX, gridY, Player=Player(-1, "test")):
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


def bfs(game_map, startPos, criteria, pathCriteria=lambda pos: True, Player=Player(-1, "test"), N=1):
    count = 0
    frontier = [(startPos, [])]
    visited = set([startPos])
    while frontier:
        pos, path = frontier.pop(0)
        if criteria(pos):
            count += 1
            if count == N:
                return path
        gridX, gridY = util.posToGrid(pos)
        successors = find_successors(game_map, gridX, gridY, Player)
        for direction, newPos in successors:
            if newPos in visited:
                continue
            if pathCriteria(newPos):
              newPath = path + [direction]
              frontier.append((newPos, newPath))
              visited.update([newPos])

def bfs_count(game_map, startPos, criteria, N=20):
    frontier = [(startPos, [])]
    visited = set([startPos])
    while True:
        if not frontier: return N+60
        pos, path = frontier.pop(0)
        if criteria(pos):
          return len(path)
        if len(path)==N:
          return N+10
        successors = find_successors(game_map, *util.posToGrid(pos))
        for direction, newPos in successors:
            if newPos in visited:
                continue

            newPath = path + [direction]
            frontier.append((newPos, newPath))
            visited.update([newPos])
