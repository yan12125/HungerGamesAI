import util
import search
from .agent import Agent
from direction import Direction
import random
from player import Player
from grid import Grid

class DodotestAgent(Agent):
    def __init__(self):
        super(DodotestAgent, self).__init__()
        self.lastMove = Direction.UP
        self.lastMoveCounter=6
        self.threshingDetect=False
        self.threshingDetectNum=0

    def once(self, state):
        if not util.packet_queue.empty():
            return
        player = state.me()
        legalMoves=state.validMovesForMe()
        safe_map = state.game_map.safeMap()
        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)

        if not safe_map[gridX][gridY]:
          print "save"
          def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY]
          '''
          outPut=state.game_map.safeMapAround(playerPos)
          if outPut:
            if state.moveValidForMe(self.lastMove)and self.lastMove!=Direction.STOP:
              self.goMove(player,self.lastMove)
              return
            if state.moveValidForMe(outPut[0]):
              self.goMove(player, outPut[0])
              self.lastMove=outPut[0]
              return
          '''
          actions = search.bfs(state.game_map, playerPos, __internal_safe,N=1)
          if actions:
            move = actions[0]
            if state.moveValidForMe(actions[0]):
              self.goMove(player, move)
              return 
            else:
              centerX, centerY = util.posToCoord(playerPos)
              dx, dy = (centerX - player.x, centerY - player.y)
              self.goMove(player, Direction.byDistance(dx, dy))
              return

        if Direction.STOP in legalMoves:
            # Not always true. Eg., on a newly put bomb
            legalMoves.remove(Direction.STOP)
        if self.threshingDetectNum>50:
          self.threshingDetect=True 
        if self.threshingDetect and self.threshingDetectNum<40:
          self.threshingDetectNum=0
          self.threshingDetect=False
        if self.threshingDetect:
          print "tesst"
          self.goMove(player,random.choice(legalMoves))
          self.threshingDetectNum -= 1
          print self.threshingDetect, self.threshingDetectNum
          return 


        scores=[self.EvaluationFunction(state,action) for action in legalMoves]
        print scores, legalMoves
        if not scores: return
        bestScore=max(scores,key=lambda item: item[0])[0]
#        bestScore=max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index][0] == bestScore]
        chosenIndex = random.choice(bestIndices)
#        chosenIndex = bestIndices[0]
#        print legalMoves[chosenIndex]
                
        if util.coordToPos(player.x,player.y) == util.coordToPos(player.newCoord(legalMoves[chosenIndex])[0],player.newCoord(legalMoves[chosenIndex])[1]):
          self.threshingDetectNum+=1
        else:
          self.threshingDetectNum=0

        self.goMove(player,legalMoves[chosenIndex])
        if scores[chosenIndex][1]==True:
          self.tryPutBomb(state, player)
          return 
        self.lastMove=legalMoves[chosenIndex]
#        print legalMoves[chosenIndex]
        return 
    def EvaluationFunction(self,state,action):
      myMap = state.game_map
      safe_map = myMap.safeMap()
      numberofIt=50
      putBomb=False
      score = 0.0
      successorGameState=state.generateSuccessor(Player.thisPlayer_id, action, bombPut=False)
      player=state.me()
      newPlayer=successorGameState.me()
      newPos = successorGameState.getPlayerPosition(Player.thisPlayer_id)
      newPosXY = util.coordToGrid(newPos[0],newPos[1])
      Pos = state.getPlayerPosition(Player.thisPlayer_id)
      GridPos=util.coordToPos(Pos[0],Pos[1])
      PosXY = util.coordToGrid(Pos[0],Pos[1])
      newGridPos=util.coordToPos(newPos[0],newPos[1])
      newGridCenterXY = util.posToCoord(newGridPos)
      newGridPosXY=util.posToGrid(newGridPos)
      
#      otherplayers=successorGameState.others()
#      otherplayer=otherplayers[0]
#      otherPlayerCorXY=successorGameState.getPlayerPosition(otherplayer.player_id)
#      print newGridPosXY
#      print PosXY, action, newGridPosXY

      def __findTool(pos):
#        if successorGameState.game_map.gridIs(pos,Grid.TOOL):
#           print util.posToGrid(pos), successorGameState.game_map.grids[pos].tool
        return successorGameState.game_map.gridIs(pos,Grid.TOOL)
#      print newGridPosXY
      count=search.bfs_count(state.game_map, newGridPos, __findTool,numberofIt)
      if (count>=numberofIt+50 and state.game_map.safeMapAroundPos(newGridPos))or (count>=numberofIt+50 and successorGameState.bombPlayer(newGridPos))and safe_map[newGridPosXY[0]][newGridPosXY[1]]:
        if  successorGameState.bombPlayer(newGridPos):
          score+=5000
        if not state.game_map.gridIs(newGridPos, Grid.TOOL):
          putBomb=True
      print count, action
      if player.bombLimit>=3 and player.bombPower>=3:
         print "HunterMode"
         def __findPlayer(pos):
            return successorGameState.posHasPlayer(pos)        
         count_Player=search.bfs_count(successorGameState.game_map, newGridPos,__findPlayer,40)
         if count_Player <= 40:
            score-=700*count_Player
         if (successorGameState.bombPlayer(GridPos) or count_Player<=5) and (state.game_map.wayAroundPos(GridPos)>=2 or safe_map[PosXY[0]][PosXY[1]]): 
            putBomb=True

#        score -= 80*util.manhattanDistance(otherPlayerCorXY,newPos)
#        print util.manhattanDistance(otherPlayerCorXY,newPos), "test"
      if state.game_map.gridIs(newGridPos, Grid.TOOL):
        score +=5000.0
      else:
        score -= 150*count
##Move to centerX,centerY
#      print (newGridCenterXY[0],newGridCenterXY[1]),player.newCoord(action)
#      score -= 0.01*util.manhattanDistance((newGridCenterXY[0],newGridCenterXY[1]),player.newCoord(action))
      if action==self.lastMove:
        score+=100+self.lastMoveCounter*1000
        self.lastMoveCounter-=3
        if self.lastMoveCounter <0 :
          self.lastMoveCounter=6
#      if PosXY==newGridPosXY:
#        score -= 500
      '''
      if putBomb == True:
        successorGameState=state.generateSuccessor(Player.thisPlayer_id, action, bombPut=True)
        player=state.me()
        newPlayer=successorGameState.me()
        newPos = successorGameState.getPlayerPosition(Player.thisPlayer_id)
        newPosXY = util.coordToGrid(newPos[0],newPos[1])
        Pos = state.getPlayerPosition(Player.thisPlayer_id)
        PosXY = util.coordToGrid(Pos[0],Pos[1])
        newGridPos=util.coordToPos(newPos[0],newPos[1])
        newGridCenterXY = util.posToCoord(newGridPos)
        newGridPosXY=util.posToGrid(newGridPos)
      '''
      if not safe_map[newGridPosXY[0]][newGridPosXY[1]]: 
        def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY]
        count2=search.bfs_count(successorGameState.game_map, newGridPos, __internal_safe,1)
        score -= 100000
        score -= 1000*count2
      if putBomb==True:
          score+=100*successorGameState.game_map.wayAroundPos(newGridPos)   
#      putBomb=False

      return score, putBomb
   




