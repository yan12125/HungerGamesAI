import util
import random
from task_loop import TaskLoop


class Player(object):
    # Static
    thisPlayer_id = None

    player_id = None
    x = -1
    y = -1
    dead = False
    disconnected = False
    name = None

    # Tools related parameters
    preparing = False
    speed = 5  # -1 indicated unknown
    bombPower = 1
    bombLimit = 5
    bombCount = 0
    penetrate = False  # whether able to bypass walls
    god_mod = False  # not killed by bombs

    def __init__(self, p_id, p_name):
        self.player_id = p_id
        self.name = p_name

    def setPreparing(self):
        self.preparing = True
        print('Player %s is in preparing mode' % self.player_id)

        def __internal(player):
            player.preparing = False
            print('Player %s exits preparing mode' % player.player_id)

        util.loop.add_task(TaskLoop.delay, 3, __internal, self)

    def setPos(self, p_pos):
        """
        Set (x, y) coordinate from 0-based grid position `pos`
        See coordCalc() in server/main.js
        """
        coord = util.posToGrid(p_pos)
        self.setCoord(coord[0] * 60 + 30, coord[1] * 60 + 30)

    def setCoord(self, _x, _y):
        self.x = _x
        self.y = _y

    def updateStatus(self, dead, disconnected):
        """
        Always use named arguments on calling
        """
        self.dead = dead
        self.disconnected = disconnected

    def toolapply(self, tooltype):
        if tooltype == 1:
            if self.speed < 10:
                self.speed += 1
        elif tooltype == 2:
            if Player.thisPlayer_id == self.player_id:
                self.speed = random.randrange(2, 11)  # 2~10
            else:
                self.speed = -1
        elif tooltype == 3:
            if self.bombLimit <= 5:
                self.bombLimit += 1
        elif tooltype == 4:
            if self.bombPower < 7:
                self.bombPower += 1
            pass
        elif tooltype == 5:
            self.penetrate = True
            # TODO Remove ufo after 15 seconds
        elif tooltype == 6:
            pass

    def bombed(self):
        if not self.preparing:
            self.dead = True
        # Connection is closed by the server

    def __str__(self):
        ret = 'Player %s "%s"' % self.player_id, self.name
        ret += ' at (%d, %d)' % self.x, self.y
        ret += ', grid (%d, %d)' % util.coordToGrid(self.x, self.y)
        if self.disconnected:
            ret += ', disconnected'
        if self.dead:
            ret += ', dead'
        return ret

    @staticmethod
    def forAll(players, callback):
        if not callable(callback):
            raise Exception("Callable object required")

        for player_id, player in players.items():
            callback(player_id, player)
