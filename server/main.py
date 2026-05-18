import socket
import threading

from server.response import Response
from .database import MinisculeDatabase
from .utils import handle_command, validate_command
from .errors import MinisculeError
from config import HOST, PORT


def handle_client(conn, addr, db):
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

            one_word_cmd = msg.strip().upper()

            if one_word_cmd == "EXIT":
                connected = False
                break

            if one_word_cmd == "HELP":
                help_message = (
                    "Available commands:\n"
                    "SET key value [type] - Set a value with an optional type (str, int, float, bool, list, dict)\n"
                    "GET key - Get the value of a key\n"
                    "DEL key - Delete a key\n"
                    "EXIT - Disconnect from the server\n"
                    "HELP [command] - Show this help message or details about a specific command"
                )
                conn.send(f"{help_message}\n".encode("utf-8"))
                continue

            # Log at the server side which client sent which command for better debugging.
            print(f"[{addr}] {msg}")

            # The server processes the command sent by the client using the following function:
            response = handle_command(
                validate_command(msg),
                db,
            )

            print(f"[{addr}] Response: {response.serialize()}")

            conn.send(f"{response.serialize()}\n".encode("utf-8"))

        except ConnectionResetError:
            break
        except MinisculeError as m_error:
            # Reconstruct the response format to match what users expect natively
            err_response = Response(
                {"status": m_error.code["status"], "action": m_error.code["message"]},
                message=str(m_error),
            )
            print(f"[{addr}] Error: {m_error.code['status']}:{m_error.code['message']}")
            conn.send(f"{err_response.serialize()}\n".encode("utf-8"))

    conn.close()


def start_server(host, port):
    # socket.AF_INET specifies that we are using IPv4 addresses,
    # and socket.SOCK_STREAM indicates that we are using TCP for communication.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Allow reusing the address and port combination to avoid wait times on restart.
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the server socket to the host and port.
    server.bind((host, port))
    server.listen()
    print(f"[LISTENING] Server is listening on {host}:{port}")

    # Set a timeout for the accept() method to allow periodic checks for shutdown signals
    # (like KeyboardInterrupt). This is especially useful on Windows.
    server.settimeout(1.0)
    print("Press Ctrl+C to stop the server.")

    try:
        db = MinisculeDatabase()
        while True:
            try:
                conn, addr = server.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr, db))
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


def main():
    start_server(HOST, PORT)


if __name__ == "__main__":
    main()
