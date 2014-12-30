import random
import util
from direction import Direction
from .agent import Agent

class DrunkenAgent(Agent):
    def __init__(self):
        super(DrunkenAgent, self).__init__()

    def once(self, state):
        if not util.packet_queue.empty():
            return

        player = state.me()

        move = self.lastMove

        if move == Direction.STOP or not state.moveValidForMe(move):
            validMoves = state.validMovesForMe()
            if Direction.STOP in validMoves:
                # Not always true. Eg., on a newly put bomb
                validMoves.remove(Direction.STOP)
            if not validMoves:
                print('Error: no valid moves')
                return
            self.lastMove = move = random.choice(validMoves)

        if move == Direction.STOP:
            return

        self.goMove(player, move)
