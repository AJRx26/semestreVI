"""
servidor.py  —  Chat seguro: servidor

Cambios respecto al original:
  1. Al conectarse cada cliente, éste envía sus llaves (AES + MAC) en claro
     (bootstrapping no seguro, según el enunciado).  El servidor responde "ACK".
  2. Cuando recibe un mensaje protegido de c_i, lo descifra y verifica el MAC
     con las llaves de c_i.
  3. Antes de hacer broadcast a cada c_j, re-cifra el plaintext con las llaves
     propias de c_j y aplica Encrypt-then-MAC.

Uso:
    python3 servidor.py <puerto>
"""

import socket
import threading
import sys
import json
import base64

import mensajes
from crypto_utils import desempaquetar, empaquetar

# Almacena para cada socket cliente: (key_aes, key_mac)
llaves_clientes: dict[socket.socket, tuple[bytes, bytes]] = {}
lock_clientes = threading.Lock()


def crear_socket_servidor(puerto: int) -> socket.socket:
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(('', puerto))
    return servidor


def recibir_llaves(cliente: socket.socket) -> tuple[bytes, bytes]:
    """
    Espera el paquete inicial del cliente con sus llaves:
        JSON  { "aes": "<b64>", "mac": "<b64>" }
    Responde "ACK".
    """
    raw = mensajes.leer_mensaje(cliente)
    datos = json.loads(raw.decode('utf-8'))
    key_aes = base64.b64decode(datos["aes"])
    key_mac = base64.b64decode(datos["mac"])
    mensajes.mandar_mensaje(cliente, b"ACK")
    print(f"[+] Llaves recibidas de {cliente.getpeername()}")
    return key_aes, key_mac


def broadcast(plaintext: bytes, origen: socket.socket) -> None:
    """
    Envía el plaintext a todos los clientes (excepto el origen),
    cifrado + MAC con las llaves propias de cada destinatario.
    """
    with lock_clientes:
        destinatarios = [(c, llaves) for c, llaves in llaves_clientes.items()
                         if c is not origen]

    for cliente, (key_aes, key_mac) in destinatarios:
        try:
            paquete = empaquetar(plaintext, key_aes, key_mac)
            mensajes.mandar_mensaje(cliente, paquete)
        except Exception as e:
            print(f"[-] Error enviando a {cliente.getpeername()}: {e}")


def atencion(cliente: socket.socket) -> None:
    """Hilo de atención para un cliente."""
    try:
        key_aes, key_mac = recibir_llaves(cliente)
        with lock_clientes:
            llaves_clientes[cliente] = (key_aes, key_mac)

        while True:
            paquete = mensajes.leer_mensaje(cliente)

            # Mensaje de salida
            if paquete.strip() == b'exit':
                print(f"[-] Cliente {cliente.getpeername()} desconectado")
                break

            # Descifrar y verificar MAC del mensaje entrante
            try:
                plaintext = desempaquetar(paquete, key_aes, key_mac)
            except ValueError as e:
                print(f"[!] {e} — mensaje descartado de {cliente.getpeername()}")
                continue

            print(f"[servidor] Mensaje de {cliente.getpeername()}: {plaintext.decode('utf-8', errors='replace')}")
            broadcast(plaintext, origen=cliente)

    except (ConnectionResetError, BrokenPipeError, OSError):
        print(f"[-] Conexión perdida con {cliente.getpeername()}")
    finally:
        with lock_clientes:
            llaves_clientes.pop(cliente, None)
        cliente.close()


def escuchar(servidor: socket.socket) -> None:
    servidor.listen(5)
    print("[*] Servidor escuchando…")
    while True:
        cliente, addr = servidor.accept()
        print(f"[+] Nuevo cliente conectado: {addr}")
        hilo = threading.Thread(target=atencion, args=(cliente,), daemon=True)
        hilo.start()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <puerto>")
        sys.exit(1)

    servidor = crear_socket_servidor(int(sys.argv[1]))
    escuchar(servidor)
