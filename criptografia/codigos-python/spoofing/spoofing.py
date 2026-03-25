#!/usr/bin/env python3

#from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
#from cryptography.hazmat.backends import default_backend
import os
import base64
import argparse

def ayuda():
    mensaje="""
    - Script que realiza un ataque de spoofing a un archivo cifrado en AES-CTR

    - python3 spoofing.py -i archivo_cifrado -o archivo_salida -m texto -x archivo_xml

    - archivo_cifrado: archivo a modificar
    - texto: mensaje que sera agregado
    - archivo_salida: archivo resultante
    - archivo xml: archivo para el offset
    """

def xor(bloque1: bytes, bloque2: bytes) -> bytes:
    """
    Calcula el XOR.

    bloque1: bytes
    bloque2: bytes

    returns: bytes
    """
    # La función zip une los dos bloques de bytes por pares para aplicar XOR a cada par
    resultado = []
    for x, y in zip(bloque1, bloque2):
        resultado.append(x ^ y)
    return bytes(resultado)

def encontrar_bytes(archivo_entrada: str, texto: str ,xml: str) -> bytes:
    """
    Obtiene los bytes de un offset en base a un archivo XML

    archivo_entrada: str
    texto: str
    xml: str

    returns: bytes
    """
    texto_original = "Evil LLC"
    # busca este texto en el archivo cifrado
    objetivo_busqueda = texto_original.encode("utf-8")
    # reemplazara por este texto en el archivo cifrado
    nuevo_mensaje = texto.encode("utf-8")

    with open(xml, "rb") as archivo:
        x = archivo.read()
        # Calcular el desplazamiento
        offset = x.find(objetivo_busqueda)
        # Calcular el tamaño del objetivo
        size = len(objetivo_busqueda)
        print(f"Texto: '{texto_original}' encontrado en {offset} bytes")

    with open(archivo_entrada, "rb") as cifrado:
        y = cifrado.read()
        bytes_cifrados = y[offset : offset + size]
        print(f"Bytes extraídos : {bytes_cifrados.hex()}")

    return bytes_cifrados, offset, nuevo_mensaje

def cifrar(archivo_entrada: str, archivo_salida: str, texto: str, xml: str) -> None:
    """
    Cifra el offset especifico de un archivo

    archivo_entrada: str
    archivo_salida: str
    texto: str
    xml: str

    returns none
    """
    bytes_cifrados, offset, nuevo_mensaje = encontrar_bytes(archivo_entrada, texto, xml)

    texto_original = "Evil LLC"
    bytes_original = texto_original.encode("utf-8")

    if len(bytes_original) != len(nuevo_mensaje):
        print(f"El texto nuevo debe tener {len(bytes_original)} caracteres")
        exit(1)
    else:
        # Se aplica texto_cifrado XOR texto_plano para obtener el keystream
        keystream = xor(bytes_cifrados, bytes_original)
        print(f"Keystream obtenido: {keystream.hex()}")

        # Se aplica keystream XOR nuevo_mensaje para cifrar el mensaje que sera agregado
        bytes_alterados = xor(keystream, nuevo_mensaje)
        print(f"Bytes alterados: {bytes_alterados.hex()}")

        with open(archivo_entrada, "rb") as entrada:
            cifrado = entrada.read()

        # Concatena los bytes cifrados con el cifrado nuevo
        cifrado_alterado = cifrado[:offset] + bytes_alterados + cifrado[offset + len(nuevo_mensaje):]

        with open(archivo_salida, "wb") as salida:
            salida.write(cifrado_alterado)
        print("Archivo guardado")

if __name__ == '__main__':
    all_args = argparse.ArgumentParser()
    all_args.add_argument("-i", "--input", help="Archivo de entrada", required=True)
    all_args.add_argument("-o", "--output", help="Archivo de salida", required=True)
    all_args.add_argument("-m", "--text", help="Texto", required=True)
    all_args.add_argument("-x", "--xml", help="Archivo XML", required=True)
    args = vars(all_args.parse_args())

    cifrar(args["input"], args["output"], args["text"], args["xml"])
