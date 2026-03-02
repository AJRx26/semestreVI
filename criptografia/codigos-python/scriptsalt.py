#import os
import base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend

#datos
salt_base64 = "GNWpRwSWikgzq1vzkEnk8Q=="
key_base64 = "zfd4fY4zkcSPUBu8HmfaN7YPW3lh3Xm4ByDSqcK7xvA="

#decodificar
salt = base64.b64decode(salt_base64)
key = base64.b64decode(key_base64)

mayus = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
minus = "abcdefghijklmnopqrstuvwxyz"
nums = "0123456789"
caracteres = mayus + minus + nums

contador = 0    
for ma in caracteres:
    for mi in caracteres:
        for num in caracteres:
            contador += 1
            if contador % 10000 == 0:
                print("Intentos: ", contador)
                
            password = (ma + mi + num).encode()

            kdf = Scrypt(
            salt=salt, length=32,
            n=2**14, r=8, p=1,
            backend=default_backend()
            )

            hash_prueba = kdf.derive(password)

            if hash_prueba == key:
                print("Contraseña encontrada: ", password.decode())
                exit()
