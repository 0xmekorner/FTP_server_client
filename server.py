import socket
import threading
from pathlib import Path

HOST = "127.0.0.1"
PORT = 5001
STORAGE = Path("server_storage")
STORAGE.mkdir(exist_ok=True)
BUFFER_SIZE = 4096

def send_line(conn, text):
    conn.sendall((text + "\n").encode())

def recv_line(file):
    return file.readline().decode().strip()

def handle_client(conn, address):
    print(f"Connected: {address}")
    file = conn.makefile("rb")

    try:
        while True:
            command = recv_line(file)

            if not command:
                break

            parts = command.split(" ", 2)
            action = parts[0].upper()

            if action == "LIST":
                files = [p.name for p in STORAGE.iterdir() if p.is_file()]
                send_line(conn, "OK " + "|".join(files))

            elif action == "UPLOAD" and len(parts) == 3:
                filename = Path(parts[1]).name
                size = int(parts[2])
                target = STORAGE / filename

                with open(target, "wb") as output:
                    remaining = size
                    while remaining:
                        chunk = conn.recv(min(BUFFER_SIZE, remaining))
                        if not chunk:
                            raise ConnectionError("Client disconnected during upload.")
                        output.write(chunk)
                        remaining -= len(chunk)

                send_line(conn, "OK UPLOAD")

            elif action == "DOWNLOAD" and len(parts) == 2:
                filename = Path(parts[1]).name
                target = STORAGE / filename

                if not target.is_file():
                    send_line(conn, "ERROR NOT_FOUND")
                    continue

                size = target.stat().st_size
                send_line(conn, f"OK {size}")

                with open(target, "rb") as input_file:
                    while chunk := input_file.read(BUFFER_SIZE):
                        conn.sendall(chunk)

            elif action == "QUIT":
                send_line(conn, "OK BYE")
                break

            else:
                send_line(conn, "ERROR INVALID_COMMAND")

    except Exception as error:
        print(f"Client error {address}: {error}")
    finally:
        conn.close()
        print(f"Disconnected: {address}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()

        print(f"File server listening on {HOST}:{PORT}")

        while True:
            conn, address = server.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(conn, address),
                daemon=True,
            )
            thread.start()

if __name__ == "__main__":
    main()
