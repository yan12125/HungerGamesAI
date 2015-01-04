from .agent import Agent
import util

class AdviceonlyAgent(Agent):
    def __init__(self):
        super(AdviceonlyAgent, self).__init__()
        self.friendId=[]

    def once(self, state):
        player=state.me()
        if player.friendId==[]:
          player.friendId=self.friendId
#        print "I have DOne something",player.friendId,player.thisPlayer_id 
        if player.friendId and not player.MoveAdvice:
          print player.thisPlayer_id
          print player.x, player.y
          util.commute_packet_queue.put({
              'event': 'register_friend',
              'myPlayerid': player.thisPlayer_id,
              'friendPlayerid': player.friendId[0]
          })
          if len(player.friendId)>1 and player.friendId[0]=='None':
            self.friendId.remove('None')
        MyFriend=player.friendId
        myFriendAdvice = player.MoveAdvice
        print player.MoveAdvice
        print state.validMovesForMe()
        if player.MoveAdvice:
          move,putBomb=eval(myFriendAdvice[0])
          if state.moveValidForMe(move):
            print move
            self.goMove(player, move)
          if putBomb:
            self.tryPutBomb(state, player)
          player.MoveAdvice=[]



