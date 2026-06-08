#!/bin/sh
set -e

if [ -n "$DATABASE_URL" ]; then
  python - <<'PY'
import os
import socket
import time
from urllib.parse import urlparse

database_url = os.environ["DATABASE_URL"]
parsed = urlparse(database_url)
host = parsed.hostname
port = parsed.port or 5432
deadline = time.time() + 60

while True:
    try:
        connected = False
        for family, socktype, proto, _, sockaddr in socket.getaddrinfo(host, port, type=socket.SOCK_STREAM):
            try:
                with socket.socket(family, socktype, proto) as sock:
                    sock.settimeout(2)
                    sock.connect(sockaddr)
                    connected = True
                    break
            except OSError:
                continue
        if connected:
            break
    except OSError:
        if time.time() >= deadline:
            raise
        time.sleep(1)
PY
fi

exec "$@"