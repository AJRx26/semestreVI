"""
crypto_utils.py

Utilidades criptográficas para el chat seguro:
  - Cifrado: AES-CTR (256 bits)
  - Autenticación: HMAC-SHA256
  - Esquema: Encrypt-then-MAC
"""

import os
import hmac
import hashlib
import base64

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

NONCE_SIZE = 16   # bytes para el nonce de AES-CTR
MAC_SIZE   = 32   # bytes del HMAC-SHA256
KEY_SIZE   = 32   # bytes de la llave AES-256


# ──────────────────────────────────────────────
#  Cifrado / Descifrado
# ──────────────────────────────────────────────

def cifrar(plaintext: bytes, key_aes: bytes) -> bytes:
    """
    Cifra `plaintext` con AES-256-CTR usando un nonce aleatorio.

    Formato del resultado:
        nonce (16 bytes) || ciphertext
    """
    nonce = os.urandom(NONCE_SIZE)
    ctx = Cipher(algorithms.AES(key_aes), modes.CTR(nonce),
                 backend=default_backend())
    enc = ctx.encryptor()
    ciphertext = enc.update(plaintext) + enc.finalize()
    return nonce + ciphertext


def descifrar(data: bytes, key_aes: bytes) -> bytes:
    """
    Descifra datos producidos por `cifrar`.

    Formato esperado:
        nonce (16 bytes) || ciphertext
    """
    nonce      = data[:NONCE_SIZE]
    ciphertext = data[NONCE_SIZE:]
    ctx = Cipher(algorithms.AES(key_aes), modes.CTR(nonce),
                 backend=default_backend())
    dec = ctx.decryptor()
    return dec.update(ciphertext) + dec.finalize()


# ──────────────────────────────────────────────
#  MAC (HMAC-SHA256)
# ──────────────────────────────────────────────

def calcular_mac(data: bytes, key_mac: bytes) -> bytes:
    """Devuelve HMAC-SHA256(key_mac, data)."""
    return hmac.new(key_mac, data, hashlib.sha256).digest()


def verificar_mac(data: bytes, key_mac: bytes, mac_recibido: bytes) -> bool:
    """Compara MACs en tiempo constante para evitar timing attacks."""
    mac_esperado = calcular_mac(data, key_mac)
    return hmac.compare_digest(mac_esperado, mac_recibido)


# ──────────────────────────────────────────────
#  Encrypt-then-MAC  (empaquetar / desempaquetar)
# ──────────────────────────────────────────────

def empaquetar(plaintext: bytes, key_aes: bytes, key_mac: bytes) -> bytes:
    """
    Aplica Encrypt-then-MAC y devuelve el paquete listo para enviar.

    Formato:
        ciphertext_con_nonce || MAC (32 bytes)
    """
    cifrado = cifrar(plaintext, key_aes)
    mac     = calcular_mac(cifrado, key_mac)
    return cifrado + mac


def desempaquetar(paquete: bytes, key_aes: bytes, key_mac: bytes) -> bytes:
    """
    Verifica el MAC y descifra.  Lanza ValueError si el MAC no es válido.
    """
    cifrado      = paquete[:-MAC_SIZE]
    mac_recibido = paquete[-MAC_SIZE:]

    if not verificar_mac(cifrado, key_mac, mac_recibido):
        raise ValueError("MAC inválido: el mensaje fue alterado o la llave es incorrecta")

    return descifrar(cifrado, key_aes)


# ──────────────────────────────────────────────
#  Serialización de llaves (base64)
# ──────────────────────────────────────────────

def llave_a_b64(key: bytes) -> str:
    return base64.b64encode(key).decode()


def b64_a_llave(s: str) -> bytes:
    return base64.b64decode(s)


def generar_llaves() -> tuple[bytes, bytes]:
    """Genera y devuelve (key_aes, key_mac) aleatorias de 32 bytes cada una."""
    return os.urandom(KEY_SIZE), os.urandom(KEY_SIZE)


def cargar_llaves(archivo: str) -> tuple[bytes, bytes]:
    """
    Lee un archivo de llaves con el formato:
        AES:<base64>
        MAC:<base64>
    Devuelve (key_aes, key_mac).
    """
    with open(archivo) as f:
        lineas = f.read().splitlines()
    key_aes = b64_a_llave(lineas[0].split(":", 1)[1])
    key_mac = b64_a_llave(lineas[1].split(":", 1)[1])
    return key_aes, key_mac


def guardar_llaves(archivo: str, key_aes: bytes, key_mac: bytes) -> None:
    """Escribe las llaves en el formato esperado por `cargar_llaves`."""
    with open(archivo, "w") as f:
        f.write(f"AES:{llave_a_b64(key_aes)}\n")
        f.write(f"MAC:{llave_a_b64(key_mac)}\n")
