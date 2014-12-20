import gevent
import gevent.monkey

# Make standard library compatible with gevent
# should be called before importing 'threading'
# http://stackoverflow.com/questions/8774958/keyerror-in-module-threading-after-a-successful-py-test-run
gevent.monkey.patch_all()

import json
import random
import ws4py.client

from player import Player
from game_map import Map
import util
from task_loop import TaskLoop

global_map = Map()
players = {}
thisPlayer_name = None


def dump_players():
    for player_id, player in players.items():
        print(player)


def handle_messages(event, data):

    if event != 'player_position':
        print('[event] %s' % event)

    # General events
    if event == 'playerid':
        player_id = Player.thisPlayer_id = data['playerid']
        print('My player id is %s' % Player.thisPlayer_id)
        players[player_id] = Player(Player.thisPlayer_id, thisPlayer_name)

    elif event == 'map_initial':
        global_map.setGrids(data['grids'])

    elif event == 'game_started':
        print('Game started')

        def __internal():
            for player_id, player in players.items():
                player.setPreparing()

        if data['already_started']:
            __internal()
        else:
            util.loop.add_task(TaskLoop.delay, 3, __internal)

    elif event == 'player_list':
        playersList = data['list']
        for player in playersList:
            player_id = player['playerid']

            # Create the player if not exist
            if player_id not in players:
                players[player_id] = Player(player_id, player['name'])

            # Update info
            player = players[player_id]
            player.setCoord(player['x'], player['y'])
            player.updateStatus(player['dead'], player['disconnected'])
        print('Receive players')
        dump_players()

    elif event == 'pos_initial':
        players[Player.thisPlayer_id].setPos(data['pos'])

    elif event == 'player_position':
        playerid = data['playerid']
        players[playerid].setCoord(data['x'], data['y'])

    elif event == 'player_offline':
        playerid = data['playerid']
        players.pop(playerid, None)
        print('Player %s is offline\nPlayers: ' % playerid)
        dump_players()

    # bomb events
    elif event == 'bomb_put':
        global_map.bombPut(util.gridToPos(data['x'], data['y']))

    elif event == 'grid_bombed':
        global_map.gridBombed(util.gridToPos(data['x'], data['y']))

    elif event == 'wall_vanish':
        global_map.wallBombed(util.gridToPos(data['x'], data['y']))

    elif event == 'player_bombed':
        players[data['playerid']].bombed()

    # tool events
    elif event == 'tool_appeared':
        global_map.toolAppeared(data['grid'], data['tooltype'])

    elif event == 'tool_disappeared':
        eater = data['eater']
        tooltype = data['tooltype']
        pos = data['glogrid']
        global_map.toolDisappeared(eater=eater, tooltype=tooltype, pos=pos)
        if eater != 'bomb':
            players[eater].toolapply(tooltype)

    else:
        print('Unknown data')
        print(data)


class WebSocketHandler(ws4py.client.WebSocketBaseClient):
    def __init__(self, *args, **kwargs):
        global thisPlayer_name
        super(WebSocketHandler, self).__init__(*args, **kwargs)

        self._th = gevent.Greenlet(self.run)

        thisPlayer_name = 'AI #%d' % random.randrange(0, 100)
        print('My name is %s' % thisPlayer_name)

    def sendJson(self, data):
        self.send(json.dumps(data))

    def opened(self):
        self.sendJson({
            'event': 'update_player_info',
            'name': thisPlayer_name
        })

    def handshake_ok(self):
        self._th.start()

    def received_message(self, data):
        try:
            obj = json.loads(str(data))  # data is in fact a Message Object
        except:
            print('Invalid JSON from server: %s' % data)
            return
        if not isinstance(obj, dict) or 'event' not in obj:
            print('Invalid message from server')
            print(obj)
            return

        event = obj['event']
        handle_messages(event, obj)

    def closed(self, code, reason=None):
        print("Closed down, code = %d, reason = %s" % (code, reason))


def main():
    util.loop = TaskLoop()

    try:
        addr = 'ws://localhost:3000/'
        ws = WebSocketHandler(addr, protocols=['game-protocol'])
        ws.connect()
        # ws.run_forever()
        gevent.joinall([ws._th, gevent.spawn(util.loop.run)])
    except KeyboardInterrupt:
        util.loop.running = False
        print("Exiting...")
        ws.close()

if __name__ == '__main__':
    main()
