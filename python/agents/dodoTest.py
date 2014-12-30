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

    def once(self, state):
        if not util.packet_queue.empty():
            return
        player = state.me()
        legalMoves=state.validMovesForMe()
        if Direction.STOP in legalMoves:
            # Not always true. Eg., on a newly put bomb
            legalMoves.remove(Direction.STOP)

        scores=[self.EvaluationFunction(state,action) for action in legalMoves]
        print scores, legalMoves
        bestScore=max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)
#        chosenIndex = bestIndices[0]
        self.goMove(player,legalMoves[chosenIndex])
        self.lastMove=legalMoves[chosenIndex]
#        print legalMoves[chosenIndex]
        return 
    def EvaluationFunction(self,state,action):
      score = 0.0
      successorGameState=state.generateSuccessor(Player.thisPlayer_id, action, bombPut=False)
      player=state.me()
      newPlayer=successorGameState.me()
      newPos = successorGameState.getPlayerPosition(Player.thisPlayer_id)
      newPosXY = util.coordToGrid(newPos[0],newPos[1])
      Pos = state.getPlayerPosition(Player.thisPlayer_id)
      PosXY = util.coordToGrid(Pos[0],Pos[1])
      newGridPos=util.coordToPos(newPos[0],newPos[1])
      newGridPosXY=util.posToGrid(newGridPos)
#      print newGridPosXY
      print PosXY, action, newGridPosXY

      if state.game_map.gridIs(newGridPos, Grid.TOOL):
        score +=100.0
      def __findTool(pos):
        if successorGameState.game_map.gridIs(pos,Grid.TOOL):
           print util.posToGrid(pos), successorGameState.game_map.grids[pos].tool
        return successorGameState.game_map.gridIs(pos,Grid.TOOL)
#      print newGridPosXY
      count=search.bfs_count(successorGameState.game_map, newGridPos, __findTool)
#      print count
      score -= 0.5*count
##Move to centerX,centerY
      print util.gridToCoord(newPosXY[0],newPosXY[1]),(newPlayer.x,newPlayer.y)
      score -= 0.0001*util.manhattanDistance(util.gridToCoord(newPosXY[0],newPosXY[1]),(newPlayer.x,newPlayer.y))
      if action==self.lastMove:
        score+=50

      return score
   




      '''
        safe_map = state.game_map.safeMap()
          
        self.tryPutBomb(state, player)
        playerPos = util.coordToPos(player.x, player.y)
        gridX, gridY = util.posToGrid(playerPos)
#        if safe_map[gridX][gridY]:
#            return

        def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safe_map[gridX][gridY]
#        actions = search.bfs(state.game_map, playerPos, __internal_safe,1)
        actions = self.getLegalMoveMe(state)
#####        print actions
#        move = actions[0]
###
        others = state.others()
        if not len(others)==0: 
          tempValue=float("inf")
          actionTemp = actions[0]
          for action in actions:
            distance=util.manhattanDistance(player.newCoord(action),\
              (others[0].x,others[0].y)) 
            if distance < tempValue:
              tempValue=distance
              actionTemp=action
        move = actionTemp
#        print move
##
        if state.moveValidForMe(move):
            self.goMove(player, move)
        else:
            # If unable to go to specified pos now, go to current center first
            centerX, centerY = util.posToCoord(playerPos)
            dx, dy = (centerX - player.x, centerY - player.y)
           rself.goMove(player, Direction.byDistance(dx, dy))
      '''
