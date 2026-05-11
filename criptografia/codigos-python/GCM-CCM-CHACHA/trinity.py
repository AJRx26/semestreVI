#!/usr/bin/env python3

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.ciphers.aead import AESCCM
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
import time

inicio = time.time()


def gcm():
    data = b"a secret message"
    aad = b"authenticate and unencrypted data"
    key = AESGCM.generate_key(bit_length=128)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, data, aad)
    plain = aesgcm.decrypt(nonce, ct, aad)

    return ct, plain


def ccm():
    data = b"a secret message"
    aad = b"authenticate but unencrypted data"
    key = AESCCM.generate_key(bit_length=128)
    aesccm = AESCCM(key)
    nonce = os.urandom(7)
    ct = aesccm.encrypt(nonce, data, aad)
    plain = aesccm.decrypt(nonce, ct, aad)

    return ct, plain


def chacha():
    data = b"a secret message"
    aad = b"authenticated but unencrypted data"
    key = ChaCha20Poly1305.generate_key()
    chacha = ChaCha20Poly1305(key)
    nonce = os.urandom(12)
    ct = chacha.encrypt(nonce, data, aad)
    plain = chacha.decrypt(nonce, ct, aad)

    return ct, plain


if __name__ == "__main__":

    ct_gcm, plain_gcm = gcm()
    ct_ccm, plain_ccm = ccm()
    ct_chacha, plain_chacha = chacha()

    print("GCM cifrado: ", ct_gcm)
    print("GCM descifrado: ", plain_gcm)

    print("CCM cifrado: ", ct_ccm)
    print("CCM descifrado: ", plain_ccm)

    print("Chacha cifrado: ", ct_chacha)
    print("Chacha descifrado: ", plain_chacha)

    fin = time.time()
    print(fin - inicio)
