import socket
import ssl

import sys

context = ssl.create_default_context(cafile='domain_cert.crt')
hostname = sys.argv[1]
puerto = int(sys.argv[2])

with socket.create_connection((hostname, puerto)) as sock:
    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(ssock.version())
        ssock.send(b'Hola mundo')
        respuesta = ssock.recv(4096)
        print(respuesta)
