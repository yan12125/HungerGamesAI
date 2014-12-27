import random
import util
from direction import Direction
from grid import Grid


class WalkbomberAgent(object):
    def __init__(self):
        self.lastMove = Direction.STOP
        self.whichState = 0
        self.lastBombPos = None
    
    def tryPutBomb(self, state, player):
        if player.bombCount >= player.bombLimit:
            return

        bombX, bombY = util.coordToGrid(player.x, player.y)
        bombPos = util.gridToPos(bombX, bombY)
        
        if state.game_map.gridIs(bombPos, Grid.BOMB):
            return

        self.whichState = 1
        self.lastBombPos = bombPos
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

        move = self.lastMove
        
        player = state.me()

        self.tryPutBomb(state, player)
        
        safe_map = state.game_map.safeMap()

        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)
        bombPos = util.gridToPos(gridX, gridY)

        if self.whichState == 1 and bombPos != self.lastBombPos:
            self.whichState = 2
        
        validMoves = state.validMovesForMe()
        if Direction.STOP in validMoves:
            # Not always true. Eg., on a newly put bomb
            validMoves.remove(Direction.STOP)
        if not validMoves:
            print('Error: no valid moves')
            return

        def oppDirection(d):
            if d == Direction.UP:
                return Direction.DOWN
            elif d == Direction.DOWN:
                return Direction.UP
            elif d == Direction.LEFT:
                return Direction.RIGHT
            elif d == Direction.RIGHT:
                return Direction.LEFT
            else:
                return Direction.STOP

        print(self.whichState)
        #run away from my own bomb
        if self.whichState == 1 and move == Direction.STOP:
            move = random.choice(validMoves)
        #run away from unsafe place
        elif self.whichState == 2:
            validMoves = [m for m in state.validMovesForMe() if m != move and m != oppDirection(move)]
            move = random.choice(validMoves)
            self.whichState = 3
                        
        if move == Direction.STOP or not state.moveValidForMe(move):
            if not validMoves:
                print('Error: no valid moves')
                return
            move = random.choice(validMoves)

        self.lastMove = move

        distance = Direction.distances[move]

        player = state.me()
        player.x += distance[0] * player.speed
        player.y += distance[1] * player.speed

        util.packet_queue.put({
            'event': 'player_position',
            'x': player.x,
            'y': player.y
        })
