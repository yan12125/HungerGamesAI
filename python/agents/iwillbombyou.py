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
        self.runFlag = 0

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
            if player.speed < 9 or player.bombLimit < 5 or player.bombPower < 6:
                return False
            else:
                return True

        moveLenth = state.tryBombAndRun(playerPos, player.bombPower)
        bombTime = state.findBombTime(playerPos)
        if  moveLenth != 0 and\
            (not state.bombThing(playerPos, Grid.TOOL) or __judgeStrong(player)) and\
            (state.bombPlayer(playerPos) or state.bombThing(playerPos, Grid.VWALL))and\
            bombTime > 0.2 and myMap.wayAroundPos(playerPos) > 2:
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
            return

        distance = Direction.distances[move]
        coorX = player.x + distance[0] * player.speed
        coorY = player.y + distance[1] * player.speed
        coorPos = util.coordToPos(coorX, coorY)
        coorGridX, coorGridY = util.posToGrid(coorPos)
        if not Map.gridInMap(gridX, gridY):
            move = random.choice(validMoves)
            distance = Direction.distances[move]
            coorX = player.x + distance[0] * player.speed
            coorY = player.y + distance[1] * player.speed
            coorPos = util.coordToPos(coorX, coorY)
        bombTime1 = state.findBombTime(coorPos)
        bombTime2 = state.findBombTime(playerPos)
        bombTime = min(bombTime1, bombTime2)
        judgePass = ((bombTime - 0.2) * player.speed / util.BASE_INTERVAL  > moveLenth * util.grid_dimension)
        if not judgePass or self.runFlag != 0 or (myMap.wayAroundPos(playerPos) < 3 and not player.penetrate):

            if not judgePass:
                self.runFlag = 2
                actions = search.bfs(myMap, playerPos, __internal_safe, Player = player)
            elif myMap.wayAroundPos(playerPos) < 3:
                self.runFlag = 1
                actions = search.bfs(myMap, playerPos, __internal_safe, Player = player, N = 2)
            if actions:
                move = actions[0]
            elif self.runFlag == 2:
                if safe_map[gridX][gridY]:
                    print "lala"
                    return

        if self.runFlag == 1 and myMap.wayAroundPos(playerPos) > 2:
            self.runFlag = 0
        elif self.runFlag == 2 and myMap.safeMapAround(playerPos) and bombTime > 0.2:
            self.runFlag = 0

        if not state.moveValidForMe(move):
            distance = Direction.distances[self.lastMove]
            newX = gridX + distance[0]
            newY = gridY + distance[1]
            newP = util.gridToPos(newX, newY)
            if Map.gridInMap(newX, newY) and myMap.grids[newP].canPass():
                centerX, centerY = util.posToCoord(playerPos)
                player.x = centerX
                player.y = centerY
            else:
                move = random.choice(validMoves)
        self.lastMove = move
        self.goMove(player, move)
