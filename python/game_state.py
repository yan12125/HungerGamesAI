from game_map import Map
from player import Player
from direction import Direction
from grid import Grid
import util


class GameState(object):
    # Static
    current = None

    def __init__(self):
        self.game_started = False
        self.game_map = Map()
        self.players = {}

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

    def posHasPlayer(self, pos):
        if util.DEBUG:
            playerPositions = []

        for player_id, player in self.players.items():
            playerPos = util.coordToPos(player.x, player.y)

            if util.DEBUG:
                playerPositions.append(playerPos)

            if pos == playerPos and player != self.me():
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
                    __markAsBomb(newX, newY)
        for play_id, player in self.players.items():
            gridX, gridY = util.coordToGrid(player.x, player.y)
            if bomb_map[gridX][gridY] and player != me:
                return True
        return False

    def bombWall(self, pos):
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
                        if self.game_map.gridIs(pos, Grid.VWALL):
                            return True
        return False

    def checkLeave(self, pos):
        # Only myself requires checking. Each client handles himself/herself
        player = self.me()
        if self.game_map.grids[pos].grid_type != Grid.BOMB:
            # XXX I don't know why bombs vanished
            print('Bomb at %s vanished' % util.gridStr(pos))
            return

        if self.game_map.nearPos(player.x, player.y, pos):
            # print("I am on a bomb")
            player.onBomb = True
            util.loop.add_timed_task(util.BASE_INTERVAL, self.checkLeave, pos)
        else:
            print("I exit a bomb")
            player.onBomb = False

    def checkLeaveWall(self):
        player = self.me()
        if self.game_map.near(player.x, player.y, passBomb=player.onBomb):
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
        return not self.game_map.near(newX, newY, p.onBomb, p.penetrate)

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
