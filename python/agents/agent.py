import util
from colorama import Fore
from direction import Direction
from grid import Grid


class Agent(object):
    def __init__(self):
        self.lastMove = Direction.STOP
        self.whichState = 0
        self.lastState = 0
        self.lastPos = None

    def tryPutBomb(self, state, player):
        if player.bombCount >= player.bombLimit:
            return False

        bombX, bombY = util.coordToGrid(player.x, player.y)
        bombPos = util.gridToPos(bombX, bombY)
        grid = state.game_map.grids[bombPos]
        if grid.grid_type is Grid.BOMB:
            return False

        if grid.grid_type == Grid.NVWALL or grid.grid_type == Grid.VWALL:
            print(Fore.RED+'Warning: attempt to put bomb on wall %s' % util.gridStr(bombPos))
            return False

        self.lastState = self.whichState
        self.whichState = 1
        self.lastPos = bombPos
        
#        state.game_map.bombPut(bombX,bombY, player.bombPower)

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
