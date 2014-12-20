from __future__ import division

import gevent
import gevent.monkey

# Make standard library compatible with gevent
# should be called before importing 'threading'
# http://stackoverflow.com/questions/8774958/keyerror-in-module-threading-after-a-successful-py-test-run
gevent.monkey.patch_all()

import json
import random
import ws4py.client

from game_state import GameState
import util
from task_loop import TaskLoop
from player import Player
import agent

thisPlayer_name = None

current_state = GameState()

agent = agent.RandomAgent()


def handle_messages(event, data):

    if event != 'player_position':
        print('[event] %s' % event)

    # General events
    if event == 'playerid':
        Player.thisPlayer_id = data['playerid']
        print('My player id is %s' % Player.thisPlayer_id)
        current_state.add_player(Player.thisPlayer_id, thisPlayer_name)

    elif event == 'map_initial':
        current_state.game_map.setGrids(data['grids'])

    elif event == 'game_started':
        print('Game started')

        current_state.game_started = True

        def __internal():
            for player_id, player in current_state.players.items():
                player.setPreparing()

        if data['already_started']:
            __internal()
        else:
            util.loop.add_task(TaskLoop.delay, 3, __internal)

    elif event == 'player_list':
        playersList = data['list']
        for playerObj in playersList:
            player_id = playerObj['playerid']

            # Create the player if not exist
            if player_id not in current_state.players:
                current_state.add_player(player_id, playerObj['name'])

            # Update info
            player = current_state.players[player_id]
            player.setCoord(playerObj['x'], playerObj['y'])
            player.updateStatus(playerObj['dead'], playerObj['disconnected'])
        print('Receive players')
        current_state.dump_players()

    elif event == 'pos_initial':
        current_state.me().setPos(data['pos'])

    elif event == 'player_position':
        playerid = data['playerid']
        current_state.players[playerid].setCoord(data['x'], data['y'])

    elif event == 'player_offline':
        playerid = data['playerid']
        current_state.players.pop(playerid, None)
        print('Player %s is offline\nPlayers: ' % playerid)
        current_state.dump_players()

    # bomb events
    elif event == 'bomb_put':
        current_state.game_map.bombPut(util.gridToPos(data['x'], data['y']))

    elif event == 'grid_bombed':
        current_state.game_map.gridBombed(util.gridToPos(data['x'], data['y']))

    elif event == 'wall_vanish':
        current_state.game_map.wallBombed(util.gridToPos(data['x'], data['y']))

    elif event == 'player_bombed':
        player_id = str(data['playerid'])
        current_state.players[player_id].bombed()

    # tool events
    elif event == 'tool_appeared':
        current_state.game_map.toolAppeared(data['grid'], data['tooltype'])

    elif event == 'tool_disappeared':
        eater = data['eater']
        tooltype = data['tooltype']
        pos = data['glogrid']
        current_state.game_map.toolDisappeared(eater, tooltype, pos)
        if eater != 'bomb':
            current_state.players[eater].toolapply(tooltype)

    else:
        print('Unknown data')
        print(data)

    if current_state.game_started:
        util.loop.add_task(agent.once, current_state)


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

    def packet_consumer(self):
        while True:
            gevent.sleep(1/60)
            obj = util.packet_queue.get()
            if not obj:
                break
            self.sendJson(obj)


def main():
    try:
        addr = 'ws://localhost:3000/'
        ws = WebSocketHandler(addr, protocols=['game-protocol'])
        ws.connect()
        # ws.run_forever()
        greenlets = []
        greenlets.append(ws._th)
        greenlets.append(gevent.spawn(util.loop.run))
        greenlets.append(gevent.spawn(ws.packet_consumer))
        gevent.joinall(greenlets)
    except KeyboardInterrupt:
        util.mark_finished()
        print("Exiting...")
        ws.close()

if __name__ == '__main__':
    main()
