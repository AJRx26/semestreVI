#! /usr/bin/env python3

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
import argparse

CHUNK_SIZE = 1024
SIZE = 16
SIZE_KEY = 32

def ayuda():
    mensaje="""
    - Script que cifra y descifra un archivo con AES-CTR

    python3 aes_ctr.py -p OPERACION -i archivo_entrada -o archivo_salida [-l llave]

    - Argumentos:
        - Operacion: cifrar o descifrar
        - Archivo de entrada
        - Archivo de salida
        - Llave (base64): Opcional solo para la operacion descifrar
    """

def cifrar(archivo_entrada: str, archivo_salida: str) -> None:
    """
    - CIfra un archivo usando AES-CTR

    archivo_entrada: str
    archivo_salida: str

    returns: None

    """
    # Crear llave aleatoria
    key = os.urandom(SIZE_KEY)
    # Crear nonce
    nonce = os.urandom(SIZE)

    # Crear cifrador
    aes_context = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
    encryptor = aes_context.encryptor()

    with open(archivo_entrada, "rb") as entrada:
        with open(archivo_salida, "wb") as salida:
            while True:
                chunk = entrada.read(CHUNK_SIZE)
                if not chunk:
                    break
                salida.write(encryptor.update(chunk))
            salida.write(encryptor.finalize())
            # Se agrega el nonce al final del archivo
            salida.write(nonce)

    print("Archivo cifrado")
    print("Llave del archivo cifrado: ", base64.b64encode(key).decode())

def descifrar(archivo_entrada: str, archivo_salida: str, key: bytes) -> None:
    """
    - Descifra un archivo uando AES-CTR

    archivo_entrada: str
    archivo_salida: str
    key: bytes

    returns: None
    """

    with open(archivo_entrada, "rb") as entrada:
        # Se pocisiona 16 bytes antes del final
        entrada.seek(-SIZE, 2)
        # Recoje el nonce
        nonce = entrada.read(SIZE)

        size = os.path.getsize(archivo_entrada) - SIZE
        entrada.seek(0)

        # Crear descifrador
        aes_context = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
        decryptor = aes_context.decryptor()

        with open(archivo_salida, "wb") as salida:
            bytes_restantes = size
            while bytes_restantes > 0:
                # Toma los ultimos bytes
                chunk = entrada.read(min(CHUNK_SIZE, bytes_restantes))
                salida.write(decryptor.update(chunk))
                bytes_restantes -= len(chunk)
            salida.write(decryptor.finalize())

    print("Archivo descifrado correctamente")

if __name__ == "__main__":
    all_args = argparse.ArgumentParser()
    all_args.add_argument("-p", "--Operacion", help="Aplicar operación, cifrar/descifrar")
    all_args.add_argument("-i", "--input", help="Archivo de entrada", required=True)
    all_args.add_argument("-o", "--output", help="Archivo de salida", required=True)
    all_args.add_argument("-l", "--llave", help="Llave en base64", required=False)
    args = vars(all_args.parse_args())
    operacion = args["Operacion"]

    if operacion == "cifrar":
        cifrar(args["input"], args["output"])
    else:
        llave = base64.b64decode(args["llave"])
        if len(llave) != SIZE_KEY:
            print("La llave de entrada debe ser de 32 bytes")
            exit(1)
        descifrar(args["input"], args["output"], llave)
