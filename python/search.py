from direction import Direction
from game_map import Map
import util


def find_successors(game_map, gridX, gridY):
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
        if game_map.grids[newPos].isWall():
            continue

        successors.append((direction, newPos))
    return successors


def bfs(game_map, startPos, criteria):
    frontier = [(startPos, [])]
    visited = set([startPos])
    while True:
        pos, path = frontier.pop(0)
        if criteria(pos):
            return path
        successors = find_successors(game_map, *util.posToGrid(pos))
        for direction, newPos in successors:
            if newPos in visited:
                continue

            newPath = path + [direction]
            frontier.append((newPos, newPath))
