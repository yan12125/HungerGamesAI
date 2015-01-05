import util
import search
from .agent import Agent
from direction import Direction


class BomberAgent(Agent):
    def __init__(self):
        super(BomberAgent, self).__init__()

    def once(self, state):
        if not util.packet_queue.empty():
            return

        player = state.me()

        self.tryPutBomb(state, player)

        safe_map = state.game_map.safeMap()

        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)
        if safe_map[gridX][gridY]:
            return

        def __safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY]
        actions = search.bfs(state.game_map, playerPos, __safe, Player=player)

        if actions:
            move = actions[0]
        else:
            print("No safe grid")
            return
        if state.moveValidForMe(actions[0]):
            self.goMove(player, move)
            return

        distance = Direction.distances[move]
        destPos = util.gridToPos(gridX + distance[0], gridY + distance[1])

        def __toGrid(coord):
            return destPos == util.coordToPos(*coord)

        startCoord = (player.x, player.y)
        actions = search.bfsPixel(state.game_map, startCoord, __toGrid, Player=player)
        if actions:
            move = actions[0]
        else:
            print("Can't reach dest grid")
            return

        if not state.moveValidForMe(move):
            raise Exception('Unexpected: move %s should be valid' % move)

        self.goMove(player, move)
