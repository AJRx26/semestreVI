#!/usr/bin/env python3

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Cifrar, se requiere un password para scrypt
salt = os.urandom(16)
kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=default_backend())
key = kdf.derive(password)
iv = os.urandom(12)
encryptor = Cipher(
    algorithms.AES(key), modes.GCM(iv), backend=default_backend()
).encryptor()

associated_data = iv + salt
encryptor.authenticate_additional_data(associated_data)
encryptor.update(textoPlano)
encryptor.finalize()  # necesario para generar tag
tag = encryptor.tag  # 16 bytes

# descifrar
# obtener el iv y el salt y generar de nuevo la llave
kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=default_backend())
key = kdf.derive(password)
# obtener el tag de algun lado
decryptor = Cipher(
    algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()
).decryptor()
# revisar integridad y autenticidad de datos adicionales
associated_data = iv + salt
decryptor.authenticate_additional_data(associated_data)
texto_plano = decryptor.update(ciphertext)
# si hay alteraciones finalize lanza excepcion
decryptor.finalize()
