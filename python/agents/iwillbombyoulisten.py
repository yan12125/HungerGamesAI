import random
import search
import util
from direction import oppDirection, Direction
from .agent import Agent
from grid import Grid
from game_map import Map
from .commuteidle import CommuteidleAgent 
from copy import deepcopy

class IwillbombyoulistenAgent(CommuteidleAgent):
    def __init__(self):
        super(IwillbombyoulistenAgent, self).__init__()
        self.lastMove = Direction.UP
        self.lastAdvice = Direction.UP
        self.goalPos = None
    def listen(self,state,friendId):
       if not state.me().MoveAdvice:
         myID=state.me().thisPlayer_id
         self.registerFriend(myID,friendId,str(self.goalPos))

    def once(self, state):
        if not util.packet_queue.empty():
            return
        player = state.me()
        if player.goalPos != None :
          print player.goalPos,"\n\n\n\n"
        myMap = state.game_map
        safe_map = myMap.safeMap()
        move = self.lastMove
        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)
        self.checkNone(player)
#        print player.friendId
        self.checkValidId(player.friendId,state)
        bombTime = state.findMinBombTime()
        if player.friendId:
          friendId=player.friendId[0]
          self.listen(state,friendId)
          if friendId!= "None":
            self.hasFriend=True

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

        moveLenth = state.tryBombConsiderOthers(__trueCriteria)
        if player.bombCount > 4:
            bombTime -= 1.0
        else:
            bombTime -=0.5
        judgePass = bombTime * player.speed / util.BASE_INTERVAL - moveLenth[0] * util.grid_dimension
        if not self.hasFriend:
          friendID=deepcopy(state.me().thisPlayer_id)
        if  moveLenth[0] != util.map_dimension ** 2 and\
            (not state.bombThing(playerPos, Grid.TOOL) or __judgeStrong(player)) and\
            (state.bombPlayer(playerPos,friendID=friendId) or state.bombThing(playerPos, Grid.VWALL))and\
            judgePass > 0:

            if player.MoveAdvice:
              if self.ActByAdvice(state,player):
                  return
              else:
                player.MoveAdvice=[]  
            self.tryPutBomb(state, player)
        if not __judgeStrong(player):
            actions = search.bfs(myMap, playerPos, __findTool, __findMiddleTool, player)
            if actions:
                move = actions[0]
        else:
            actions = search.bfs(myMap, playerPos, __findPlayer, __findMiddleTool, player)
            if player.goalPos == None:
                print "\n\n\n\n", self.goalPos
                self.goalPos = __findPlayer.PosGeter
            if actions:
                move = actions[0]

        if judgePass < 0:
            if moveLenth[0] == util.map_dimension ** 2:
                actions = search.bfs(myMap, playerPos, __internal_safe, Player = player)
            else:
                actions = state.tryBombConsiderOthers(__othersCriteria)[1]

            if actions:
                move = actions[0]
            else:
                return

        print("Speed: %s, Limit: %s, Count: %s, Power: %s"\
        %(player.speed, player.bombLimit, player.bombCount, player.bombPower))
        print("JudgePass: %s, Action: %s, Move: %s" %(judgePass, actions, move))

        if not state.moveValidForMe(move) and judgePass > 0:
            centerX, centerY = util.posToCoord(playerPos)
            player.x = centerX
            player.y = centerY
            validMoves = state.validMovesForMe()
            if Direction.STOP in validMoves:
                # Not always true. Eg., on a newly put bomb
                validMoves.remove(Direction.STOP)
            if not validMoves:
                print('Error: no valid moves')
                return
            if validMoves:
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
                  
        distance = Direction.distances[move]
        gridX, gridY = util.coordToGrid(player.x, player.y)
        newX = gridX + distance[0]
        newY = gridY + distance[1]
        newP = util.gridToPos(newX, newY)
        if (myMap.wayAroundPos(newP, player) == 0) and judgePass > 0:
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
