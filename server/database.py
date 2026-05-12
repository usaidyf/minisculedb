import threading


class MinisculeDatabase:
    """
    Encapsulates the in-memory data store and its thread lock.
    This replaces the global DATA_STORE and LOCK variables.
    """

    def __init__(self):
        self._store = {}
        self._lock = threading.Lock()

    def set(self, key, value):
        with self._lock:
            self._store[key] = value

    def get(self, key):
        with self._lock:
            return self._store.get(key)

    def delete(self, key):
        with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False

    def exists(self, key):
        with self._lock:
            return key in self._store
