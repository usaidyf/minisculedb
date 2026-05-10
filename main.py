import socket
import threading
from utils import handle_command, validate_command, MinisculeError
from config import HOST, PORT, DATA_STORE, LOCK


def main():
    def handle_client(conn, addr):
        print(f"[NEW CONNECTION] {addr} connected.")
        conn.send("Welcome to Minisculedb!\n".encode("utf-8"))

        client_verbose = False
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
                    client_verbose = not client_verbose
                    status = "ON" if client_verbose else "OFF"
                    conn.send(f"<VERBOSE MODE {status}>\n".encode("utf-8"))
                    continue

                # Log at the server side which client sent which command for better debugging.
                print(f"[{addr}] {msg}")

                # The server processes the command sent by the client using the following function:
                response = handle_command(
                    validate_command(msg, client_verbose),
                    LOCK,
                    DATA_STORE,
                    client_verbose,
                )

                # Sends the response from above back to the client
                conn.send(f"{response}{"\n" if client_verbose else ''}".encode("utf-8"))

            except ConnectionResetError:
                break
            except MinisculeError as m_error:
                conn.send(f"{m_error.error_code}\n".encode("utf-8"))

        conn.close()

    def start_server():
        # socket.AF_INET specifies that we are using IPv4 addresses,
        # and socket.SOCK_STREAM indicates that we are using TCP for communication.
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reusing the address and port combination to avoid wait times on restart.
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the server socket to the host and port.
        server.bind((HOST, PORT))
        server.listen()
        print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

        # Set a timeout for the accept() method to allow periodic checks for shutdown signals
        # (like KeyboardInterrupt). This is especially useful on Windows.
        server.settimeout(1.0)
        print("Press Ctrl+C to stop the server.")

        try:
            while True:
                try:
                    conn, addr = server.accept()
                    thread = threading.Thread(target=handle_client, args=(conn, addr))
                    thread.start()
                    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
                except socket.timeout:
                    continue

        except KeyboardInterrupt:
            print("\n[SHUTDOWN] Server is shutting down...")
        except Exception as error:
            print("\n[CRITICAL] Error:", error)
        finally:
            server.close()
            print("[SHUTDOWN] Server closed.")

    start_server()


if __name__ == "__main__":
    main()
