import random
import util
from direction import Direction


class DrunkenAgent(object):
    def __init__(self):
        self.lastMove = Direction.STOP

    def once(self, state):
        if not util.packet_queue.empty():
            return

        move = self.lastMove

        if move == Direction.STOP or not state.moveValidForMe(move):
            validMoves = state.validMovesForMe()
            if Direction.STOP in validMoves:
                # Not always true. Eg., on a newly put bomb
                validMoves.remove(Direction.STOP)
            self.lastMove = move = random.choice(validMoves)

        if move == Direction.STOP:
            return

        distance = Direction.distances[move]

        player = state.me()
        player.x += distance[0] * player.speed
        player.y += distance[1] * player.speed

        util.packet_queue.put({
            'event': 'player_position',
            'x': player.x,
            'y': player.y
        })
