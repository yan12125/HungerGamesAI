from game_map import Map
from player import Player
from direction import Direction
import util


class GameState(object):
    # Static
    current = None

    def __init__(self):
        self.game_started = False
        self.game_map = Map()
        self.players = {}

    def start_game(self, already_started):
        print('Game started')

        self.game_started = True

        def __internal_preparing():
            for player_id, player in self.players.items():
                player.setPreparing()

        if already_started:
            __internal_preparing()
        else:
            util.loop.add_timed_task(3, __internal_preparing)

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

    def checkLeave(self, pos):
        # Only myself requires checking. Each client handles himself/herself
        player = self.me()
        if self.game_map.nearPos(player.x, player.y, pos):
            print("I am on a bomb")
            player.onBomb = True
            util.loop.add_timed_task(util.BASE_INTERVAL, self.checkLeave, pos)
        else:
            print("I exit a bomb")
            player.onBomb = False

    def moveValidForPlayer(self, player_id, move):
        player = self.players[player_id]
        move_distance = Direction.distances[move]
        newX = player.x + move_distance[0] * player.speed
        newY = player.y + move_distance[1] * player.speed
        if not self.game_map.coordInMap(newX, newY):
            return False

        if player.penetrate:
            return True

        return not self.game_map.near(newX, newY, canPassBomb=player.onBomb)

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
