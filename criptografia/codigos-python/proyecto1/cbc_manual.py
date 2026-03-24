#! /usr/bin/env python3
import sys
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import argparse
import base64

#Evitar numeros magicos
CHUNK_SIZE = 1024
BLOCK_SIZE = 16
SIZE_IV = 16
SIZE_HASH = 32
SIZE_ALL = SIZE_HASH + SIZE_IV

def ayuda():
    mensaje="""
    Script que hace implementación manual de AES CBC:
        - Usa modo ECB como base para el cifrado por bloque
        - Usa el padding visto en clase
        - Genera un IV aleatorio al cifrar, se pega al final del archivo
        - Hace comprobación de integridad

    - Modo de uso:
    python3 aes_cbc.py -p OPERACION -i archivo_entrada -o archivo_salida -l llave

    - Argumentos:
        - Operacion: cifrar o descifrar
        - Archivo de entrada
        - Archivo de salida
        - Llave (base 64)
    """
    return 0

def generar_padding(padding_size: int) -> bytes:
    """
    Genera padding de cierta longitud.
    padding_size: int
    returns: bytes
    """
    if padding_size < 1 or padding_size > BLOCK_SIZE:
        raise Exception("El tamaño de padding es incorrecto")
    byte_len_padding = bytes([padding_size])
    return b"0" * (padding_size - 1) + byte_len_padding

def xor(bloque1: bytes, bloque2: bytes) -> bytes:
    """
    Calcula el XOR entre dos bloques.
    returns: bytes
    """
    tam_bloque = len(bloque1)
    if len(bloque2) < len(bloque1):
        tam_bloque = len(bloque2)

    res = []
    for i in range(tam_bloque):
        res.append(bloque1[i] ^ bloque2[i])
    return bytes(res)

def cifrar_chunk_ecb(encryptor, chunk: bytes, bloque_anterior: bytes):
    """
    Cifra un chunk completo aplicando CBC bloque a bloque (16 bytes).
    encryptor
    chunk: bytes
    bloque_anterior: bytes
    returns (chunk_cifrado, ultimo_bloque_cifrado)
    """
    #se escribe en bytes
    resultado = b""
    # range(x, y, z): x marca el inicio, y: marca el final, z: incremento del indice
    for i in range(0, len(chunk), BLOCK_SIZE):
        #toma un chunk desde i (0) hasta (15) dado que el tamaño del bloque es 16
        bloque = chunk[i:i + BLOCK_SIZE]
        # XOR
        bloque_xor = xor(bloque, bloque_anterior)
        # Cifra el chunk con ecb
        cifrado = encryptor.update(bloque_xor)
        #Gurada el bloque cifrado para el siguiente ciclo
        bloque_anterior = cifrado
        resultado += cifrado
    return resultado, bloque_anterior

def descifrar_chunk_ecb(decryptor, chunk: bytes, bloque_anterior: bytes):
    """
    Descifra un chunk completo revirtiendo CBC bloque a bloque (16 bytes).
    encryptor
    chunk: bytes
    bloque_anterior: bytes
    returns (chunk_descifrado, ultimo_bloque_cifrado)
    """
    #se escribe en bytes
    resultado = b""

    # range(x, y, z): x marca el inicio, y: marca el final, z: incremento del indice
    for i in range(0, len(chunk), BLOCK_SIZE):
        #toma un chunk desde i (0) hasta (15) dado que el tamaño del bloque es 16
        bloque = chunk[i:i + BLOCK_SIZE]
        # Descifra el chunk con ecb
        descifrado = decryptor.update(bloque)
        # XOR
        descifrado_xor = xor(descifrado, bloque_anterior)
        #Gurada el bloque cifrado para el siguiente ciclo
        bloque_anterior = bloque
        resultado += descifrado_xor
    return resultado, bloque_anterior

def cifrar(archivo_entrada: str, archivo_salida: str, llave: bytes) -> None:
    """
    Cifra un archivo usando AES-CBC manual.
    archivo_entrada: str
    archivo_salida: str
    llave: bytes
    returns: None
    """
    # Genera IV
    iv = os.urandom(SIZE_IV)
    hasher = hashlib.sha256()

    aesCipher = Cipher(algorithms.AES(llave), modes.ECB(), backend=default_backend())
    aesEncryptor = aesCipher.encryptor()

    bloque_anterior = iv

    with open(archivo_salida, "wb") as salida:
        with open(archivo_entrada, "rb") as entrada:
            chunk = entrada.read(CHUNK_SIZE)

            while len(chunk) == CHUNK_SIZE:
                hasher.update(chunk)
                cifrado, bloque_anterior = cifrar_chunk_ecb(aesEncryptor, chunk, bloque_anterior)
                salida.write(cifrado)
                chunk = entrada.read(CHUNK_SIZE)

            # Último chunk: agregar padding
            hasher.update(chunk)
            bytes_finales_cubiertos = len(chunk) % BLOCK_SIZE
            padding_size = BLOCK_SIZE - bytes_finales_cubiertos
            padding = generar_padding(padding_size)
            chunk_con_padding = chunk + padding
            cifrado, bloque_anterior = cifrar_chunk_ecb(aesEncryptor, chunk_con_padding, bloque_anterior)
            aesEncryptor.finalize()
            salida.write(cifrado)

            # Escribir hash e IV al final
            hash_final = hasher.digest()
            salida.write(hash_final)
            salida.write(iv)

    print("Archivo cifrado")
    print("Hash del archivo:", hash_final.hex())

def descifrar(archivo_entrada: str, archivo_salida: str, llave: bytes) -> None:
    """
    Descifra un archivo usando AES-CBC manual.
    archivo_entrada: str
    archivo_salida: str
    llave: bytes
    returns: None
    """
    hasher = hashlib.sha256()

    aesCipher = Cipher(algorithms.AES(llave), modes.ECB(), backend=default_backend())
    aesDecryptor = aesCipher.decryptor()

    chunk_anterior = None
    contador = 0

    with open(archivo_entrada, "rb") as entrada:
        # Leer IV (últimos 16 bytes)
        # seek() mueve un "puntero" a una pocisión especifica dentro de un archivo abierto.
        # file.seek(desplazamiento, inicio)
            # 0: inicio
            # 2: final del archivo
        entrada.seek(-SIZE_IV, 2)
        iv = entrada.read(SIZE_IV)

        # Leer hash (32 bytes antes del IV)
        entrada.seek(-SIZE_ALL, 2)
        hash_guardado = entrada.read(SIZE_HASH)

        # Tamaño real de los datos cifrados
        tamano = os.path.getsize(archivo_entrada) - SIZE_ALL
        entrada.seek(0)

        with open(archivo_salida, "wb") as salida:
            bloque_anterior = iv

            while contador < tamano:
                bytes_a_leer = min(CHUNK_SIZE, tamano - contador)
                chunk = entrada.read(bytes_a_leer)
                contador += len(chunk)

                descifrado, bloque_anterior = descifrar_chunk_ecb(aesDecryptor, chunk, bloque_anterior)

                if chunk_anterior is not None:
                    salida.write(chunk_anterior)
                    hasher.update(chunk_anterior)

                chunk_anterior = descifrado

            aesDecryptor.finalize()

            # Último bloque: eliminar padding y escribir
            if chunk_anterior is not None:
                tamano_padding = chunk_anterior[-1]
                no_padding = chunk_anterior[:-tamano_padding]
                salida.write(no_padding)
                hasher.update(no_padding)

    # Verificar integridad
    hash_calculado = hasher.digest()
    if hash_calculado == hash_guardado:
        print("Archivo descifrado: archivo NO modificado")
    else:
        print("Archivo descifrado: el archivo fue modificado")
    print("Hash original:", hash_guardado.hex())
    print("Hash nuevo:   ", hash_calculado.hex())

if __name__ == '__main__':
    all_args = argparse.ArgumentParser()
    all_args.add_argument("-p", "--Operacion", help="Aplicar operación, cifrar/descifrar")
    all_args.add_argument("-i", "--input", help="Archivo de entrada", required=True)
    all_args.add_argument("-o", "--output", help="Archivo de salida", required=True)
    all_args.add_argument("-l", "--llave", help="Llave en base64", required=True)
    args = vars(all_args.parse_args())
    operacion = args["Operacion"]

    llave = base64.b64decode(args["llave"])
    if len(llave) != 16:
        print("La llave de entrada debe ser de 16 bytes")
        exit(1)

    if operacion == "cifrar":
        cifrar(args["input"], args["output"], llave)
    else:
        descifrar(args["input"], args["output"], llave)
