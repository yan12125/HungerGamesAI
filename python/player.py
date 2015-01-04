import util
import random
from direction import Direction


class Player(object):
    # Static
    thisPlayer_id = None

    def __init__(self, p_id, p_name):
        self.player_id = p_id
        self.name = p_name

        self.x = -1
        self.y = -1
        self.dead = False
        self.disconnected = False

        # Tools related parameters
        self.preparing = False
        self.speed = 5  # -1 indicated unknown
        self.bombPower = 1
        self.bombLimit = 1
        self.bombCount = 0
        self.penetrate = False  # whether able to bypass walls
        self.god_mod = False  # not killed by bombs

        ##Handle multiAgent

        self.friendId=[]
        self.MoveAdvice=[]

    def RegisterMyFriendId(self,FriendID):
        self.friendId.append(FriendID)
        print("my Friend ID is : %s" % FriendID)
    
    def getMoveFromFriend(self,Move):
        self.MoveAdvice.append(Move)


    def isMe(self):
        return self.player_id == Player.thisPlayer_id

    @staticmethod
    def isMe2(player_id):
        return Player.thisPlayer_id == player_id

    def setPreparing(self):
        self.preparing = True
        print('Player %s is in preparing mode' % self.player_id)

        def __internal_exitPreparing(player):
            player.preparing = False
            print('Player %s exits preparing mode' % player.player_id)

        util.loop.add_timed_task(3, __internal_exitPreparing, self)

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
            if self.isMe():
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
            print("Player %s is penetrate" % self.player_id)
            self.penetrate = True
        elif tooltype == 6:
            pass

    def putBomb(self):
        if self.isMe():
            print("Received my bomb")
            return  # state is handled in agents
        self.bombCount += 1

    def bombed(self):
        if not self.preparing:
            self.dead = True
        if self.isMe():
            util.mark_finished()
        # Connection is closed by the server

    def newCoord(self, move):
        distance = Direction.distances[move]
        newX = self.x + distance[0] * self.speed
        newY = self.y + distance[1] * self.speed
        return (newX, newY)

    def __str__(self):
        ret = 'Player %s "%s"' % (self.player_id, self.name)
        ret += ' at (%d, %d)' % (self.x, self.y)
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
