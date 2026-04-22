"""
mensajes.

Módulo utileria para manejo de mensajes de chat
"""


import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend


DELIMITADOR = b'\r\n'
# Cifrado de mensajes usando CTR
def cifrar_mensaje(mensaje, llave_cifrado):
    nonce = os.urandom(16)
    cipher = Cipher(algorithms.AES(llave_cifrado), modes.CTR(nonce),backend=default_backend())
    encryptor = cipher.encryptor()
    return nonce, encryptor.update(mensaje) + encryptor.finalize()

def descifrar_mensaje(nonce, mensaje_cifrado, llave_cifrado):
    cipher = Cipher(algorithms.AES(llave_cifrado), modes.CTR(nonce),backend=default_backend())
    decryptor = cipher.decryptor()
    return decryptor.update(mensaje_cifrado) + decryptor.finalize()

# Funciones para mac (man aqui lo hice con hmac pero se puede hacer con cmac asi que no se cual prefieras )
def generar_mac(mensaje, llave_mac):
    h = hmac.HMAC(llave_mac, hashes.SHA256(), backend=default_backend())
    h.update(mensaje)
    return h.finalize()

def verificar_mac(mensaje, mac, llave_mac):
    h = hmac.HMAC(llave_mac, hashes.SHA256(), backend=default_backend())
    h.update(mensaje)
    try:
        h.verify(mac)
        return True
    except:
        return False

def quitar_delimitador(mensaje):
    """
    Limpia un mensaje para que no tenga delemitador.

    Keyword Arguments:
    mensaje -- 
    returns: bytes
    """
    if not mensaje.endswith(DELIMITADOR):
        return mensaje
    return mensaje[:-len(DELIMITADOR)]


def leer_mensaje(socket, llave_cifrado, llave_mac):
    """
    Permite leer un mensaje de longitud arbitraria, utilizando delimitadores de mensaje.

    Keyword Arguments:
    socket de cliente
    returns: bytes
    """
    chunk = socket.recv(1024)
    mensaje = b''
    while not chunk.endswith(DELIMITADOR):
        mensaje += chunk
        chunk = socket.recv(1024)
    mensaje += chunk
    #esta parte es para verificar el mac y descifrar el mensaje, si el mac no coincide se lanza una excepcion
    #creo que puede haber otra forma de manejar esto pero ya tengo sueño
    if not verificar_mac(mensaje=mensaje[:-len(DELIMITADOR)-32], mac=mensaje[-len(DELIMITADOR)-32:-len(DELIMITADOR)], llave_mac=llave_mac):
        raise Exception('MAC no coincide, mensaje alterado')
    
    mensaje_descifrado = descifrar_mensaje(iv=mensaje[:16], mensaje_cifrado=mensaje[16:-len(DELIMITADOR)-32], llave_cifrado=llave_cifrado)
    return quitar_delimitador(mensaje_descifrado)


def mandar_mensaje(socket, mensaje, llave_cifrado, llave_mac):
    """
    Manda un mensaje tomando en cuenta el delimitador.

    Keyword Arguments:
    socket es el socket de servidor o cliente destino
    mensaje bytes de mensaje 
    returns: None
    """
    nonce, mensaje_cifrado = cifrar_mensaje(mensaje, llave_cifrado)
    #aqui tengo duda de si solo usamos el mensaje cifrado para generar el mac o si usamos el iv + mensaje cifrado,
    #ya alrato me dices que prefieres
    mac = generar_mac(mensaje_cifrado, llave_mac)
    socket.send(nonce + mensaje_cifrado + mac + DELIMITADOR)
