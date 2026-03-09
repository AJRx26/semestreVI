import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import argparse
import base64

CHUNK_SIZE = 1024
BLOCK_SIZE = 16


def generar_padding(padding_size: int) -> bytes:
    """
    Función para generar padding de cierta longitud.

    padding_size: int
    returns: bytes
    """
    if padding_size < 1 or padding_size > BLOCK_SIZE:
        raise Exception("El tamaño de padding es incorrecto")

    byte_len_padding = bytes([padding_size])
    return b"0" * (padding_size - 1) + byte_len_padding


def cifrar(archivo_entrada: str, archivo_salida: str, llave: bytes) -> None:
    """
    Cifrado mediante ECB (no usar es ejemplo).

    archivo_entrada: str
    archivo_salida: str
    llave: bytes
    returns: None
    """
    aesCipher = Cipher(algorithms.AES(llave), modes.ECB(), backend=default_backend())
    aesEncryptor = aesCipher.encryptor()

    with open(archivo_salida, "wb") as salida:
        with open(archivo_entrada, "rb") as entrada:
            chunk = entrada.read(CHUNK_SIZE)
            while len(chunk) == CHUNK_SIZE:
                cifrado = aesEncryptor.update(chunk)
                salida.write(cifrado)
                try:
                    chunk = entrada.read(CHUNK_SIZE)
                except:
                    chunk = b""
                    break

            bytes_finales_cubiertos = len(chunk) % BLOCK_SIZE
            padding_size = BLOCK_SIZE - bytes_finales_cubiertos
            padding = generar_padding(padding_size)
            cifrado = aesEncryptor.update(chunk + padding)
            aesEncryptor.finalize()
            salida.write(cifrado)


def descifrar(archivo_entrada: str, archivo_salida: str, llave: bytes) -> None:
    """
    archivo_entrada: str
    archivo_salida: str
    llave: bytes
    returns: None
    """

    # Se crea el descifrador
    aesCipher = Cipher(algorithms.AES(llave), modes.ECB(), backend=default_backend())
    aesDecryptor = aesCipher.decryptor()

    # Guarda el chunk anterior
    chunk_anterior = None

    # Procesa todos los chunk pero no escribe el ultimo hasta eliminar el padding
    with open(archivo_salida, "wb") as salida:
        with open(archivo_entrada, "rb") as entrada:
            chunk = entrada.read(CHUNK_SIZE)
            while len(chunk) == CHUNK_SIZE:
                descifrado = aesDecryptor.update(chunk)

                if chunk_anterior is not None:
                    salida.write(chunk_anterior)

                chunk_anterior = descifrado
                chunk = entrada.read(CHUNK_SIZE)

            # Procesa el ultimo chunk incompleto
            if len(chunk) > 0:
                descifrado = aesDecryptor.update(chunk)

                if chunk_anterior is not None:
                    salida.write(chunk_anterior)
                chunk_anterior = descifrado

            aesDecryptor.finalize()

            # Si el chunk anterior esta vacio, no hay nada que escribir
            if chunk_anterior is None:
                return

            # Obtiene el tamano del padding del ultimo chunk
            tamano_padding = chunk_anterior[-1]
            # Elimina todo el padding del chunk
            no_padding = chunk_anterior[:-tamano_padding]
            salida.write(no_padding)


if __name__ == "__main__":
    all_args = argparse.ArgumentParser()
    all_args.add_argument(
        "-p", "--Operacion", help="Aplicar operación, cifrar/descifrar"
    )
    all_args.add_argument("-i", "--input", help="Archivo de entrada", required=True)
    all_args.add_argument("-o", "--output", help="Archivo de salida", required=True)
    all_args.add_argument("-l", "--llave", help="Llave", required=True)
    args = vars(all_args.parse_args())
    operacion = args["Operacion"]

    # Preparar llave recibida en base64
    llave = base64.b64decode(args["llave"])
    if len(llave) != 16:
        print("La llave de entrada debe ser de 16 bytes")
        exit(1)

    if operacion == "cifrar":
        cifrar(args["input"], args["output"], llave)
    else:
        descifrar(args["input"], args["output"], llave)
