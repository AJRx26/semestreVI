#!/usr/bin/env python3

import socket
import sys
import utils

def crear_socket_cliente(host, puerto):
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((host, int(puerto)))
    return cliente


def cargar_identidad(ruta_privada, ruta_publica):
    """Carga las llaves ECDSA del cliente y la pública del servidor."""
    print('[+] Cargando llaves ECDSA')
    priv_ecdsa = utils.desserializar_privada(ruta_privada)
    pub_ecdsa_servidor = utils.desserializar_publica_pem(ruta_publica)
    print('[+] Llaves ECDSA cargadas')
    return priv_ecdsa, pub_ecdsa_servidor


def handshake(conn, priv_ecdsa, pub_ecdsa_servidor):
    """
    1. Genera llaves ECDH y las firma
    2. Envía pub_ECDH + firma al servidor
    3. Recibe pub_ECDH + firma del servidor
    4. Verifica la firma
    5. Deriva y retorna la llave AES-256
    """

    # genera llaves ECDH firmadas
    priv_ecdh, pub_ecdh = utils.generar_llaves_ecdh()
    pub_ecdh_bytes = utils.serializar_publica(pub_ecdh)
    firma = utils.firmar(pub_ecdh_bytes, priv_ecdsa)

    # envia pub_ECDH + firma
    utils.mandar_datos(conn, pub_ecdh_bytes)
    utils.mandar_datos(conn, firma)
    print('[+] Llaves enviadas al servidor')

    # recibe pub_ECDH + firma
    print('[+] Esperando llaves del servidor')
    pub_ecdh_servidor_bytes = utils.leer_datos(conn)
    firma_servidor = utils.leer_datos(conn)

    # verificar firma del servidor
    if not utils.verificar(pub_ecdh_servidor_bytes, firma_servidor, pub_ecdsa_servidor):
        raise ValueError('Firma del servidor inválida')
    print('[+] Firma del servidor verificada')

    # deriva la llave AES
    pub_ecdh_servidor = utils.deserializar_publica(pub_ecdh_servidor_bytes)
    return utils.derivar_llave(priv_ecdh, pub_ecdh_servidor)


def conectar(host, puerto, priv_ecdsa, pub_ecdsa_servidor):
    conn = crear_socket_cliente(host, puerto)
    with conn:
        print(f'[+] Conectado al servidor {host}:{puerto}')
        try:
            llave_aes = handshake(conn, priv_ecdsa, pub_ecdsa_servidor)
        except ValueError as e:
            print(f'[+] {e} — cerrando conexión')
            return

        print(f'\n[+] Llave AES-256:')
        print(f'{llave_aes.hex()}')


if __name__ == '__main__':
    host   = sys.argv[1]
    puerto = sys.argv[2]
    ruta_privada = sys.argv[3]
    ruta_publica = sys.argv[4]
    priv_ecdsa, pub_ecdsa_servidor = cargar_identidad(ruta_privada, ruta_publica)
    conectar(host, puerto, priv_ecdsa, pub_ecdsa_servidor)
