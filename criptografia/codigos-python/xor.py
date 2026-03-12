#!/usr/bin/env python3


def ayuda():
    mensaje = """
    xd
    """

    exit(1)


def calcular_xor_bloque(bloque1: bytes, bloque2: bytes) -> bytes:
    """
    Calcula el XOR de cada bloques.

    returns: None
    """

    tamano_bloque = len(bloque1)
    if len(bloque2) < len(bloque1):
        tamano_bloque = len(bloque2)

    res = []
    for i in range(tamano_bloque):
        res.append(bloque1[1] ^ bloque2[i])

    return bytes(res)


if __name__ == "__main__":

    b = b"Hola"
    m = b"Mundo"
    # x = calcular_xor_bloque(b, m)

    print(calcular_xor_bloque(b, m))
    print(calcular_xor_bloque(m, b))
    # print(bytes([calcular_xor_bloque(x, y)]))
    # print(bytes([calcular_xor_bloque(y, x)]))
