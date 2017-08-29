from queue import Queue
from threading import Thread
import logging

logger = logging.getLogger(__name__)


class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.queue.get()
            try:
                func(*args, **kargs)
            except Exception as ex:
                # An exception happened in this thread
                logger.exception("An error occurred while performing work", exc_info=ex)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.queue.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """

    def __init__(self, num_threads=10):
        self.queue = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.queue)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.queue.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)
