#!/usr/bin/env python3
"""
generar_llaves.py

Genera un archivo de llaves (AES + MAC) para usar con el chat seguro.

Uso:
    python3 generar_llaves.py llaves_cliente1.txt
"""

import sys
from crypto_utils import generar_llaves, guardar_llaves

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso: {sys.argv[0]} <archivo_salida>")
        sys.exit(1)

    archivo = sys.argv[1]
    key_aes, key_mac = generar_llaves()
    guardar_llaves(archivo, key_aes, key_mac)
    print(f"Llaves generadas y guardadas en: {archivo}")
