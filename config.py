from dotenv import load_dotenv
import os
import threading
load_dotenv()

def get_env_or_exit(key):
    value = os.getenv(key)
    if value is None:
        print(f"Error: Environment variable '{key}' is not set.")
        exit(1)
    return value

HOST = get_env_or_exit('HOST')
PORT = int(get_env_or_exit('PORT'))
DATA_STORE = {}
LOCK = threading.Lock()