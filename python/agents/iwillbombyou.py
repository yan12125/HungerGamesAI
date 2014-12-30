import random
import search
import util
from direction import Direction
from .agent import Agent
from grid import Grid
from game_map import Map

class IwillbombyouAgent(Agent):
    def __init__(self):
        super(IwillbombyouAgent, self).__init__()
        self.lastMove = Direction.UP

    def once(self, state):
        if not util.packet_queue.empty():
            return

        move = self.lastMove

        player = state.me()
        myMap = state.game_map
        safe_map = myMap.safeMap()
        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)
        def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY] and myMap.wayAroundPos(pos) > 1
        def __findPlayer(pos):
            return state.posHasPlayer(pos)
        def __findTool(pos):
            return myMap.gridIs(pos, Grid.TOOL)

        if  safe_map[gridX][gridY] and (state.bombPlayer(playerPos) or\
            (state.bombWall(playerPos) and myMap.wayAroundPos(playerPos) > 2)
            or myMap.wayAroundPos(playerPos) == 1):
            self.tryPutBomb(state, player)

        if safe_map[gridX][gridY]:
            actions = search.bfs(myMap, playerPos, __findTool)
            if actions:
                move = actions[0]
            else:
                actions = search.bfs(myMap, playerPos, __findPlayer, __internal_safe)
                if actions:
                    move = actions[0]
            if not state.bombValidForMe(move):
                return
        else:
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
            distance = Direction.distances[self.lastMove]
            newX = gridX + distance[0]
            newY = gridY + distance[1]
            newP = util.gridToPos(newX, newY)
            if Map.gridInMap(newX, newY) and myMap.grids[newP].canPass():
                centerX, centerY = util.posToCoord(newP)
                player.x = centerX
                player.y = centerY
            else:
                move = random.choice(validMoves)

        self.lastMove = move
        self.goMove(player, move)
