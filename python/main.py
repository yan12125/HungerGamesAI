import ws4py.client.threadedclient
import json
import random

from player import Player
from game_map import Map

global_map = Map()
players = {}
thisPlayer_id = None
thisPlayer_name = None

def dump_players():
    for player_id, player in players.items():
        print(player)

def handle_messages(event, data):
    global global_map, players, thisPlayer_id, thisPlayer_name

    if event != 'player_position':
        print('[event]', event)

    # General events
    if event == 'playerid':
        thisPlayer_id = data['playerid']
        print('My player id is', thisPlayer_id)
        players[thisPlayer_id] = Player(thisPlayer_id, thisPlayer_name)

    elif event == 'map_initial':
        global_map.setGrids(data['grids'])

    elif event == 'game_started':
        print('Game started')
        for player_id, player in players.items():
            player.setPreparing()

    elif event == 'player_list':
        playersList = data['list']
        for player in playersList:
            player_id = player['playerid']

            # Create the player if not exist
            if player_id not in players:
                players[player_id] = Player(player_id, player['name'])

            # Update info
            players[player_id].setCoord(player['x'], player['y'])
            players[player_id].updateStatus(dead=player['dead'], disconnected=player['disconnected'])
        print('Receive players')
        dump_players()

    elif event == 'pos_initial':
        players[thisPlayer_id].setPos(data['pos'])

    elif event == 'player_position':
        playerid = data['playerid']
        players[playerid].setCoord(data['x'], data['y'])

    elif event == 'player_offline':
        playerid = data['playerid']
        players.pop(playerid, None)
        print('Player %s is offline\nPlayers: ' % playerid)
        dump_players()

    # bomb events
    # tool events
    elif event == 'tool_appeared':
        global_map.toolAppeared(data)

    elif event == 'tool_disappeared':
        eater = data['eater']
        tooltype = data['tooltype']
        global_map.toolDisappeared(eater=eater, tooltype=tooltype, pos=data['glogrid'])
        if eater != 'bomb':
            players[eater].toolapply(tooltype)

    else:
        print('Unknown data')
        print(data)

class WebSocketHandler(ws4py.client.threadedclient.WebSocketClient):
    def __init__(self, *args, **kwargs):
        global thisPlayer_name
        super(WebSocketHandler, self).__init__(*args, **kwargs)
        thisPlayer_name = ('AI #%d' % random.randrange(0, 100))

    def sendJson(self, data):
        self.send(json.dumps(data))

    def opened(self):
        global thisPlayer_name
        self.sendJson({
            'event': 'update_player_info',
            'name': thisPlayer_name
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
        print("Exiting...")
        ws.close()

if __name__ == '__main__':
    main()
