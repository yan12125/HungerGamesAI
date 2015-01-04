from game_map import Map
from player import Player
from direction import Direction
from grid import Grid
from copy import deepcopy
import util
import time
import search


class GameState(object):
    # Static
    current = None

    def __init__(self, prevState=None):
      if prevState!=None:
         self.game_started=prevState.game_started
         self.game_map=deepcopy(prevState.game_map)
         self.players=deepcopy(prevState.players)
      else:
        self.game_started = False
        self.game_map = Map()
        self.players = {}
    def deepCopy(self):
      state = GameState(self)
      state.game_started = self.game_started
      state.game_map = self.game_map
      state.players = self.players
      return state

    def start_game(self, already_started):
        def __internal_preparing(state):
            print('Game started')
            state.game_started = True
            for player_id, player in self.players.items():
                player.setPreparing()

        if already_started:
            print('Game started immediately')
            __internal_preparing(self)
        else:
            print('Game will start in 3 seconds')
            util.loop.add_timed_task(3, __internal_preparing, self)

    def set_players(self, player_list):
        print('Receive players')

        for playerObj in player_list:
            player_id = playerObj['playerid']

            # Create the player if not exist
            if player_id not in self.players:
                self.add_player(player_id, playerObj['name'])

            # Update info
            player = self.players[player_id]
            player.setCoord(playerObj['x'], playerObj['y'])
            player.updateStatus(playerObj['dead'], playerObj['disconnected'])

        self.dump_players()

    def dump_players(self):
        for player_id, player in self.players.items():
            print(player)

    def add_player(self, player_id, name):
        self.players[player_id] = Player(player_id, name)

    def me(self):
        return self.players[Player.thisPlayer_id]

    def others(self):
        ''' Return a list of other players

        '''
        otherlist=[]
        for item in self.players:
          if item!=Player.thisPlayer_id:
            otherlist.append(self.players[item])
        return otherlist
    def posHasPlayer(self, pos, playerID=None):
        if playerID==None:
          playerID=Player.thisPlayer_id
        if util.DEBUG:
            playerPositions = []

        for player_id, player in self.players.items():
            playerPos = util.coordToPos(player.x, player.y)

            if util.DEBUG:
                playerPositions.append(playerPos)

            if pos == playerPos and player != self.players[playerID]:
                return True

        if util.DEBUG:
            print(playerPositions, pos)

        return False

    def bombPlayer(self, pos):
        me = self.me()
        bomb_map = util.linearGridToMap([False for i in util.grid_gen])

        def __markAsBomb(gridX, gridY):
            if not Map.gridInMap(gridX, gridY):
                return
            bomb_map[gridX][gridY] = True

        gridX, gridY = util.posToGrid(pos)
        for direction in Direction.ALL:
            if direction == Direction.STOP:
                __markAsBomb(gridX, gridY)
            else:
                for i in range(0, me.bombPower):
                    distance = Direction.distances[direction]
                    newX = gridX + distance[0] * (i+1)
                    newY = gridY + distance[1] * (i+1)
                    newP = util.gridToPos(newX, newY)
                    if Map.gridInMap(newX, newY) and self.game_map.gridIs(newP, Grid.NVWALL):
                        break
                    __markAsBomb(newX, newY)
        for play_id, player in self.players.items():
            gridX, gridY = util.coordToGrid(player.x, player.y)
            if bomb_map[gridX][gridY] and player.player_id != me.player_id:
                return True
        return False

    def bombThing(self, pos, kind):
        me = self.me()

        gridX, gridY = util.posToGrid(pos)
        for direction in Direction.ALL:
            if direction != Direction.STOP:
                for i in range(0, me.bombPower):
                    distance = Direction.distances[direction]
                    newX = gridX + distance[0] * (i+1)
                    newY = gridY + distance[1] * (i+1)
                    pos = util.gridToPos(newX, newY)
                    if Map.gridInMap(newX, newY):
                        if self.game_map.gridIs(pos, kind):
                            return True
                        elif self.game_map.gridIs(pos, Grid.NVWALL):
                            break
                    else:
                        break
        return False

    def findBombTime(self, pos):
        bombTime = 0

        gridX, gridY = util.posToGrid(pos)
        for direction in Direction.ALL:
            if direction != Direction.STOP:
                for i in range(0, util.map_dimension):
                    distance = Direction.distances[direction]
                    newX = gridX + distance[0] * (i+1)
                    newY = gridY + distance[1] * (i+1)
                    pos = util.gridToPos(newX, newY)
                    if Map.gridInMap(newX, newY):
                        if self.game_map.gridIs(pos, Grid.BOMB):
                            bombTime = max(bombTime, time.time() - self.game_map.grids[pos].bombPutTime)
                        elif self.game_map.gridIs(pos, Grid.NVWALL):
                            break
                    else:
                        break
        return (Grid.BOMB_DELAY - bombTime)

    def findMinBombTime(self):
        bombTime = 0.0
        for i, grid in self.game_map.bombsGen():
            bombTime = max(bombTime, time.time() - grid.bombPutTime)
        return (Grid.BOMB_DELAY - bombTime)

    def tryBombConsiderOthers(self, criteria,playid = None):
        if playid == None:
          playid=deepcopy(Player.thisPlayer_id)
        safeMap = util.linearGridToMap([True for i in util.grid_gen])
        gameMap = deepcopy(self.game_map)
        bombs = list(self.game_map.bombsGen())

        def __markAsUnsafe(gridX, gridY):
            if not Map.gridInMap(gridX, gridY):
                return
            safeMap[gridX][gridY] = False

        def __internal_safe(pos):
            gridX, gridY = util.posToGrid(pos)
            return safeMap[gridX][gridY]

        for player_id, player in self.players.items():
            if criteria(player):
                gridX, gridY = util.coordToGrid(player.x, player.y)
                pos = util.coordToPos(player.x, player.y)
                grid = Grid()
                grid.bombPower = player.bombPower
                grid.grid_type = grid.BOMB
                grid.bombPutTime = time.time()
                bombs.append((pos, grid))
                gameMap.grids[pos] = grid

        for i, grid in bombs:
            gridX, gridY = util.posToGrid(i)
            for direction in Direction.ALL:
                if direction == Direction.STOP:
                    __markAsUnsafe(gridX, gridY)
                else:
                    for i in range(0, grid.bombPower):
                        distance = Direction.distances[direction]
                        newX = gridX + distance[0] * (i+1)
                        newY = gridY + distance[1] * (i+1)
                        newP = util.gridToPos(newX, newY)
                        if Map.gridInMap(newX, newY) and gameMap.gridIs(newP, Grid.NVWALL):
                            break
                        __markAsUnsafe(newX, newY)

        me = self.players[playid]
        startPos = util.coordToPos(me.x, me.y)
        path = search.bfs(gameMap, startPos, __internal_safe, Player = me)
        if path:
            return (len(path), path)
        else:
            return (util.map_dimension ** 2, path)

    def checkLeave(self, pos):
        # Only myself requires checking. Each client handles himself/herself
        player = self.me()
        self.checkLeavePlayer(player, pos)

    def checkLeavePlayer(self, player, pos):
        gridAtPos = self.game_map.grids[pos]

        if gridAtPos.grid_type != Grid.BOMB:
            # XXX I don't know why bombs vanished
            print('Bomb at %s vanished' % util.gridStr(pos))
            return

        playerPos = util.coordToPos(player.x, player.y)
        if self.game_map.nearPos(player.x, player.y, pos):
            # print("I am on a bomb")
            gridAtPos.canPassBomb = True
            util.loop.add_timed_task(util.BASE_INTERVAL, self.checkLeave, pos)
        elif self.game_map.grids[playerPos] != Grid.BOMB and player.penetrate == False:
            print("I exit the bomb at %s" % util.gridStr(pos))
            gridAtPos.canPassBomb = False

    def checkLeaveWall(self):
        player = self.me()
        if self.game_map.near(player.x, player.y):
            print("Still in some wall")
            util.loop.add_timed_task(util.BASE_INTERVAL, self.checkLeaveWall)
        else:
            print("Dropping UFO")
            player.penetrate = False
            util.packet_queue.put({
                'event': 'ufo_removal',
                'playerid': Player.thisPlayer_id
            })

    def moveValidForPlayer(self, player_id, move):
        p = self.players[player_id]
        move_distance = Direction.distances[move]
        newX = p.x + move_distance[0] * p.speed
        newY = p.y + move_distance[1] * p.speed
        return not self.game_map.near(newX, newY, p.penetrate)

    def moveValidForMe(self, move):
        return self.moveValidForPlayer(Player.thisPlayer_id, move)

    def validMovesForPlayer(self, player_id):
        ret = []
        for move in Direction.ALL:
            if self.moveValidForPlayer(player_id, move):
                ret.append(move)

        return ret

    def validMovesForMe(self):
        return self.validMovesForPlayer(Player.thisPlayer_id)

    def moveGoodForPlayer(self, player_id, move):
        if not self.moveValidForPlayer(player_id, move):
            return False

        player = self.players[player_id]
        playerGrid = list(util.coordToGrid(player.x, player.y))

        distance = Direction.distances[move]
        playerGrid[0] += distance[0]
        playerGrid[1] += distance[1]

        if not Map.gridInMap(*playerGrid):
            return False

        grid = self.game_map.grids[util.gridToPos(*playerGrid)]
        return grid.canPass()

    def moveGoodForMe(self, move):
        return self.moveGoodForPlayer(Player.thisPlayer_id, move)

    def goodMovesForPlayer(self, player_id):
        ret = []
        for move in Direction.ALL:
            if self.moveGoodForPlayer(player_id, move):
                ret.append(move)
        return ret

    def goodMovesForMe(self):
        return self.goodMovesForPlayer(Player.thisPlayer_id)

    def bombValidForPlayer(self, player_id, move):
        safe_map = self.game_map.safeMap()

        p = self.players[player_id]
        move_distance = Direction.distances[move]
        newX = p.x + move_distance[0] * p.speed
        newY = p.y + move_distance[1] * p.speed
        gridX, gridY = util.coordToGrid(newX, newY)
        return safe_map[gridX][gridY]

    def bombValidForMe(self, move):
        return self.bombValidForPlayer(Player.thisPlayer_id, move)

    def validBombForPlayer(self, player_id):
        ret = []
        for move in Direction.ALL:
            if self.bombValidForPlayer(player_id, move):
                ret.append(move)

        return ret

    def validBombForMe(self):
        return self.validbombForPlayer(Player.thisPlayer_id)

    def getMePosition(self): 
        return (self.me().x,self.me().y)  

    def getPlayerPosition(self,PlayerID):
        return (self.players[PlayerID].x, self.players[PlayerID].y)

    def generateSuccessor( self, agentID, action, bombPut=False):
      """
      Returns the successor state after the specified agent takes the action.
      """
      state = GameState(self)
      Pos = state.getPlayerPosition(agentID)
      GridPos=util.coordToPos(Pos[0],Pos[1])
      GridPosXY=util.posToGrid(GridPos)
      grid = state.game_map.grids[GridPos]
      player = state.players[agentID]
      if action!=Direction.STOP:
        distance = Direction.distances[action]
        newGridPosXY = (GridPosXY[0]+distance[0],\
                        GridPosXY[1]+distance[1])
      else: newGridPosXY=GridPosXY
      newCorXY =  util.gridToCoord(newGridPosXY[0],newGridPosXY[1])
      if state.game_map.near(newCorXY[0],newCorXY[1], player.penetrate):
         return state
      newGridPos=util.gridToPos(newGridPosXY[0],newGridPosXY[1])
      newGrid = state.game_map.grids[newGridPos]
      game_map = state.game_map
###Need TO Check more###############
##Eat Bomb ##
#        for playerItem in state.players:
#          self.checkLeavePlayer(playerItem,GridPos)
#        return state
####################################
##PLayer move##
      player.x , player.y = util.gridToCoord(newGridPosXY[0],newGridPosXY[1])
      if bombPut== True : 
        state.game_map.bombPut(GridPosXY[0],GridPosXY[1],player.bombPower)
#        player.putBomb()
##Player Eat TOOL##
      if state.game_map.gridIs(newGridPos, Grid.TOOL):
        ##Tool disapear###
        toolname = util.tools_map[newGrid.tool]
        newGrid.grid_type = 'empty'
        newGrid.tool=None
        game_map.dumpGrids()
        ##Tool Apply ###
        notInPenetrate = not player.penetrate
        player.toolapply(newGrid.tool)
##        if grid.tool == 5 and notInPenetrate:  # ufo
##          util.loop.add_timed_task(15, state.checkLeaveWall)


      return state




      
    ######################################################
    ## The following is the private method, you should  ##
    ## not call it from the outside.                    ##
    ######################################################
