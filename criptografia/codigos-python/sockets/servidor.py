import socket
import ssl

import sys

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.minimum_version = ssl.TLSVersion.TLSv1_3 # permitir a partir de TLS 1.3
context.load_cert_chain('domain_cert.crt', 'domain_key.pem')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
    sock.bind(('0.0.0.0', int(sys.argv[1])))
    sock.listen(5)
    with context.wrap_socket(sock, server_side=True) as ssock:
        conn, addr = ssock.accept()
        mensaje = conn.recv(4096)
        print(mensaje)
        conn.send(b'OK')
