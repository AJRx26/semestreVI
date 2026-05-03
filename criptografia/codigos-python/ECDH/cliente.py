#!/usr/bin/env python3

import socket
import struct
import sys
import utils


def crear_socket_cliente(host, puerto):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((host, int(puerto)))
    return cliente


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
    """Carga las llaves ECDSA del cliente y la pública del servidor."""
    print('[*] Cargando llaves ECDSA...')
    priv_ecdsa         = utils.cargar_llave_privada(ruta_privada)
    pub_ecdsa_servidor = utils.cargar_llave_publica(ruta_publica)
    print('[+] Llaves ECDSA cargadas')
    return priv_ecdsa, pub_ecdsa_servidor


def handshake(conn, priv_ecdsa, pub_ecdsa_servidor):
    """
    Realiza el intercambio de llaves con el servidor:
    1. Genera llaves ECDH efímeras y las firma
    2. Envía pub_ECDH + firma al servidor
    3. Recibe pub_ECDH + firma del servidor
    4. Verifica la firma
    5. Deriva y retorna la llave AES-256
    """
    # Generar llaves ECDH efímeras y firmarlas
    priv_ecdh, pub_ecdh = utils.generar_llaves_ecdh()
    pub_ecdh_bytes      = utils.serializar_publica(pub_ecdh)
    firma               = utils.firmar(pub_ecdh_bytes, priv_ecdsa)

    # PASO 1: Enviar pub_ECDH + firma al servidor
    enviar(conn, pub_ecdh_bytes)
    enviar(conn, firma)
    print('[+] Llaves enviadas al servidor')

    # PASO 2: Recibir pub_ECDH y firma del servidor
    print('[*] Esperando llaves del servidor...')
    pub_ecdh_servidor_bytes = recibir(conn)
    firma_servidor          = recibir(conn)

    # PASO 3: Verificar firma del servidor
    if not utils.verificar(pub_ecdh_servidor_bytes, firma_servidor, pub_ecdsa_servidor):
        raise ValueError('Firma del servidor inválida')
    print('[+] Firma del servidor verificada')

    # PASO 4: Derivar llave AES
    pub_ecdh_servidor = utils.deserializar_publica(pub_ecdh_servidor_bytes)
    return utils.derivar_llave(priv_ecdh, pub_ecdh_servidor)


def conectar(host, puerto, priv_ecdsa, pub_ecdsa_servidor):
    conn = crear_socket_cliente(host, puerto)
    with conn:
        print(f'[+] Conectado al servidor {host}:{puerto}')
        try:
            llave_aes = handshake(conn, priv_ecdsa, pub_ecdsa_servidor)
        except ValueError as e:
            print(f'[!] {e} — cerrando conexión')
            return

        print(f'\n[+] Llave AES-256 derivada:')
        print(f'    {llave_aes.hex()}')


if __name__ == '__main__':
    host   = sys.argv[1]
    puerto = sys.argv[2]
    ruta_privada = sys.argv[3]
    ruta_publica = sys.argv[4]
    priv_ecdsa, pub_ecdsa_servidor = cargar_identidad(ruta_privada, ruta_publica)
    conectar(host, puerto, priv_ecdsa, pub_ecdsa_servidor)
