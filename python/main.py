import ws4py.client.threadedclient
import json
import random

grids = None
players = {}
pos = -1
my_playerid = None

def handle_messages(event, data):
    global grids, players, pos, my_playerid
    if event == 'playerid':
        my_playerid = data['playerid']
        print('My player id is', my_playerid)
    elif event == 'map_initial':
        grids = data['grids']
    elif event == 'player_list':
        playersList = data['list']
        for player in playersList:
            players[player['playerid']] = player
        print('Receive players')
        print(json.dumps(players, indent=4))
    elif event == 'pos_initial':
        pos = data['pos']
    elif event == 'player_position':
        playerid = data['playerid']
        players[playerid]['pos'] = (data['x'], data['y'])
    elif event == 'player_offline':
        playerid = data['playerid']
        players.pop(playerid, None)
        print('Player %s is offline\nPlayers: ' % playerid)
        print(players)
    else:
        print('Unknown data')
        print(data)

class WebSocketHandler(ws4py.client.threadedclient.WebSocketClient):
    player_name = 'AI #'
    player_team = 'AI'

    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)
        self.player_name = self.player_name + str(random.randrange(0, 100))

    def sendJson(self, data):
        self.send(json.dumps(data))

    def opened(self):
        self.sendJson({
            'event': 'update_player_info',
            'name': self.player_name,
            'team': self.player_team
        })

    def closed(self, code, reason=None):
        print("Closed down, code = %d, reason = %s" % (code, reason))

    def received_message(self, data):
        try:
            obj = json.loads(str(data)) # data is in fact a Message Object
        except:
            print('Invalid JSON from server: %s' % data)
            return
        if not isinstance(obj, dict) or 'event' not in obj:
            print('Invalid message from server')
            print(obj)
            return

        event = obj['event']
        handle_messages(event, obj)

def main():
    try:
        ws = WebSocketHandler('ws://localhost:3000/', protocols=[ 'game-protocol' ])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()

if __name__ == '__main__':
    main()
