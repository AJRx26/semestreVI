#!/usr/bin/env python3


from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# solo hay que elegir un tipo de curva
private_key1 = ec.generate_private_key(ec.SECP384R1(), default_backend())

# esta es la llave que se va a intercambiar
public_key1 = private_key1.public_key()


print("[+] Valores 1")
print(f"LLave privada: ", private_key1)
print(f"Llave publica: ", public_key1)

private_key2 = ec.generate_private_key(ec.SECP384R1(), default_backend())
public_key2 = private_key2.public_key()

print("[+] Valores 2")
print(f"LLave privada: ", private_key2)
print(f"Llave publica: ", public_key2)

# usan las llaves publicas de la otra parte
shared_key1 = private_key1.exchange(ec.ECDH(), public_key2)
shared_key2 = private_key2.exchange(ec.ECDH(), public_key1)

print("[+] Valores compartidos")
print(f"LLave 1: ", shared_key1)
print(f"Llave 1: ", shared_key2)


# Derivar llaves
derived_key1 = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"handshake data",
    backend=default_backend(),
).derive(shared_key1)

derived_key2 = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"handshake data",
    backend=default_backend(),
).derive(shared_key2)

print("[+] Llaves finales")
print(f"LLave 1: ", derived_key1)
print(f"Llave 2: ", derived_key2)
