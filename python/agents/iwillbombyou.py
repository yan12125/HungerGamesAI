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
        if not state.moveValidForMe(move):
            validMoves = state.validMovesForMe()
            if Direction.STOP in validMoves:
                # Not always true. Eg., on a newly put bomb
                validMoves.remove(Direction.STOP)
            if not validMoves:
                print('Error: no valid moves')
                return
            move = random.choice(validMoves)

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

        def __trueCriteria(p):
            return True

        runActions = state.tryBombConsiderOthers(__trueCriteria)
        moveLenth = runActions[0]
        bombTime = state.findMinBombTime()
        bombTime -= 0.5
        judgePass = bombTime * player.speed / util.BASE_INTERVAL - moveLenth * util.grid_dimension

        if  (not state.bombThing(playerPos, Grid.TOOL) or __judgeStrong(player)) and\
            (state.bombPlayer(playerPos) or state.bombThing(playerPos, Grid.VWALL))and\
            myMap.grids[playerPos].canPass() and judgePass > 0:
            self.tryPutBomb(state, player)

        distance = Direction.distances[move]
        gridX, gridY = util.coordToGrid(player.x, player.y)
        newX = gridX + distance[0]
        newY = gridY + distance[1]
        newP = util.gridToPos(newX, newY)

        if judgePass > 0 and myMap.wayAroundPos(newP, player) > 0:
            if not __judgeStrong(player):
                actions = search.bfs(myMap, playerPos, __findTool, __findMiddleTool, player)
                if actions:
                    move = actions[0]
            else:
                actions = search.bfs(myMap, playerPos, __findPlayer, __findMiddleTool, player)
                if actions:
                    move = actions[0]

        if judgePass < 0 or myMap.wayAroundPos(newP, player) == 0:
            actions = search.bfs(myMap, playerPos, __internal_safe, Player = player)
            if actions:
                move = actions[0]
            else:
                return

        #print("Speed: %s, Limit: %s, Count: %s, Power: %s"\
        #%(player.speed, player.bombLimit, player.bombCount, player.bombPower))

        if not state.moveValidForMe(move):
            distance = Direction.distances[move]
            destPos = util.gridToPos(gridX + distance[0], gridY + distance[1])

            def __toGrid(coord):
                return destPos == util.coordToPos(*coord)

            startCoord = (player.x, player.y)
            actions = search.bfsPixel(state.game_map, startCoord, __toGrid, Player=player)
            if actions:
                move = actions[0]
            else:
                print("Can't reach dest grid")
                return

            if not state.moveValidForMe(move):
                raise Exception('Unexpected: move %s should be valid' % move)

        #print("JudgePass: %s, Action: %s, Move: %s" %(judgePass, actions, move))
        self.goMove(player, move)
        self.lastMove = move
