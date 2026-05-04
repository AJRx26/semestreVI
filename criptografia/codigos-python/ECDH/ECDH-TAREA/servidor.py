#!/usr/bin/env python3

import socket
import sys
import utils


def crear_socket_servidor(puerto):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('', int(puerto)))
    return servidor

# carga las llaves ECDSA del servidor y la pública del cliente
def cargar_identidad(ruta_privada, ruta_publica):
    print('[*] Cargando llaves ECDSA')
    priv_ecdsa = utils.desserializar_privada(ruta_privada)
    pub_ecdsa_cliente = utils.desserializar_publica_pem(ruta_publica)
    print('[+] Llaves ECDSA cargadas')
    return priv_ecdsa, pub_ecdsa_cliente


def handshake(cliente, priv_ecdsa, pub_ecdsa_cliente):
    """
    1. Recibe pub_ECDH + firma del cliente
    2. Verifica la firma
    3. Envía el pub_ECDH + firma
    4. Deriva y retorna la llave AES-256
    """

    # genera llaves ECDH firmardas
    priv_ecdh, pub_ecdh = utils.generar_llaves_ecdh()
    pub_ecdh_bytes = utils.serializar_publica(pub_ecdh)
    firma = utils.firmar(pub_ecdh_bytes, priv_ecdsa)

    # recibe pub_ECDH + firma del cliente
    print('[+] Esperando llaves del cliente')
    pub_ecdh_cliente_bytes = utils.leer_datos(cliente)
    firma_cliente = utils.leer_datos(cliente)

    # verifica firma del cliente
    if not utils.verificar(pub_ecdh_cliente_bytes, firma_cliente, pub_ecdsa_cliente):
        raise ValueError('Firma del cliente invalida')
    print('[+] Firma del cliente verificada')

    # envia pub_ECDH + firma al cliente
    utils.mandar_datos(cliente, pub_ecdh_bytes)
    utils.mandar_datos(cliente, firma)
    print('[+] Llaves enviadas al cliente')

    # deriva la llave AES
    pub_ecdh_cliente = utils.deserializar_publica(pub_ecdh_cliente_bytes)
    return utils.derivar_llave(priv_ecdh, pub_ecdh_cliente)


def escuchar(servidor, priv_ecdsa, pub_ecdsa_cliente):
    servidor.listen(1)
    print('[+] Esperando conexión')

    cliente, addr = servidor.accept()
    with cliente:
        print(f'[+] Cliente conectado desde {addr}')
        try:
            llave_aes = handshake(cliente, priv_ecdsa, pub_ecdsa_cliente)
        except ValueError as e:
            print(f'[+] {e} — cerrando conexión')
            return

        print(f'[+] Llave AES-256:')
        print(f'{llave_aes.hex()}')


if __name__ == '__main__':
    puerto = sys.argv[1]
    ruta_privada = sys.argv[2]
    ruta_publica = sys.argv[3]
    priv_ecdsa, pub_ecdsa_cliente = cargar_identidad(ruta_privada, ruta_publica)
    servidor = crear_socket_servidor(puerto)
    escuchar(servidor, priv_ecdsa, pub_ecdsa_cliente)
