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


def bfs(game_map, startPos, criteria, pathCriteria=lambda pos: True, N=1):
    count = 0
    frontier = [(startPos, [])]
    visited = set([startPos])
    while frontier:
        pos, path = frontier.pop(0)
        if criteria(pos):
            count += 1
            if count == N:
                return path
        successors = find_successors(game_map, *util.posToGrid(pos))
        for direction, newPos in successors:
            if newPos in visited:
                continue

            newPath = path + [direction]
            frontier.append((newPos, newPath))
            visited.update([newPos])

def bfs_count(game_map, startPos, criteria, N=20):
    count = 0
    frontier = [(startPos, [])]
    visited = set([startPos])
    while True:
        if not frontier: return N+10
        pos, path = frontier.pop(0)
        if criteria(pos):
          return count
        if count==N:
          return N+1
        count += 1
        successors = find_successors(game_map, *util.posToGrid(pos))
        for direction, newPos in successors:
            if newPos in visited:
                continue

            newPath = path + [direction]
            frontier.append((newPos, newPath))
            visited.update([newPos])
            if pathCriteria(newPos):
                newPath = path + [direction]
                frontier.append((newPos, newPath))
                visited.update([newPos])
