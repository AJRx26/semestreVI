#!/usr/bin/env python3

import socket
import struct
import sys
import utils


def crear_socket_servidor(puerto):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(('', int(puerto)))
    return servidor


def recv_exact(sock, num_bytes) -> bytes:
    datos = b''
    while len(datos) < num_bytes:
        chunk = sock.recv(num_bytes - len(datos))
        if not chunk:
            raise ConnectionError('Conexión cerrada mientras se recibían datos')
        datos += chunk
    return datos


def enviar(conn, datos: bytes):
    """Envía datos precedidos de su longitud (4 bytes)."""
    conn.sendall(struct.pack('!I', len(datos)) + datos)


def recibir(conn) -> bytes:
    """Recibe datos precedidos de su longitud (4 bytes)."""
    longitud = struct.unpack('!I', recv_exact(conn, 4))[0]
    return recv_exact(conn, longitud)


def cargar_identidad(ruta_privada, ruta_publica):
    """Carga las llaves ECDSA del servidor y la pública del cliente."""
    print('[*] Cargando llaves ECDSA...')
    priv_ecdsa        = utils.cargar_llave_privada(ruta_privada)
    pub_ecdsa_cliente = utils.cargar_llave_publica(ruta_publica)
    print('[+] Llaves ECDSA cargadas')
    return priv_ecdsa, pub_ecdsa_cliente


def handshake(cliente, priv_ecdsa, pub_ecdsa_cliente):
    """
    Realiza el intercambio de llaves con el cliente:
    1. Recibe pub_ECDH + firma del cliente
    2. Verifica la firma
    3. Envía pub_ECDH + firma propias
    4. Deriva y retorna la llave AES-256
    """
    # Generar llaves ECDH efímeras y firmarlas
    priv_ecdh, pub_ecdh = utils.generar_llaves_ecdh()
    pub_ecdh_bytes      = utils.serializar_publica(pub_ecdh)
    firma               = utils.firmar(pub_ecdh_bytes, priv_ecdsa)

    # PASO 1: Recibir pub_ECDH y firma del cliente
    print('[*] Esperando llaves del cliente...')
    pub_ecdh_cliente_bytes = recibir(cliente)
    firma_cliente          = recibir(cliente)

    # PASO 2: Verificar firma del cliente
    if not utils.verificar(pub_ecdh_cliente_bytes, firma_cliente, pub_ecdsa_cliente):
        raise ValueError('Firma del cliente inválida')
    print('[+] Firma del cliente verificada')

    # PASO 3: Enviar pub_ECDH + firma al cliente
    enviar(cliente, pub_ecdh_bytes)
    enviar(cliente, firma)
    print('[+] Llaves enviadas al cliente')

    # PASO 4: Derivar llave AES
    pub_ecdh_cliente = utils.deserializar_publica(pub_ecdh_cliente_bytes)
    return utils.derivar_llave(priv_ecdh, pub_ecdh_cliente)


def escuchar(servidor, priv_ecdsa, pub_ecdsa_cliente):
    servidor.listen(1)
    print(f'[*] Esperando conexión...')

    cliente, addr = servidor.accept()
    with cliente:
        print(f'[+] Cliente conectado desde {addr}')
        try:
            llave_aes = handshake(cliente, priv_ecdsa, pub_ecdsa_cliente)
        except ValueError as e:
            print(f'[!] {e} — cerrando conexión')
            return

        print(f'\n[+] Llave AES-256 derivada:')
        print(f'    {llave_aes.hex()}')


if __name__ == '__main__':
    puerto = sys.argv[1]
    ruta_privada = sys.argv[2]
    ruta_publica = sys.argv[3]
    priv_ecdsa, pub_ecdsa_cliente = cargar_identidad(ruta_privada, ruta_publica)
    servidor = crear_socket_servidor(puerto)
    escuchar(servidor, priv_ecdsa, pub_ecdsa_cliente)
