import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, limit=10, window=60, clock=time.monotonic):
        self.limit = limit
        self.window = window
        self.clock = clock
        self.events = defaultdict(deque)

    def allow(self, key):
        now = self.clock()
        queue = self.events[key]
        while queue and queue[0] <= now - self.window:
            queue.popleft()
        if len(queue) >= self.limit:
            return False
        queue.append(now)
        return True
