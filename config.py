import threading

HOST = '127.0.0.1'
PORT = 6464
DATA_STORE = {}
LOCK = threading.Lock()