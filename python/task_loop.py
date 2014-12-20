import gevent
from compat import queue


class TaskLoop(object):
    q = queue.Queue()
    running = True

    def __init__(self):
        pass

    def add_task(self, callback, *args, **kwargs):
        self.q.put((callback, args, kwargs))

    def run(self):
        while self.running:
            gevent.sleep()
            callback, args, kwargs = self.q.get()
            callback(*args, **kwargs)

    @staticmethod
    def delay(nSeconds, callback, *args, **kwargs):
        gevent.sleep(nSeconds)
        callback(*args, **kwargs)
