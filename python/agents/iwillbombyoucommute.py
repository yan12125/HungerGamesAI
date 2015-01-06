import random
import search
import util
from direction import oppDirection, Direction
from .agent import Agent
from grid import Grid
from game_map import Map
from .commuteidle import CommuteidleAgent 
from copy import deepcopy

class IwillbombyoucommuteAgent(CommuteidleAgent):
    def __init__(self):
        super(IwillbombyoucommuteAgent, self).__init__()
        self.lastMove = Direction.UP
        self.lastAdvice = Direction.UP
        self.goalPos = None
    def coordinate(self,state,friendId):
        putBomb=False
        myID=state.me().thisPlayer_id
        player = state.players[friendId]
        myMap = state.game_map
        safe_map = myMap.safeMap()
        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)                
        move = self.lastMove
        if not state.moveValidForPlayer(friendId,move):
            validMoves = state.validMovesForPlayer(friendId)
            if Direction.STOP in validMoves:
                # Not always true. Eg., on a newly put bomb
                validMoves.remove(Direction.STOP)
            if not validMoves:
                print('Error: no valid moves')
                return
            move = random.choice(validMoves)
 




        def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY]
        def __findPlayer(pos):
            return state.posHasPlayer(pos,friendId)
        def __findTool(pos):
            return myMap.gridIs(pos, Grid.TOOL) and myMap.grids[pos].tool != 2 and pos != playerPos
        def __findMiddleTool(pos):
            return myMap.grids[pos].tool != 2

        def __judgeStrong(player):
            if player.speed < 7 or player.bombLimit < 4 or player.bombPower < 4:
                return False
            else:
                return True

        def __meCriteria(p):
            return p == player
        def __othersCriteria(p):
            return p != player
        def __trueCriteria(p):
            return True

        runActions = state.tryBombConsiderOthers(__trueCriteria,friendId)
        moveLenth = runActions[0]
        bombTime = state.findMinBombTime()
        bombTime -= 0.5
        judgePass = bombTime * player.speed / util.BASE_INTERVAL - moveLenth* util.grid_dimension
        if  (not state.bombThing(playerPos, Grid.TOOL) or __judgeStrong(player)) and\
            (state.bombPlayer(playerPos,friendId) or state.bombThing(playerPos, Grid.VWALL))and\
            myMap.grids[playerPos].canPass()and \
            judgePass > 0 and not state.bombMyFriend(playerPos,friendID=state.me().thisPlayer_id):
            putBomb=True


        if self.goalPos != None and putBomb == False:
            if (not state.bombThing(playerPos, Grid.TOOL) or __judgeStrong(player)) and\
            (state.bombPlayer(playerPos,friendId) or state.bombThing(playerPos, Grid.VWALL) or state.bombNearPlayer(playerPos,friendId,self.goalPos))and myMap.grids[playerPos].canPass() and judgePass > 0:
              putBomb=True

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

        if not state.moveValidForPlayer(friendId,move):
            distance = Direction.distances[move]
            destPos = util.gridToPos(gridX + distance[0], gridY + distance[1])

            def __toGrid(coord):
                return destPos == util.coordToPos(*coord)

            startCoord = (player.x, player.y)
            print startCoord
            actions = search.bfsPixel(state.game_map, startCoord, __toGrid, Player=player)
            if actions:
                move = actions[0]
                print move
            else:
                print("Can't reach dest grid")
                return

            if not state.moveValidForPlayer(friendId,move):
                return

        #print("JudgePass: %s, Action: %s, Move: %s" %(judgePass, actions, move))
        self.lastAdvice = move
        self.sendAdviceFriend(myID,friendId,str((move,putBomb)),str(self.goalPos))

    def once(self, state):
        if not util.packet_queue.empty():
            return
        player = state.me()
        self.checkNone(player)
#        print player.friendId
        self.checkValidId(player.friendId,state)
        if player.friendId:
          friendId=player.friendId[0]
          self.coordinate(state,friendId)
          self.hasFriend=True
        else:
          self.hasFriend=False
#          return 

        move = self.lastMove
        myMap = state.game_map
        safe_map = myMap.safeMap()
        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)

        if not state.moveValidForMe(move):
            validMoves = state.validMovesForMe()
            if Direction.STOP in validMoves:
                # Not always true. Eg., on a newly put bomb
                validMoves.remove(Direction.STOP)
            if not validMoves:
                print('Error: no valid moves')
                return
            if player.goalPos == None:
              move = random.choice(validMoves)
            else:
              self.goalPos=None
              print "\n\n\n\nGoFindPlayer\n\n\n\n"
              dis = float("INF")
              goalCoord = util.posToCoord(player.goalPos)
              for item in validMoves:
                newCoord = player.newCoord(item)
                tempDis=util.manhattanDistance(goalCoord,newCoord)
                if tempDis<dis: 
                  temp=dis
                  move=item

        ##############
        def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY]
        def __findPlayer(pos):
            if self.hasFriend:
              if state.posHasPlayer(pos,friendID=friendId):
                __findPlayer.PosGeter= pos
                return True
              else:
                return False
            else :
              if state.posHasPlayer(pos):
                __findPlayer.PosGeter = pos
#                print pos
                return True    
              else:
                return False
        __findPlayer.PosGeter = None
        def __findTool(pos):
            return myMap.gridIs(pos, Grid.TOOL) and myMap.grids[pos].tool != 2 and pos != playerPos
        def __findMiddleTool(pos):
            return myMap.grids[pos].tool != 2

        def __judgeStrong(player):
            if player.speed < 7 or player.bombLimit < 4 or player.bombPower < 3:
                return False
            else:
                return True

        def __meCriteria(p):
            return p == player
        def __othersCriteria(p):
            if self.hasFriend:
              return p!=player and p!=state.players[friendId]
            return p != player
        def __trueCriteria(p):
            return True
        if player.friendId:
          runActions = state.tryBombConsiderOthers(__trueCriteria)
        else:
          runActions = state.tryBombConsiderOthers(__trueCriteria)
        moveLenth = runActions[0]
        bombTime = state.findMinBombTime()
        bombTime -= 0.7
        judgePass = bombTime * player.speed / util.BASE_INTERVAL - moveLenth* util.grid_dimension
        if not self.hasFriend:
          friendId=state.me().thisPlayer_id
        print state.bombMyFriend(playerPos,friendID=friendId)
        if  (not state.bombThing(playerPos, Grid.TOOL) or __judgeStrong(player)) and\
            (state.bombPlayer(playerPos,friendID=friendId) or state.bombThing(playerPos, Grid.VWALL))and\
            myMap.grids[playerPos].canPass() and \
            judgePass > 0 and not state.bombMyFriend(playerPos,friendID=friendId):
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

