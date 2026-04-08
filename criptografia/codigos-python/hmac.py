#!/usr/bin/env python3
import hashlib

B = 128  # size de bloque de SHA256
IPAD = bytes([54]) * B
OPAD = bytes([92]) * B


def expandir_llave(llave: bytes) -> bytes:
    if len(llave) == B:
        return llave
    if len(llave) < B:
        return llave + bytes(B - len(llave))
    hasher = hashlib.sha256()
    hasher.update(llave)
    hash_k = hasher.digest()
    if hash_k == B:
        return hash_k
    return hash_k + bytes(B - len(hash_k))


def hmac(text: bytes, llave: bytes) -> bytes:
    llave = expandir_llave(llave)
