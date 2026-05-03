import sys
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import argparse
import base64

chunk_size = 1024
BLOCK_SIZE = 16

def generar_padding(padding_size: int) -> bytes:
    """
    Función para generar padding de x longitud.

    padding_size: int
    returns: bytes 
    """
    if padding_size < 1  or padding_size > BLOCK_SIZE:
        raise Exception('El tamaño de padding es incorrecto')

    byte_len_padding = bytes([padding_size])
    return b'0' * (padding_size - 1) + byte_len_padding

def cifrar_bmp(archivo_entrada: str, archivo_salida: str ,llave : bytes) -> None:
    """
    Funcion para cifrar el archivo BMP usando ECB, ignorando los primeros 54 bytes.
    Este script esta basado en otro script realizado en clase.

    archivo_entrada: str
    archivo_salida: str
    llave: bytes

    returns: None
    """

    encabezado = 54

    # Se crea el cifrador
    aesCipher = Cipher(algorithms.AES(llave), modes.ECB(), backend=default_backend())
    aesEncryptor = aesCipher.encryptor()

    with open(archivo_entrada, 'rb') as entrada:
        # Se escriben los primeros 54 bytes
        encabezado = entrada.read(encabezado)
        chunk = entrada.read(chunk_size)
        with open(archivo_salida, 'wb') as salida:
            salida.write(encabezado)
            while len(chunk) == chunk_size:
                cifrado = aesEncryptor.update(chunk)   
                salida.write(cifrado)
                chunk = entrada.read(chunk_size)

            bytes_finales_cubiertos = len(chunk) % BLOCK_SIZE
            padding_size = BLOCK_SIZE - bytes_finales_cubiertos
            padding = generar_padding(padding_size)
            cifrado = aesEncryptor.update(chunk + padding)
            aesEncryptor.finalize()
            salida.write(cifrado)

if __name__ == '__main__':
    all_args =  argparse.ArgumentParser()
    all_args.add_argument("-i", "--input", help="Archivo de entrada", required=True)
    all_args.add_argument("-o", "--output", help="Archivo de salida", required=True)
    all_args.add_argument("-l", "--llave", help="Llave", required=True)
    args = vars(all_args.parse_args())

    llave = base64.b64decode(args['llave'])
    if len(llave) != 16:
        print('La llave de entrada debe ser de 16 bytes')
        exit(1)

    cifrar_bmp(args['input'], args['output'], llave)
