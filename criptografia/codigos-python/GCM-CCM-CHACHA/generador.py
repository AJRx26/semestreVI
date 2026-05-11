import random

def float_bytes(numero):
    entero = int(numero * 256)
    return bytes([entero])

def crear_generador_segmentos(semilla, longitud=1024):
    random.seed(semilla)
    while True:
        binario = []
        for b in range(longitud):
            binario.append(float_bytes(random.random()))
        yield b''.join(binario)
