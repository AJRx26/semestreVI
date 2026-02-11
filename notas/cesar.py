#!/usr/bin/env python3


def cifrar(path_entrada: str, shift: int, path_salida: str) -> None:
    """
    Cifrar el archivo de entrada y lo guarda cifrado en la ruta destino.

    path_entrada: str
    path_salida: str
    shift: int
    returns: Nono
    """
    # for chunk in open(path_entrada, "rb"):
    # print(chunk)
    # print(len(chunk))
    with open(path_salida, "wb") as salida:
        for chunk in open(path_entrada, "rb"):
            chunk_cifrado = []
            for byte in chunk:
                print(byte)
                byte_cifrado = (byte + shift) % 256
                chunk_cifrado.append(byte_cifrado)
                # print(len(byte))
            salida.write(bytes(chunk_cifrado))


path_entrada = "/tmp/hola.txt"
path_salida = "/tmp/cifrado.bin"
shift = int(611)

cifrar(path_entrada, shift, path_salida)
