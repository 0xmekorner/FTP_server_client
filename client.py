import socket
from pathlib import Path

HOST = "127.0.0.1"
PORT = 5001
BUFFER_SIZE = 4096

def recv_line(file):
    return file.readline().decode().strip()

def upload(sock, file, path):
    path = Path(path)
    if not path.is_file():
        print("File not found.")
        return

    sock.sendall(f"UPLOAD {path.name} {path.stat().st_size}\n".encode())
    with open(path, "rb") as input_file:
        while chunk := input_file.read(BUFFER_SIZE):
            sock.sendall(chunk)

    print(recv_line(file))

def download(sock, file, filename):
    sock.sendall(f"DOWNLOAD {filename}\n".encode())
    response = recv_line(file)

    if not response.startswith("OK "):
        print(response)
        return

    size = int(response.split()[1])
    output = Path("downloads") / Path(filename).name
    output.parent.mkdir(exist_ok=True)

    with open(output, "wb") as destination:
        remaining = size
        while remaining:
            chunk = sock.recv(min(BUFFER_SIZE, remaining))
            if not chunk:
                raise ConnectionError("Server disconnected during download.")
            destination.write(chunk)
            remaining -= len(chunk)

    print(f"Saved to {output}")

def main():
    with socket.create_connection((HOST, PORT)) as sock:
        file = sock.makefile("rb")

        while True:
            command = input("file-client> ").strip()
            parts = command.split(" ", 1)

            if command == "list":
                sock.sendall(b"LIST\n")
                print(recv_line(file))

            elif parts[0] == "upload" and len(parts) == 2:
                upload(sock, file, parts[1])

            elif parts[0] == "download" and len(parts) == 2:
                download(sock, file, parts[1])

            elif command == "quit":
                sock.sendall(b"QUIT\n")
                print(recv_line(file))
                break

            else:
                print("Commands: list, upload <path>, download <name>, quit")

if __name__ == "__main__":
    main()
