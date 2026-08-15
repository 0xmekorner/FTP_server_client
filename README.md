The server listens on `127.0.0.1:5001`, accepts clients, and supports:

- Listing files on the server.
- Uploading files.
- Downloading files.
- Multiple clients using a separate thread per connection.

Files are transferred in chunks so the program does not need to load an entire large file into memory at once.

## Files

- `server.py` - TCP server and file-storage logic.
- `client.py` - interactive client.
- `README.md` - project overview and usage.
- `explanations.md` - detailed explanation of the code and protocol.

## How to run

Terminal 1:

```bash
python server.py
```

Terminal 2:

```bash
python client.py
```

The client commands are:

text
list
upload <path>
download <name>
quit


The server stores uploaded files in `server_storage/`.

The client stores downloaded files in `downloads/`.

