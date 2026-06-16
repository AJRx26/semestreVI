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


def generar_llave_efimera():
    return ec.generate_private_key(ec.SECP384R1())

def derivar_llaves(shared_key):
    derived = HKDF(
        algorithm=hashes.SHA256(),
        length=64, salt=None,
        info=b'handshake data',
        backend=default_backend()
    ).derive(shared_key)
    return derived[:32], derived[32:]


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


def cifrar(llave, datos, timestamp_entero):
    """
    Cifra un segmento con AES-GCM incluyendo datos autenticados adicionales (AAD).
    timestamp_entero: El tiempo actual como int (ej. int(time.time()))
    """
    # Aseguramos que el timestamp siempre ocupe 8 bytes exactos
    timestamp_bytes = timestamp_entero.to_bytes(8, 'big')
               
    iv = os.urandom(12) # IV estándar de 12 bytes para GCM
    encryptor = Cipher(algorithms.AES(llave), 
                       modes.GCM(iv),
                       backend=default_backend()).encryptor()

    # Autenticamos el contexto (IV y Timestamp) como AAD
    associated_data = iv + timestamp_bytes 
    encryptor.authenticate_additional_data(associated_data)                

    cifrado = encryptor.update(datos)
    cifrado += encryptor.finalize() # Necesario para generar el tag final
    tag = encryptor.tag # El tag de 16 bytes protege todo lo anterior

    # Retornamos el paquete con la estructura que espera el descifrador
    return iv + timestamp_bytes + tag + cifrado


def descifrar(llave, paquete):
    """
    Descifra el paquete con AES-GCM [iv + timestamp_bytes + tag + cifrado].
    """
    iv = paquete[:12]
    timestamp_bytes = paquete[12:20]
    tag = paquete[20:36]
    cifrado = paquete[36:]

    decryptor = Cipher(algorithms.AES(llave), 
        modes.GCM(iv, tag),
        backend=default_backend()).decryptor()

    associated_data = iv + timestamp_bytes
    decryptor.authenticate_additional_data(associated_data)

    try:
        datos = decryptor.update(cifrado)
        datos += decryptor.finalize() # Valida integridad y AAD
    except InvalidTag:
        raise Exception("Error de integridad: el segmento ha sido manipulado.")

    timestamp_del_paquete = int.from_bytes(timestamp_bytes, 'big')
    tiempo_ahora = int(time.time())

    if abs(tiempo_ahora - timestamp_del_paquete) > 7200:
        raise Exception("El segmento ha caducado (más de 2 horas)")
    
    return datos
