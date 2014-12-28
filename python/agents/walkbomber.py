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
        def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY]

        player = state.me()

        if not state.moveValidForMe(move):
            self.tryPutBomb(state, player)

        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)
 
        actions = search.bfs(state.game_map, playerPos, __internal_safe)
        if actions:
            move = actions[0]

        validMoves = state.validMovesForMe()
        if Direction.STOP in validMoves:
            # Not always true. Eg., on a newly put bomb
            validMoves.remove(Direction.STOP)
        if not validMoves:
            print('Error: no valid moves')
            return
        
        if not state.moveValidForMe(move):
            move = random.choice(validMoves)

        self.lastMove = move

        self.goMove(player, move)
