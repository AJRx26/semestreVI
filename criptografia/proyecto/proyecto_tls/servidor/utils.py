"""
utils.py.
Módulo de utileria para manejo de mensajes/cifrado/descifrado en el repositorio.
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os
import time
import hashlib
import os


def _recibir_exacto(sock, n):
    datos = b''
    while len(datos) < n:
        chunk = sock.recv(n - len(datos))
        if not chunk:
            raise ConnectionError("Conexión cerrada")
        datos += chunk
    return datos


def enviar_bytes(sock, data: bytes):
    longitud = len(data).to_bytes(4, 'big')
    sock.sendall(longitud + data)


def recibir_bytes(sock) -> bytes:
    longitud = int.from_bytes(_recibir_exacto(sock, 4), 'big')
    return _recibir_exacto(sock, longitud)


def mandar_mensaje(sock, mensaje: bytes):
    enviar_bytes(sock, mensaje)


def leer_mensaje(sock) -> bytes:
    return recibir_bytes(sock)


def crear_generador_lectura(path_archivo, tam_lectura=4096):
    """
    Lee archivos en pedazos para no saturar la RAM.
    """
    with open(path_archivo, 'rb') as archivo:
        while True:
            contenido = archivo.read(tam_lectura)
            if not contenido:
                break
            yield contenido


def regresar_bytes(path_archivo):
    contenido = ''
    with open(path_archivo, 'rb') as archivo:
        contenido = archivo.read()
    return contenido

def generar_salt():
    """Genera un salt aleatorio de 32 bytes en hexadecimal."""
    return os.urandom(32).hex()

def hashear_password(password, salt):
    """Aplica SHA-512 con salt a una contraseña."""
    return hashlib.sha512((salt + password).encode()).hexdigest()

