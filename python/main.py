from __future__ import division

import gevent
import gevent.monkey

# Make standard library compatible with gevent
# should be called before importing 'threading'
# http://stackoverflow.com/questions/8774958/keyerror-in-module-threading-after-a-successful-py-test-run
gevent.monkey.patch_all()

import compat
compat.patch_all()

import random

from game_state import GameState
from websocket_client import WebSocketHandler
import util
# from agent import RandomAgent as Agent
from bomber import BomberAgent as Agent

GameState.current = GameState()

current_agent = Agent()


def main():
    myname = 'AI #%d' % random.randrange(0, 100)
    print('My name is %s' % myname)

    try:
        addr = 'ws://localhost:3000/'
        ws = WebSocketHandler(current_agent, myname, addr, ['game-protocol'])
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
