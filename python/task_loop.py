import gevent
import time
from compat import queue


class TaskLoop(object):
    def __init__(self):
        self.q = queue.Queue()
        self.last_timestamp = time.time()

    def add_timed_task(self, timeout, callback, *args, **kwargs):
        self.q.put((timeout, callback, args, kwargs))

    def add_task(self, callback, *args, **kwargs):
        self.add_timed_task(0, callback, *args, **kwargs)

    def add_finished_task(self):
        self.add_task('finished', None, None)
        print('Task loop is going to be terminated')

    def run(self):
        while True:
            gevent.sleep()
            timeout, callback, args, kwargs = self.q.get()
            new_timestamp = time.time()
            timeout -= (new_timestamp - self.last_timestamp)
            if timeout <= 0:
                if not self.run_task(callback, args, kwargs):
                    break
            else:
                self.add_timed_task(timeout, callback, *args, **kwargs)

            self.last_timestamp = new_timestamp

    def run_task(self, callback, args, kwargs):
        if callback == 'finished':
            print('Task loop exits')
            return False

        callback(*args, **kwargs)
        return True
