import gevent
import time
from compat import queue
import util


class TaskLoop(object):
    def __init__(self):
        self.q = queue.Queue()
        self.last_timestamp = time.time()

    def update_timeouts(self):
        # XXX is it safe to access elements in a Queue directly?
        new_timestamp = time.time()
        min_timeout = float("inf")
        # print('-----------')
        for i in range(0, len(self.q.queue)):
            timeout, callback, args, kwargs = self.q.queue[i]
            old_timeout = timeout
            timeout -= (new_timestamp - self.last_timestamp)
            if hasattr(callback, '__name__'):
                cbName = callback.__name__
            else:
                cbName = callback
            # print(old_timeout, timeout, cbName)
            if min_timeout > timeout:
                min_timeout = timeout
            self.q.queue[i] = (timeout, callback, args, kwargs)
        self.last_timestamp = new_timestamp

        gevent.sleep(min(util.BASE_INTERVAL, min_timeout))

    def add_timed_task_impl(self, timeout, callback, *args, **kwargs):
        self.q.put((timeout, callback, args, kwargs))

    def add_timed_task(self, timeout, callback, *args, **kwargs):
        self.update_timeouts()
        self.add_timed_task_impl(timeout, callback, *args, **kwargs)

    def add_task(self, callback, *args, **kwargs):
        self.add_timed_task(0, callback, *args, **kwargs)

    def add_finished_task(self):
        self.add_task('finished', None, None)
        print('Task loop is going to be terminated')

    def run(self):
        while True:
            self.update_timeouts()
            timeout, callback, args, kwargs = self.q.get()
            if timeout <= 0:
                if not self.run_task(callback, args, kwargs):
                    break
            else:
                self.add_timed_task_impl(timeout, callback, *args, **kwargs)

    def run_task(self, callback, args, kwargs):
        if callback == 'finished':
            print('Task loop exits')
            return False

        callback(*args, **kwargs)
        return True
