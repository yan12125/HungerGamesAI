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

        def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY]
        actions = search.bfs(state.game_map, playerPos, __internal_safe)

        move = actions[0]
        if state.moveValidForMe(actions[0]):
            self.goMove(player, move)
        else:
            # If unable to go to specified pos now, go to current center first
            centerX, centerY = util.posToCoord(playerPos)
            dx, dy = (centerX - player.x, centerY - player.y)
            self.goMove(player, Direction.byDistance(dx, dy))
