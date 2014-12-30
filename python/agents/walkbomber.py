import random
import search
import util
from direction import Direction
from .agent import Agent
from grid import Grid

class WalkbomberAgent(Agent):
    def __init__(self):
        super(WalkbomberAgent, self).__init__()
        self.lastMove = Direction.UP

    def once(self, state):
        if not util.packet_queue.empty():
            return

        move = self.lastMove

        player = state.me()
        safe_map = state.game_map.safeMap()
        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)
        def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY] and state.game_map.wayAroundPos(pos) > 1
        def __findTool(pos):
            return state.game_map.gridIs(pos, Grid.TOOL)

        if state.game_map.safeMapAroundPos(playerPos) and (not state.moveValidForMe(move)\
           or state.game_map.wayAroundPos(playerPos) < 4):
            self.tryPutBomb(state, player)

        if state.game_map.safeMapAroundPos(playerPos):
            actions = search.bfs(state.game_map, playerPos, __findTool)
            if actions:
                move = actions[0]
        else:
            actions = search.bfs(state.game_map, playerPos, __internal_safe)
            if actions:
                move = actions[0]
            if safe_map[gridX][gridY] and not state.bombValidForMe(move):
                return

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
