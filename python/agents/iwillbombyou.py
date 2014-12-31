import random
import search
import util
from direction import oppDirection, Direction
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
            return safe_map[gridX][gridY]
        def __findPlayer(pos):
            return state.posHasPlayer(pos)
        def __findTool(pos):
            return myMap.gridIs(pos, Grid.TOOL) and myMap.grids[pos].tool != 2 and pos != playerPos
        def __findMiddleTool(pos):
            return myMap.grids[pos].tool != 2

        def __judgeStrong(player):
            print((player.speed, player.bombLimit, player.bombPower))
            if player.speed < 9 or player.bombLimit < 5 or player.bombPower < 6:
                return False
            else:
                return True

        moveLenth = state.tryBombAndRun(playerPos, player.bombPower)
        bombTime = state.findMinBombTime()
        if  moveLenth != util.map_dimension ** 2 and\
            (not state.bombThing(playerPos, Grid.TOOL) or __judgeStrong(player)) and\
            (state.bombPlayer(playerPos) or state.bombThing(playerPos, Grid.VWALL))and\
            bombTime > 1:
            self.tryPutBomb(state, player)
        if not __judgeStrong(player):
            actions = search.bfs(myMap, playerPos, __findTool, __findMiddleTool, player)
            if actions:
                move = actions[0]
        else:
            actions = search.bfs(myMap, playerPos, __findPlayer, __findMiddleTool, player)
            if actions:
                move = actions[0]

        validMoves = state.validMovesForMe()
        if Direction.STOP in validMoves:
            # Not always true. Eg., on a newly put bomb
            validMoves.remove(Direction.STOP)
        if not validMoves:
            print('Error: no valid moves')

        distance = Direction.distances[move]
        coorX = player.x + distance[0] * player.speed
        coorY = player.y + distance[1] * player.speed
        coorPos = util.coordToPos(coorX, coorY)
        coorGridX, coorGridY = util.posToGrid(coorPos)
        if not Map.gridInMap(gridX, gridY):
            move = oppDirection(move)
            distance = Direction.distances[move]
            coorX = player.x + distance[0] * player.speed
            coorY = player.y + distance[1] * player.speed
            coorPos = util.coordToPos(coorX, coorY)
        actions = search.bfs(myMap, playerPos, __internal_safe, Player = player)
        if actions:
            pathLenth = len(actions)
        else:
            pathLenth = 0
        judgePass = (bombTime - 1.0) * player.speed / util.BASE_INTERVAL - pathLenth * util.grid_dimension
        if judgePass < 0:
            print(actions)
            if actions:
                move = actions[0]
            else:
                return

        if not state.moveValidForMe(move) and judgePass > 0:
            centerX, centerY = util.posToCoord(playerPos)
            player.x = centerX
            player.y = centerY
            move = oppDirection(move)
        distance = Direction.distances[move]
        gridX, gridY = util.coordToGrid(player.x, player.y)
        newX = gridX + distance[0]
        newY = gridY + distance[1]
        newP = util.gridToPos(newX, newY)
        if (myMap.wayAroundPos(newP) == 0) and judgePass > 0:
            for d in Direction.ALL:
                dis = Direction.distances[d]
                nX = gridX + dis[0]
                nY = gridY + dis[1]
                nP = util.gridToPos(nX, nY)
                if myMap.wayAroundPos(nP) > 0:
                    move = d
                    break;
        self.lastMove = move
        self.goMove(player, move)
