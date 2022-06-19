import time
import threading
import heapq
import logging

class timer_object():
    def __init__(self, timeInSeconds, callback, object):
        self.time = time.time() + timeInSeconds
        self.callback = callback
        self.object = object
    def __gt__(self, other):
        return self.time > other.time
    def __lt__(self, other):
        return self.time < other.time
    def __eq__(self, other):
        return self.time == other.time
    def __le__(self, other):
        return self.time <= other.time
    def __ge__(self, other):
        return self.time >= other.time
    def call(self):
        self.callback(self.object)

timer_thread = None
timer_queue = []

def add_timer(time, callback, object):
    heapq.heappush(timer_queue, timer_object(time, callback, object))

def initalize():
    timer_thread = threading.Thread(target=timer_worker)
    timer_thread.daemon = True
    timer_thread.start()

def timer_worker():
    while True:
        try:
            now = time.time()
            while len(timer_queue) > 0 and timer_queue[0].time <= now:
                timer_queue[0].call()
                heapq.heappop(timer_queue)
            time.sleep(0.5)
        except Exception as e:
            logging.error(f"[timer:timer_worker] exception: {e}")
            continue