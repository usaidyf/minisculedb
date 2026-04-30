import socket
import threading
from utils import handle_command, validate_command, MinisculeError
from config import HOST, PORT, DATA_STORE, LOCK

CLIENT_VERBOSE = False


def main():
    def handle_client(conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        conn.send("Welcome to Minisculedb!\n".encode("utf-8"))

        connected = True
        while connected:
            try:
                # 1024 is the size of the buffer in bytes for receiving data
                # meaning that the server will read up to 1024 bytes of data sent by the client at a time.
                msg = conn.recv(1024).decode("utf-8")
                if not msg:
                    break

                if msg.strip().upper() == "EXIT":
                    connected = False
                    break

                # This is for the client to receive more detailed responses from the server for
                # debugging, testing purposes and for a more "console-like" experience.
                if msg.strip().upper() == "VERBOSE":
                    global CLIENT_VERBOSE
                    CLIENT_VERBOSE = not CLIENT_VERBOSE
                    status = "ON" if CLIENT_VERBOSE else "OFF"
                    conn.send(f"<VERBOSE MODE {status}>\n".encode("utf-8"))
                    continue

                # Log at the server side which client sent which command for better debugging.
                print(f"[{addr}] {msg}")
                
                # The server processes the command sent by the client using the following function:
                response = handle_command(
                    validate_command(msg, CLIENT_VERBOSE),
                    LOCK,
                    DATA_STORE,
                    CLIENT_VERBOSE,
                )

                # Sends the response from above back to the client
                conn.send(f"{response}{"\n" if CLIENT_VERBOSE else ''}".encode("utf-8"))

            except ConnectionResetError:
                break
            except MinisculeError as m_error:
                conn.send(f"{m_error.error_code}\n".encode("utf-8"))

        conn.close()

    def start_server():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
