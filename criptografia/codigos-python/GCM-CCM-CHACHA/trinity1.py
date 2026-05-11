#!/usr/bin/env python3

import os
import random
import time
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, AESCCM, ChaCha20Poly1305


# ── Generador de segmentos (visto anteriormente) ──────────────────────────────

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


# ── Funciones de benchmark ────────────────────────────────────────────────────

def benchmark_gcm(segmentos):
    """Cifra y descifra cada segmento con AES-GCM. Retorna (t_cifrado, t_descifrado)."""
    key   = AESGCM.generate_key(bit_length=128)
    aad   = b"aad"
    aesgcm = AESGCM(key)

    cifrados    = []
    nonces      = []
    t_cifrado   = 0.0
    t_descifrado = 0.0

    for data in segmentos:
        nonce = os.urandom(12)
        t0 = time.perf_counter()
        ct = aesgcm.encrypt(nonce, data, aad)
        t_cifrado += time.perf_counter() - t0
        cifrados.append(ct)
        nonces.append(nonce)

    for ct, nonce in zip(cifrados, nonces):
        t0 = time.perf_counter()
        aesgcm.decrypt(nonce, ct, aad)
        t_descifrado += time.perf_counter() - t0

    return t_cifrado, t_descifrado


def benchmark_ccm(segmentos):
    """Cifra y descifra cada segmento con AES-CCM. Retorna (t_cifrado, t_descifrado)."""
    key    = AESCCM.generate_key(bit_length=128)
    aad    = b"aad"
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


def benchmark_chacha(segmentos):
    """Cifra y descifra cada segmento con ChaCha20-Poly1305. Retorna (t_cifrado, t_descifrado)."""
    key    = ChaCha20Poly1305.generate_key()
    aad    = b"aad"
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


# ── Utilidades de presentación ────────────────────────────────────────────────

def imprimir_resultado(nombre, t_cifrado, t_descifrado, num_segmentos, tam_segmento):
    total_bytes = num_segmentos * tam_segmento
    print(f"\n{'─'*40}")
    print(f"  {nombre}")
    print(f"{'─'*40}")
    print(f"  Cifrado    : {t_cifrado:.6f} s")
    print(f"  Descifrado : {t_descifrado:.6f} s")
    print(f"  Total      : {t_cifrado + t_descifrado:.6f} s")
    print(f"  Throughput : {total_bytes / (t_cifrado + t_descifrado) / 1_000_000:.2f} MB/s")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Parámetros
    try:
        tam_segmento  = int(input("Tamaño de segmento (bytes): "))
        num_segmentos = int(input("Número de segmentos      : "))
    except ValueError:
        print("Error: ingresa números enteros válidos.")
        return

    semilla = 42  # semilla fija → los 3 algoritmos procesan exactamente los mismos datos

    print(f"\nProcesando {num_segmentos} segmentos de {tam_segmento} bytes "
          f"({num_segmentos * tam_segmento / 1_000:.1f} KB en total)...")

    # Generar segmentos UNA vez y reutilizarlos en los 3 algoritmos
    def obtener_segmentos():
        gen = crear_generador_segmentos(semilla, tam_segmento)
        return [next(gen) for _ in range(num_segmentos)]

    segmentos = obtener_segmentos()   # lista compartida

    # Benchmarks
    t_gcm_c,    t_gcm_d    = benchmark_gcm(segmentos)
    t_ccm_c,    t_ccm_d    = benchmark_ccm(segmentos)
    t_chacha_c, t_chacha_d = benchmark_chacha(segmentos)

    # Resultados
    print("\n" + "═"*40)
    print("  RESULTADOS DE BENCHMARK")
    print("═"*40)
    imprimir_resultado("AES-GCM",            t_gcm_c,    t_gcm_d,    num_segmentos, tam_segmento)
    imprimir_resultado("AES-CCM",            t_ccm_c,    t_ccm_d,    num_segmentos, tam_segmento)
    imprimir_resultado("ChaCha20-Poly1305",  t_chacha_c, t_chacha_d, num_segmentos, tam_segmento)

    # Ranking
    totales = {
        "AES-GCM":           t_gcm_c    + t_gcm_d,
        "AES-CCM":           t_ccm_c    + t_ccm_d,
        "ChaCha20-Poly1305": t_chacha_c + t_chacha_d,
    }
    ganador = min(totales, key=totales.get)
    print(f"\n🏆  Más rápido en total: {ganador} ({totales[ganador]:.6f} s)\n")


if __name__ == "__main__":
    main()
