#!/usr/bin/env python3

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.exceptions import InvalidSignature

# ── Llaves ECDSA (para firmar y verificar) ──────────────────────
ecdsa_private1 = ec.generate_private_key(ec.SECP384R1(), default_backend())
ecdsa_public1  = ecdsa_private1.public_key()

ecdsa_private2 = ec.generate_private_key(ec.SECP384R1(), default_backend())
ecdsa_public2  = ecdsa_private2.public_key()

# ── Llaves ECDH (para el intercambio) ───────────────────────────
private_key1 = ec.generate_private_key(ec.SECP384R1(), default_backend())
public_key1  = private_key1.public_key()

print("[+] Valores 1")
print(f"LLave privada: ", private_key1)
print(f"Llave publica: ", public_key1)

private_key2 = ec.generate_private_key(ec.SECP384R1(), default_backend())
public_key2  = private_key2.public_key()

print("[+] Valores 2")
print(f"LLave privada: ", private_key2)
print(f"Llave publica: ", public_key2)

# ── Firmar las llaves públicas ECDH antes de intercambiarlas ────
def firmar_llave(llave_publica_bytes, ecdsa_privada):
    return ecdsa_privada.sign(llave_publica_bytes, ec.ECDSA(hashes.SHA256()))

def verificar_llave(llave_publica_bytes, firma, ecdsa_publica):
    try:
        ecdsa_publica.verify(firma, llave_publica_bytes, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False

from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
pub1_bytes = public_key1.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
pub2_bytes = public_key2.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)

firma1 = firmar_llave(pub1_bytes, ecdsa_private1)  # parte 1 firma su llave ECDH
firma2 = firmar_llave(pub2_bytes, ecdsa_private2)  # parte 2 firma su llave ECDH

# ── Verificación cruzada ─────────────────────────────────────────
print("\n[+] Verificación ECDSA")

# parte 2 verifica la llave de parte 1 (usa la pública ECDSA de parte 1)
if verificar_llave(pub1_bytes, firma1, ecdsa_public1):
    print("Llave pública 1: ✅ Firma válida")
else:
    print("Llave pública 1: ❌ Firma inválida — abortando")
    exit(1)

# parte 1 verifica la llave de parte 2 (usa la pública ECDSA de parte 2)
if verificar_llave(pub2_bytes, firma2, ecdsa_public2):
    print("Llave pública 2: ✅ Firma válida")
else:
    print("Llave pública 2: ❌ Firma inválida — abortando")
    exit(1)

# ── Intercambio ECDH (solo si las firmas fueron válidas) ─────────
shared_key1 = private_key1.exchange(ec.ECDH(), public_key2)
shared_key2 = private_key2.exchange(ec.ECDH(), public_key1)

print("[+] Valores compartidos")
print(f"LLave 1: ", shared_key1)
print(f"Llave 2: ", shared_key2)

# ── Derivar llaves ───────────────────────────────────────────────
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
