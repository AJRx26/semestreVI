"""
cliente.py  —  Chat seguro: cliente

Cambios respecto al original:
  1. Al conectarse, lee su archivo de llaves y las envía al servidor en claro.
     Espera un "ACK" de confirmación.
  2. Cada mensaje saliente se cifra con AES-CTR y se protege con HMAC
     (esquema Encrypt-then-MAC) antes de enviarlo.
  3. Los mensajes entrantes (broadcast del servidor) se verifican y descifran
     con las llaves propias del cliente.

Uso:
    python3 cliente.py <host> <puerto> <archivo_llaves>

Ejemplo:
    python3 cliente.py 127.0.0.1 9000 llaves_c1.txt
"""

import socket
import threading
import sys
import json
import base64

import mensajes
from crypto_utils import cargar_llaves, empaquetar, desempaquetar


def conectar_servidor(host: str, puerto: int) -> socket.socket:
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((host, puerto))
        return cliente
    except Exception as e:
        print(f"Servidor inalcanzable: {e}")
        sys.exit(1)


def enviar_llaves(cliente: socket.socket, key_aes: bytes, key_mac: bytes) -> None:
    """
    Envía las llaves al servidor en formato JSON y espera el ACK.
    (Bootstrapping no seguro, por diseño del enunciado.)
    """
    payload = json.dumps({
        "aes": base64.b64encode(key_aes).decode(),
        "mac": base64.b64encode(key_mac).decode(),
    }).encode('utf-8')
    mensajes.mandar_mensaje(cliente, payload)

    ack = mensajes.leer_mensaje(cliente)
    if ack != b"ACK":
        print(f"[!] Respuesta inesperada del servidor: {ack}")
        sys.exit(1)
    print("[*] Llaves aceptadas por el servidor. ¡Conexión segura!")


def leer_mensajes(cliente: socket.socket, key_aes: bytes, key_mac: bytes) -> None:
    """Hilo receptor: verifica MAC y descifra cada mensaje entrante."""
    while True:
        try:
            paquete = mensajes.leer_mensaje(cliente)
            plaintext = desempaquetar(paquete, key_aes, key_mac)
            print(f"\r--> {plaintext.decode('utf-8', errors='replace')}")
            print("Mensaje: ", end='', flush=True)
        except ValueError as e:
            print(f"\r[!] Mensaje descartado — {e}")
        except (ConnectionResetError, BrokenPipeError, OSError):
            print("\r[!] Conexión cerrada por el servidor")
            break


def enviar_mensaje_loop(cliente: socket.socket, key_aes: bytes, key_mac: bytes) -> None:
    """Bucle principal del hilo emisor: cifra y envía cada mensaje."""
    while True:
        try:
            texto = input("Mensaje: ")
        except EOFError:
            break

        if texto.strip() == "exit":
            mensajes.mandar_mensaje(cliente, b"exit")
            break

        plaintext = texto.encode('utf-8')
        paquete   = empaquetar(plaintext, key_aes, key_mac)
        mensajes.mandar_mensaje(cliente, paquete)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(f"Uso: {sys.argv[0]} <host> <puerto> <archivo_llaves>")
        sys.exit(1)

    host, puerto, archivo_llaves = sys.argv[1], int(sys.argv[2]), sys.argv[3]

    key_aes, key_mac = cargar_llaves(archivo_llaves)
    cliente = conectar_servidor(host, puerto)

    enviar_llaves(cliente, key_aes, key_mac)

    hilo_rx = threading.Thread(target=leer_mensajes, args=(cliente, key_aes, key_mac), daemon=True)
    hilo_rx.start()

    enviar_mensaje_loop(cliente, key_aes, key_mac)
    cliente.close()
