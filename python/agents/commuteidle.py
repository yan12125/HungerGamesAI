from .agent import Agent
import util

class CommuteidleAgent(Agent):
    def __init__(self):
        super(CommuteidleAgent, self).__init__()
        self.friendId=[]

    def once(self, state):
        player=state.me()
        if player.friendId==[]:
          player.friendId=self.friendId
        if player.friendId:
#          print player.thisPlayer_id
          util.commute_packet_queue.put({
              'event': 'register_friend',
              'myPlayerid': player.thisPlayer_id,
              'friendPlayerid': player.friendId[0]
          })
          if len(player.friendId)>1 and player.friendId[0]=='None':
            self.friendId.remove('None')


