import socket
import threading

HOST = '127.0.0.1'
PORT = 6464
DATA_STORE = {}
LOCK = threading.Lock()

class MinisculeError(Exception):
    def __init__(self, message, error_code="<GENERIC>"):
        super().__init__(message)
        self.error_code = error_code

def main():
    def handle_command(command):
        parts = command.split()
        cmd = parts[0]

        if cmd == "SET":
            key, value = parts[1], parts[2]

            with LOCK:
                DATA_STORE[key] = value
            return "<OK>"

        elif cmd == "GET":
            key = parts[1]

            with LOCK:
                val = DATA_STORE.get(key)
            return val if val else "<INVALID_KEY>"

        elif cmd == "DEL":
            key = parts[1]

            with LOCK:
                if key in DATA_STORE:
                    del DATA_STORE[key]
                    return "<DELETED>"
                else:
                    return "<INVALID_KEY>"

    def validate_command(command):
        parts = command.split()
        parts_length = len(parts)
        
        if parts_length == 0:
            raise MinisculeError("Empty command", "<EMPTY_COMMAND_STRING>")

        cmd = parts[0].upper()
        
        if cmd == "SET" and parts_length > 3:
            raise MinisculeError("Too many arguments", "<TOO_MANY_ARGS>")
        if (cmd == "GET" or cmd == "DEL") and parts_length > 2:
            raise MinisculeError("Too many arguments", "<TOO_MANY_ARGS>")
        if cmd not in {"GET", "SET", "DEL"}:
            raise MinisculeError("Invalid command", "<INVALID_COMMAND>")

        return f"{cmd} " + " ".join(parts[1:])

    def handle_client(conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        conn.send("Welcome to Minisculedb!\n".encode('utf-8'))
        
        connected = True
        while connected:
            try:
                msg = conn.recv(1024).decode('utf-8')
                if not msg:
                    break
                
                # Welcome user
                
                if msg.strip().upper() == "DISCONNECT":
                    connected = False
                    break
                
                print(f"[{addr}] {msg}")
                response = handle_command(validate_command(msg))
                conn.send(f"{response}\n".encode('utf-8'))
                
            except ConnectionResetError:
                break
            except MinisculeError as m_error:
                conn.send(f"{m_error}\n".encode('utf-8'))
            
        conn.close()
        
    def start_server():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen()
        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
        
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    
    start_server()


if __name__ == "__main__":
    main()
