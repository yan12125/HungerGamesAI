import random
import util
from direction import Direction, oppDirection
from agent import Agent

class WalkbomberAgent(Agent):
    def __init__(self):
        super(WalkbomberAgent, self).__init__()

    def once(self, state):
        if not util.packet_queue.empty():
            return

        move = self.lastMove

        player = state.me()

        if not state.moveValidForMe(move):
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

        # print(self.whichState)
        # run away from my own bomb
        if self.whichState == 1 and move == Direction.STOP:
            move = random.choice(validMoves)
        # run away from unsafe place
        elif self.whichState == 2:
            validMoves = [m for m in state.validMovesForMe() if m != move and m != oppDirection(move)]
            if validMoves:
                move = random.choice(validMoves)
                self.whichState = 3
        elif self.whichState == 3:
            pass

        if move == Direction.STOP or not state.moveValidForMe(move):
            if not validMoves:
                print('Error: no valid moves')
                return
            move = random.choice(validMoves)

        self.lastMove = move

        self.goMove(player, move)
