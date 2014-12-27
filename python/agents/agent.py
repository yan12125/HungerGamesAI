import util
from direction import Direction
from grid import Grid

class Agent(object):
    def __init__(self):
        self.lastMove = Direction.STOP
        self.whichState = 0
        self.lastBombPos = None

    def tryPutBomb(self, state, player):
        if player.bombCount >= player.bombLimit:
            return False

        bombX, bombY = util.coordToGrid(player.x, player.y)
        bombPos = util.gridToPos(bombX, bombY)
        grid = state.game_map.grids[bombPos]
        if grid.grid_type is Grid.BOMB or grid.willBeBomb:
            return False

        self.whichState = 1
        self.lastBombPos = bombPos
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

        return True

    def goMove(self, player, move):
        newCoord = player.newCoord(move)

        player.x, player.y = newCoord

        util.packet_queue.put({
            'event': 'player_position',
            'x': player.x,
            'y': player.y
        })

    def once(self, state):
        raise NotImplementedError("Please Implement this method")
