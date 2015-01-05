from .agent import Agent
import util
import random
from direction import Direction


class CommuteidleAgent(Agent):
    def __init__(self):
        super(CommuteidleAgent, self).__init__()
        self.friendId=[]
        self.hasFriend=False
    def ActByAdvice(self,state,player):
      move,putBomb = eval(player.MoveAdvice[0])

      if putBomb:
        self.tryPutBomb(state,player)
      if state.moveValidForMe(move):
        print "Friend Advice",move
        self.goMove(player,move)
        player.MoveAdvice=[]
        return True
      else:
        player.MoveAdvice=[]
        return False

    def sendAdviceFriend(self,myID,friendID,advice,goal=None):
      '''This method implement send message to friend
         send advice (move,PutBomb) to friend
      '''

      util.commute_packet_queue.put({
                'event': 'Advice',
                'myPlayerid': myID,
                'friendPlayerid': friendID,
                'Move': advice,
                'Goal': goal
      })
    def registerFriend(self,myID,friendID):
      util.commute_packet_queue.put({
              'event': 'register_friend',
              'myPlayerid': myID,
              'friendPlayerid': friendID
      })
    def checkNone(self,player):
      if player.friendId==[]:
          player.friendId=self.friendId
      if len(player.friendId)>1 and player.friendId[0]=='None':
         player.friendId.remove('None')
    def checkValidId(self,IdList,state):
       if not IdList : return 
       for ID in IdList:
         try:
            if ID=="None":
              return 
            state.players[ID]
         except:
            print "False"
            state.me().friendId.remove(ID)
            return 
       return 

    def once(self, state):
        player=state.me()
        myID=player.thisPlayer_id
        self.checkNone(player)
        move = self.lastMove
        self.checkValidId(player.friendId,state)
        if player.friendId:
          friendId=player.friendId[0]
          validMoveforFriend=state.validMovesForPlayer(friendId)
          if Direction.STOP in validMoveforFriend: 
            validMoveforFriend.remove(Direction.STOP)
          if validMoveforFriend:
            move = random.choice(validMoveforFriend)
            putBomb=False
            self.sendAdviceFriend(myID,friendId,str((move,putBomb)))
    def coordinate(self,state,friendId): 
        raise NotImplementedError("Please Implement this method")






