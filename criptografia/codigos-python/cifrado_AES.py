#!/usr/bin/env python3

import sys
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import argparse
import base64

CHUNK_SIZE = 1024
BLOCK_SIZE = 16

def generar_padding(padding_size: int) -> bytes:
    """
    Funcion para generar padding de cierta longitud

    padding_size: int
    returns: bytes
    """
    if padding_size < 1 or padding_size > BLOCK_SIZE:
        raise Exception('El tamano de padding es incorrecto')

    byte_len_padding = bytes([padding_size])
    return b'0' * (padding_size - 1) + byte_len_padding


def cifrar(archivo_entrada: str, archivo_salida: str, llave: bytes) -> None:
    """
    Cifrado mediante ECB (no usar, es un ejemplo)

    archivo_entrada: str
    archivo_salida: str
    llave: bytes
    returns: None
    """
    aesCipher = Cipher(algorithms.AES(llave),
                       modes.ECB(),
                       backend = default_backend)
    aesEncryptor = aesCipher.encryptor()


    #Se crea un contexto que abre un recurso mientras lo usa y lo cierra cuando termina
    with open(archivo_salida, 'wb') as salida:
        with open(archivo_entrada, 'rb') as entrada:
            chunk = entrada.read(CHUNK_SIZE)

            #Para evitar tomar un chunk menor a 1024, se usa la siguiente condicion.
            while len(chunk) == CHUNK_SIZE:
                cifrado = aesEncryptor.update(chunk)
                salida.write(cifrado)

                #Medida para evitar un EOF
                try:
                    chunk = entrada.read(CHINK_SIZE)
                except:
                    chunk = b''
                    break

            bytes_finales_cubiertos = len(chunk) % BLOCK_SIZE
            padding_size = BLOCK_SIZE - bytes_finales_cubiertos
            padding = generar_padding(padding_size)
            cifrado = aesEncryptor.update(chunk + padding)
            aesEncryptor.finalize()
            salida.write(cifrado)

if __name__ == '__main__':
