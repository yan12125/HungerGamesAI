import gevent
from compat import queue


class TaskLoop(object):
    q = queue.Queue()

    def __init__(self):
        pass

    def add_task(self, callback, *args, **kwargs):
        self.q.put((callback, args, kwargs))

    def add_finished_task(self):
        self.add_task('finished', None, None)
        print('Task loop is going to be terminated')

    def run(self):
        while True:
            gevent.sleep()
            callback, args, kwargs = self.q.get()
            if callback == 'finished':
                print('Task loop exits')
                break
            callback(*args, **kwargs)

    @staticmethod
    def delay(nSeconds, callback, *args, **kwargs):
        gevent.sleep(nSeconds)
        callback(*args, **kwargs)
