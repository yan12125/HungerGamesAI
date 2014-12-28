import random
import search
import util
from direction import Direction, oppDirection
from agent import Agent

class WalkbomberAgent(Agent):
    def __init__(self):
        super(WalkbomberAgent, self).__init__()
        self.lastMove = Direction.UP

    def once(self, state):
        if not util.packet_queue.empty():
            return

        move = self.lastMove

        safe_map = state.game_map.safeMap()

        player = state.me()

        if not state.moveValidForMe(move):
            self.tryPutBomb(state, player)

        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)
        bombPos = util.gridToPos(gridX, gridY)

        if self.whichState == 0 and self.lastState == 1 and bombPos != self.lastPos:
            self.whichState = 2
        elif self.whichState == 0 and self.lastState == 2 and safe_map[gridX][gridY] == True:
            self.whichState = 3

        validMoves = state.validMovesForMe()
        if Direction.STOP in validMoves:
            # Not always true. Eg., on a newly put bomb
            validMoves.remove(Direction.STOP)
        if not validMoves:
            print('Error: no valid moves')
            return

        # can we stop?

        print(self.whichState)
        # run away from my own bomb
        if self.whichState == 1:
            if move == Direction.STOP:
                move = random.choice(validMoves)
            self.whichState = 0
            self.lastState = 1
        # run away from unsafe place
        elif self.whichState == 2:
            moves = [m for m in validMoves if m != move and m != oppDirection(move)]
            if moves:
                move = random.choice(moves)
            self.whichState = 0
            self.lastState = 2
        elif self.whichState == 3:
            if not validMoves:
                print('Error: no valid moves')
                return
            else:
                def __internal_safe(pos):
                    gridX, gridY = util.posToGrid(pos)
                    return safe_map[gridX][gridY]
                actions = search.bfs(state.game_map, playerPos, __internal_safe)
                if actions:
                    move = actions[0]

        if not state.moveValidForMe(move):
            if not validMoves:
                print('Error: no valid moves')
                return
            move = random.choice(validMoves)

        self.lastMove = move

        self.goMove(player, move)
