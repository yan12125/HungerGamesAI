import util
from grid import Grid
from direction import Direction
import search


class BomberAgent(object):
    def __init__(self):
        pass

    def tryPutBomb(self, state, player):
        if player.bombCount >= player.bombLimit:
            return

        bombX, bombY = util.coordToGrid(player.x, player.y)
        bombPos = util.gridToPos(bombX, bombY)
        grid = state.game_map.grids[bombPos]
        if grid.grid_type is Grid.BOMB or grid.willBeBomb:
            return

        # grid.grid_type = Grid.BOMB
        # grid.bombPower = player.bombPower
        grid.willBeBomb = True

        print("Put a bomb at %s" % util.gridStr(bombPos))
        player.bombCount += 1
        util.packet_queue.put({
            'event': 'put_bomb',
            'playerid': player.player_id,
            'bombingPower': player.bombPower,
            'x': bombX,
            'y': bombY
        })

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

    def goMove(self, player, move):
        newCoord = player.newCoord(move)

        player.x, player.y = newCoord

        util.packet_queue.put({
            'event': 'player_position',
            'x': player.x,
            'y': player.y
        })
