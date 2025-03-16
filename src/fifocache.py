from collections import deque

class FIFOCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}  # Key-value store
        self.order = deque()  # Queue to maintain the order of insertion
    
    def get(self, key):
        """Retrieve item from cache. Does NOT cause eviction."""
        return self.cache.get(key, -1)
    
    def put(self, key, value):
        """Add item to cache. Evicts FIFO when capacity is exceeded."""
        if key in self.cache:
            # If key already exists, update value and move it to the end
            self.cache[key] = value
        else:
            # If the cache has reached its capacity, evict the oldest item (FIFO)
            if len(self.cache) >= self.capacity:
                oldest_key = self.order.popleft()  # Remove from the front of the queue
                del self.cache[oldest_key]  # Remove from cache
            # Add new item to cache and update order
            self.cache[key] = value
            self.order.append(key)
    
    def __iter__(self):
        """Make the cache iterable (iterate over key-value pairs in FIFO order)."""
        for key in self.order:
            yield key, self.cache[key]

    def __repr__(self):
        """For debugging purposes."""
        return f"Cache: {self.cache}\nOrder: {list(self.order)}"