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
#        self.bombGrid=[]

    def once(self, state):
        if not util.packet_queue.empty():
            return
        player = state.me()
        legalMoves=state.validMovesForMe()
        safe_map = state.game_map.safeMap()
        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)
        bombTime = state.findMinBombTime()
        print state.game_map.wayAroundPos(playerPos,player)

        if ((not safe_map[gridX][gridY]) and bombTime<=2.2) or (state.game_map.wayAroundPos(playerPos,player)==0 and  bombTime<=2.5):
          print "save"
          def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY]
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
        if self.threshingDetectNum>35:
          self.threshingDetect=True 
        if self.threshingDetect and self.threshingDetectNum<20:
          self.threshingDetectNum=0
          self.threshingDetect=False
        if self.threshingDetect:
          print "tesst"
          self.goMove(player,random.choice(legalMoves))
          self.threshingDetectNum -= 1
#          print self.threshingDetect, self.threshingDetectNum
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
                
#        if util.coordToPos(player.x,player.y) == util.coordToPos(player.newCoord(legalMoves[chosenIndex])[0],player.newCoord(legalMoves[chosenIndex])[1]):
#          self.threshingDetectNum+=1 
#        else:
#          self.threshingDetectNum=0
#          self.threshingDetect=False
#        if (not safe_map[gridX][gridY])and bombTime<=0.5:
#            self.threshingDetectNum+=10
        print("Speed: %s, Limit: %s, Count: %s, Power: %s"\
                %(player.speed, player.bombLimit, player.bombCount, player.bombPower))

        distance = Direction.distances[action]
        newGridPosXY=(gridX+distance[0],gridY+distance[1])
        self.goMove(player,legalMoves[chosenIndex])
        self.lastMove=legalMoves[chosenIndex]
        if scores[chosenIndex][1]==True :
#          and util.coordToGrid(player.x,player.y)==newGridPosXY:
          self.tryPutBomb(state, player)
          return 
#        print legalMoves[chosenIndex]

        return 
    def EvaluationFunction(self,state,action):
      myMap = state.game_map
      safe_map = myMap.safeMap()
      numberofIt=50
      putBomb=False
      score = 0.0
      successorGameState=state.generateSuccessor(Player.thisPlayer_id, action, bombPut=True)
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
      bombTime = state.findMinBombTime()
      
      otherplayers=state.others()
      newOtherPlayers=successorGameState.others()

      
#############Find Tool Method################

      def __findTool(pos):
        return successorGameState.game_map.gridIs(pos,Grid.TOOL)


      count=search.bfs_count(state.game_map, newGridPos, __findTool, numberofIt)
      ###IF No Tool Found Try put some bomb#########
      if ((count>=numberofIt+50 and state.game_map.safeMapAroundPos(newGridPos))or \
          (count>=numberofIt+50 and successorGameState.bombPlayer(newGridPos))):
#and safe_map[newGridPosXY[0]][newGridPosXY[1]]:
        if  successorGameState.bombPlayer(newGridPos):
          score+=5000
        if (not state.game_map.gridIs(newGridPos, Grid.TOOL))and state.bombThing(newGridPos,Grid.VWALL):
          putBomb=True
#        else:
#          self.threshingDetectNum+=9
#      print count, action
      if state.game_map.gridIs(newGridPos, Grid.TOOL):
        if player.speed >=7 and state.game_map.grids[newGridPos]==2:
          score -= 10000 
        score +=5000.0
      else:
        score -= 300*count
###############Start Hunting other Player################

      if player.bombLimit>=3 and player.bombPower>=4:
         print "HunterMode"
         def __findPlayer(pos):
            return successorGameState.posHasPlayer(pos)        
         WayOut=[]
         newWayOut=[]
         for otherPlayer in otherplayers:
           tempPos = state.getPlayerPosition(otherPlayer.player_id)
           tempGridPos=util.coordToPos(tempPos[0],tempPos[1]) 
           WayOut.append( state.game_map.moreWayAroundPos(tempGridPos,otherPlayer) )
         for newOtherPlayer in newOtherPlayers:
           tempPos = successorGameState.getPlayerPosition(newOtherPlayer.player_id)
           tempGridPos=util.coordToPos(tempPos[0],tempPos[1]) 
           newWayOut.append(successorGameState.game_map.moreWayAroundPos(tempGridPos,newOtherPlayer))
#         print newWayOut, WayOut
         diff = min([a-b for a,b in zip(newWayOut,WayOut)])
#         print diff



         count_Player=search.bfs_count(successorGameState.game_map, newGridPos,__findPlayer,40)
         if count_Player <= 40:
#            print "tureHunter"
            if count_Player!=0:
              score += 1000*1.0/count_Player
         if (successorGameState.bombPlayer(GridPos) or count_Player<=5) and\
            ((state.game_map.wayAroundPos(GridPos,player)>=2 or safe_map[PosXY[0]][PosXY[1]] )and\
            count_Player<=7) and \
            diff <0 :
            putBomb=True

#        score -= 80*util.manhattanDistance(otherPlayerCorXY,newPos)
#        print util.manhattanDistance(otherPlayerCorXY,newPos), "test"
##Move to centerX,centerY
#      print (newGridCenterXY[0],newGridCenterXY[1]),player.newCoord(action)
#      score -= 0.01*util.manhattanDistance((newGridCenterXY[0],newGridCenterXY[1]),player.newCoord(action))
#################Weight up the consistency###############
      if action==self.lastMove:
        score+=100+self.lastMoveCounter*50
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
      if not safe_map[newGridPosXY[0]][newGridPosXY[1]] and \
            (bombTime <= 2 or state.game_map.wayAroundPos(GridPos,player)<=2):
        def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY]
        count2=search.bfs_count(successorGameState.game_map, newGridPos, __internal_safe,1)
        score -= 100000
        score -= 1000*count2
      if putBomb==True:
          score+=10*successorGameState.game_map.wayAroundPos(newGridPos,player)   
#      putBomb=False

      return score, putBomb
   




