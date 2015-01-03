from __future__ import division

import gevent
import gevent.monkey

# Make standard library compatible with gevent
# should be called before importing 'threading'
# http://stackoverflow.com/questions/8774958/keyerror-in-module-threading-after-a-successful-py-test-run
gevent.monkey.patch_all()

import compat
compat.patch_all()

import sys
import random
import argparse
import logging
import importlib
import traceback
import inspect
import colorama

from game_state import GameState
from websocket_client import WebSocketHandler
import util

colorama.init(autoreset=True)

GameState.current = GameState()


def load_agent(name):
    filename = 'agents/%s.py' % name

    try:
        agent_module = importlib.import_module('agents.'+name)
    except ImportError:
        print('File %s not found' % filename)
        return None
    except Exception:
        print('Failed to load %s' % filename)
        print(traceback.format_exc())
        return None

    class_name = name.capitalize()+'Agent'
    try:
        agent_class = getattr(agent_module, class_name)
    except AttributeError:
        print('class %s not found' % class_name)
        return None

    if not inspect.isclass(agent_class):
        print('%s is not a class' % class_name)
        return None

    agent = agent_class()
    return agent


def run_agent(agent):
    state = GameState.current
    if state.game_started:
        agent.once(state)

    util.loop.add_timed_task(util.BASE_INTERVAL, run_agent, agent)


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', dest='agentName', default='idle')
    parser.add_argument('-p', dest='posReq', default=None)
    options = parser.parse_args()
    current_agent = load_agent(options.agentName)

    if not current_agent:
        return -1

    myname = 'AI %s #%d' % (options.agentName, random.randrange(0, 100))
    print('My name is %s' % myname)

    if options.posReq:
        posReq = util.gridToPos(*util.strToGrid(options.posReq))
        print('Initial position at %s' % util.gridStr(posReq))
    else:
        posReq = None

    try:
        addr = 'ws://127.0.0.1:3000/'
        ws = WebSocketHandler(myname, posReq, addr, ['game-protocol'])
        ws.connect()
        run_agent(current_agent)
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
    sys.exit(main())
