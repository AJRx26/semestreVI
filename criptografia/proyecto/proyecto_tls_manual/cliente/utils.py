"""
utils.py.
Aquí se encuentran las funciones compartidas entre servidor y cliente.
Módulo de utileria para envío/recepción de mensajes,
para cifrado/descifrado y lectura de archivos en el repositorio.
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
    """
    Función para longitud fija, 
    se envían 4 bytes que indican que tan grande es el mensaje real.
    """
    longitud = len(data).to_bytes(4, 'big')
    sock.sendall(longitud + data)


def recibir_bytes(sock) -> bytes:
    """
    Función para longitud fija, 
    se reciben 4 bytes que indican que tan grande es el mensaje real.
    """
    longitud = int.from_bytes(_recibir_exacto(sock, 4), 'big')
    return _recibir_exacto(sock, longitud)


def mandar_mensaje(sock, mensaje: bytes):
    enviar_bytes(sock, mensaje)


def leer_mensaje(sock) -> bytes:
    return recibir_bytes(sock)


# Fase 2: Funciones para el Handshake (ECDHE)

def generar_llave_efimera():
    """
    Función para crear una llave privada efímera usando curvas elípticas.
    """
    return ec.generate_private_key(ec.SECP384R1())

def derivar_llaves(shared_key):
    """
    Se usa el algoritmo HKDF para transformar el secreto compartido.
    Genera dos llaves cruzadas simétricas de 32 bytes. Una para envíar otra para recibir.
    """
    derived = HKDF(
        algorithm=hashes.SHA256(),
        length=64, salt=None,
        info=b'handshake data',
        backend=default_backend()
    ).derive(shared_key)
    return derived[:32], derived[32:]


# FASE 4: Operaciones de repositorio.

def crear_generador_lectura(path_archivo, tam_lectura=4096):
    """
    Lee archivos en pedazos (4096 bytes) para no saturar la RAM.
    """
    with open(path_archivo, 'rb') as archivo:
        while True:
            contenido = archivo.read(tam_lectura)
            if not contenido:
                break
            yield contenido # yield -> hacer una pausa después de leer un pezado
            # se entrega para cifrar y solo se lee el siguiente pedazo cuando se solicita


def regresar_bytes(path_archivo):
    contenido = ''
    with open(path_archivo, 'rb') as archivo:
        contenido = archivo.read()
    return contenido


def cifrar(llave, datos, timestamp_entero):
    """
    Cifra un segmento con AES-GCM incluyendo datos autenticados adicionales (AAD).
    Los pasos son:
    1. Convierte el tiempo a 8 bytes exactos para el AAD.
    2. Genera un IV de 12 bytes único.
    3. Cifra con AES-GCM.
    Return: [IV] + [Timestamp] + [TAG] + [Cifrado]
    """
    # Aseguramos que el timestamp siempre ocupe 8 bytes exactos
    timestamp_bytes = timestamp_entero.to_bytes(8, 'big')
               
    iv = os.urandom(12) # IV estándar de 12 bytes para GCM
    encryptor = Cipher(algorithms.AES(llave), # llave_sesion_enviar
                       modes.GCM(iv),
                       backend=default_backend()).encryptor()

    # Autenticamos datos (IV y Timestamp) como AAD
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
    Los pasos son:
    1. Extrae cada componente con rebanadas precisas.
    2. Configura modo GCM usando el IV y el TAG.
    3. Verifica timestamp no sea mayor a 7200 seg respecto al reloj local
    4. Si TAG no conincide en finalize() lanza excepción.
    """
    iv = paquete[:12] # 12 bytes
    timestamp_bytes = paquete[12:20] # 8 bytes
    tag = paquete[20:36] # 16 bytes
    cifrado = paquete[36:] # contenido restante

    decryptor = Cipher(algorithms.AES(llave), # llave_sesion_recibir
        modes.GCM(iv, tag),
        backend=default_backend()).decryptor()

    associated_data = iv + timestamp_bytes
    decryptor.authenticate_additional_data(associated_data)

    try:
        datos = decryptor.update(cifrado) # descifra los datos
        datos += decryptor.finalize() # Recalcula el tag con los datos recibidos y lo compara
    except InvalidTag: # si el IV o el Timestamp fueron alterados lanza excepción
        raise Exception("[ERROR] Error de integridad: el segmento ha sido manipulado.")

    # Toma los 8 bytes extraídos y los transforma en número entero para python
    timestamp_del_paquete = int.from_bytes(timestamp_bytes, 'big') # big --> significativo al menos
    tiempo_ahora = int(time.time()) # Pide al SO la hora actual en formato Unix

    # resta -> diferencia en segundos entre: momento en que se generó paquete y momento en que servidor procesa
    if abs(tiempo_ahora - timestamp_del_paquete) > 7200: # abs -> convertir número negativo en positivo
        raise Exception("El segmento ha caducado (más de 2 horas)")
    
    return datos


def generar_salt():
    """Genera un salt aleatorio de 32 bytes en hexadecimal."""
    return os.urandom(32).hex()

def hashear_password(password, salt):
    """Aplica SHA-512 con salt a una contraseña."""
    #salt + password
    return hashlib.sha512((salt + password).encode()).hexdigest()
