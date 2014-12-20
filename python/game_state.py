from game_map import Map
from player import Player
from direction import Direction


class GameState(object):
    game_started = False
    game_map = Map()
    players = {}

    def __init__(self):
        pass

    def dump_players(self):
        for player_id, player in self.players.items():
            print(player)

    def add_player(self, player_id, name):
        self.players[player_id] = Player(player_id, name)

    def me(self):
        return self.players[Player.thisPlayer_id]

    def moveValidForPlayer(self, player_id, move):
        player = self.players[player_id]
        move_distance = Direction.distances[move]
        newX = player.x + move_distance[0] * player.speed
        newY = player.y + move_distance[1] * player.speed
        if not self.game_map.coordInMap(newX, newY):
            return False
        if player.penetrate:
            return True
        else:
            return not self.game_map.near(newX, newY, 25)

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
