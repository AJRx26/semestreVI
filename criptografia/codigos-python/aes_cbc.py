#! /usr/bin/env python3

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import base64
import argparse

CHUNK_SIZE = 1024
SIZE = 16

def ayuda():
    mensaje = """
    - Script que cifra y descifrar un archivo usando AES-CBC (de manera automatica)

    Uso: python3 aes_cbc_automatico.py -p OPERACION -i archivo_entrada -o archivo_salida -l llave -v iv

    - Argumentos:
        - Operacion
        - archivo de entrada
        - archivo de salida
        - llave (base64)
        - iv (base64)
    """

    """
    padder = padding.PKCS7(128).padder()
    unpadder = padding.PKCS7(128).unpadder()

    m = padder.update(AlgunBinario) # Solo llena el buffer
    m = padder.finalize() #aplica padding al resto

    m2 = unpadder.update(AlgunBinario)
    m2 = unpadder.finalize() #quita el padding
    """

def cifrar(archivo_entrada: str, archivo_salida: str, llave: bytes, iv: bytes) -> None:
    """
    - Cifra usando AES-CBC

    - archivo_entrada: str
    - archivo_ salida: str
    - key: bytes
    - iv: bytes

    - Returns None
    """

    # Crear cifrador
    aesCipher = Cipher(algorithms.AES(llave), modes.CBC(iv), backend=default_backend())
    aesEncryptor = aesCipher.encryptor()

    # Crear padder
    padder = padding.PKCS7(128).padder()

    with open(archivo_entrada, "rb") as entrada:
        with open(archivo_salida, "wb") as salida:
            while True:
                chunk = entrada.read(CHUNK_SIZE)
                if not chunk:
                    m = padder.finalize() #aplica padding al resto
                    salida.write(aesEncryptor.update(m))
                    salida.write(aesEncryptor.finalize())
                    break
                m = padder.update(chunk)
                salida.write(aesEncryptor.update(m))
    print("Archivo cifrado")

def descifrar(archivo_entrada: str, archivo_salida: str, llave: bytes, iv: bytes) -> None:
    """
    - Descifra usando AES-CBC

    - archivo_entrada: str
    - archivo_ salida: str
    - key: bytes
    - iv: bytes

    - Returns None
    """

    # Crear descifrador
    aesCipher = Cipher(algorithms.AES(llave), modes.CBC(iv), backend=default_backend())
    aesDecryptor = aesCipher.decryptor()

    # Crear padder
    unpadder = padding.PKCS7(128).unpadder()

    with open(archivo_entrada, "rb") as entrada:
        with open(archivo_salida, "wb") as salida:
            while True:
                chunk = entrada.read(CHUNK_SIZE)
                if not chunk:
                    descifrado = aesDecryptor.finalize()
                    salida.write(unpadder.update(descifrado))
                    salida.write(unpadder.finalize()) #quita padding
                    break
                descifrado = aesDecryptor.update(chunk)
                salida.write(unpadder.update(descifrado))
    print("Archivo descifrado")


if __name__ == "__main__":
    all_args = argparse.ArgumentParser()
    all_args.add_argument("-p", "--Operacion", help="Aplicar operación, cifrar/descifrar")
    all_args.add_argument("-i", "--input", help="Archivo de entrada", required=True)
    all_args.add_argument("-o", "--output", help="Archivo de salida", required=True)
    all_args.add_argument("-l", "--llave", help="Llave en base64", required=True)
    all_args.add_argument("-v", "--iv", help="IV en base64", required=True)
    args = vars(all_args.parse_args())
    operacion = args["Operacion"]

    llave = base64.b64decode(args["llave"])
    if len(llave) != 32:
        print("La llave de entrada debe ser de 32 bytes")
        exit(1)

    iv = base64.b64decode(args["iv"])
    if len(iv) != 16:
        print("El IV de entrada debe ser de 16 bytes")
        exit(1)

    if operacion == "cifrar":
        cifrar(args["input"], args["output"], llave, iv)
    else:
        descifrar(args["input"], args["output"], llave, iv)
