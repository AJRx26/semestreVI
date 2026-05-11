#!/usr/bin/env python3

import os
import random
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import argparse

#generador de segmentos
def float_bytes(numero):
    entero = int(numero * 256)
    return bytes([entero])

def crear_generador_segmentos(semilla, longitud=1024):
    random.seed(semilla)
    while True:
        binario = []
        for _ in range(longitud):
            binario.append(float_bytes(random.random()))
        yield b''.join(binario)

#cifrados y descifrados
def gcm(segmentos):
    #Cifra y descifra cada segmento con AES-GCM
    key = AESGCM.generate_key(bit_length=128)
    aad = b"authenticate and unencrypted data"
    aesgcm = AESGCM(key)

    cifrados    = []
    nonces      = []
    t_cifrado   = 0.0
    t_descifrado = 0.0

    for data in segmentos:
        nonce = os.urandom(12)
        t0 = time.perf_counter() #devuelve un valor float que representa el tiempo transcurrido en segundos desde un punto de referencia
        ct = aesgcm.encrypt(nonce, data, aad)
        t_cifrado += time.perf_counter() - t0 #hace el calculo del tiempo transcurrido restando los valores de time.perf_counter()
        cifrados.append(ct)
        nonces.append(nonce)

#junta cada segmento cifrado con su respectivo nonce 
    for ct, nonce in zip(cifrados, nonces):
        t0 = time.perf_counter()
        aesgcm.decrypt(nonce, ct, aad)
        t_descifrado += time.perf_counter() - t0

    return t_cifrado, t_descifrado


def ccm(segmentos):
    #Cifra y descifra cada segmento con AES-CCM
    key = AESCCM.generate_key(bit_length=128)
    aad = b"authenticate and unencrypted data"
    aesccm = AESCCM(key)

    cifrados     = []
    nonces       = []
    t_cifrado    = 0.0
    t_descifrado = 0.0

    for data in segmentos:
        nonce = os.urandom(7)
        t0 = time.perf_counter()
        ct = aesccm.encrypt(nonce, data, aad)
        t_cifrado += time.perf_counter() - t0
        cifrados.append(ct)
        nonces.append(nonce)

    for ct, nonce in zip(cifrados, nonces):
        t0 = time.perf_counter()
        aesccm.decrypt(nonce, ct, aad)
        t_descifrado += time.perf_counter() - t0

    return t_cifrado, t_descifrado


def chacha(segmentos):
    key = ChaCha20Poly1305.generate_key()
    aad = b"authenticate and unencrypted data"
    chacha = ChaCha20Poly1305(key)

    cifrados     = []
    nonces       = []
    t_cifrado    = 0.0
    t_descifrado = 0.0

    for data in segmentos:
        nonce = os.urandom(12)
        t0 = time.perf_counter()
        ct = chacha.encrypt(nonce, data, aad)
        t_cifrado += time.perf_counter() - t0
        cifrados.append(ct)
        nonces.append(nonce)

    for ct, nonce in zip(cifrados, nonces):
        t0 = time.perf_counter()
        chacha.decrypt(nonce, ct, aad)
        t_descifrado += time.perf_counter() - t0

    return t_cifrado, t_descifrado

def imprimir_resultado(nombre, t_cifrado, t_descifrado):
    print(f"{nombre}")
    print(f"- Cifrado: {t_cifrado:.3f} s")
    print(f"- Descifrado: {t_descifrado:.3f} s")

if __name__ == "__main__":
    all_args = argparse.ArgumentParser()
    all_args.add_argument("-s", "--segmento", help="Tamaño de segmento en bytes")
    all_args.add_argument("-n", "--numero", help="Cantidad de segmentos")
    #all_args.add_argument("-S", "--semilla", help="Semilla fija")
    args = vars(all_args.parse_args())
    segmento_size = int(args["segmento"])
    num_segmentos = int(args["numero"])
    semilla = 261104

    # Generar segmentos una vez y reutilizarlos
    def obtener_segmentos():
        gen = crear_generador_segmentos(semilla, segmento_size)
        return [next(gen) for _ in range(num_segmentos)]

    segmentos = obtener_segmentos() #lista compartida

    t_gcm_c, t_gcm_d = gcm(segmentos)
    t_ccm_c, t_ccm_d = ccm(segmentos)
    t_chacha_c, t_chacha_d = chacha(segmentos)

    # Resultados
    imprimir_resultado("AES-GCM", t_gcm_c, t_gcm_d)
    imprimir_resultado("AES-CCM", t_ccm_c, t_ccm_d)
    imprimir_resultado("ChaCha20-Poly1305", t_chacha_c, t_chacha_d)
