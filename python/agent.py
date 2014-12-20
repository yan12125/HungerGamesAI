import random
import util
from direction import Direction


class RandomAgent(object):
    lastMove = Direction.STOP

    def once(self, state):
        player = state.me()

        move = self.lastMove

        if move == Direction.STOP or not state.moveValidForMe(move):
            validMoves = state.validMovesForMe()
            validMoves.remove(Direction.STOP)
            self.lastMove = move = random.choice(validMoves)

        if move == Direction.STOP:
            return

        distance = Direction.distances[move]

        player.x += distance[0] * player.speed
        player.y += distance[1] * player.speed

        util.packet_queue.put({
            'event': 'player_position',
            'x': player.x,
            'y': player.y
        })