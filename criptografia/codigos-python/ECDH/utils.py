#!/usr/bin/env python3

import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat
)
from cryptography.exceptions import InvalidSignature

DELIMITADOR = b'\r\n'

# generar llaves ECDH
def generar_llaves_ecdh():
    privada = ec.generate_private_key(ec.SECP384R1(), default_backend())
    publica = privada.public_key()
    return privada, publica

# intercambio ECDH y deriva una llave
def derivar_llave(priv_ecdh, pub_ecdh_remota) -> bytes:
    """
    priv_ecdh: llave privada ECDH propia
    pub_ecdh_remota: llave pública ECDH del otro
    """
    secreto_compartido = priv_ecdh.exchange(ec.ECDH(), pub_ecdh_remota)

    llave = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"handshake data",
        backend=default_backend(),
    ).derive(secreto_compartido)

    return llave


# cargar llave privad ECDSA
def desserializar_privada(ruta_pem: str):
    binario = b''
    with open(ruta_pem, 'rb') as entrada:
        binario = entrada.read()
    return serialization.load_pem_private_key(
        binario,
        backend=default_backend(),
        password=None)

# cargar llave publica ECDSA
def desserializar_publica_pem(ruta_pem: str):
    binario = b''
    with open(ruta_pem, 'rb') as entrada:
        binario = entrada.read()
    return serialization.load_pem_public_key(
        binario,
        backend=default_backend())

# firma la llave publica ECDH con la llave privada ECDSA
def firmar(llave_publica_ecdh: bytes, priv_ecdsa) -> bytes:
    return priv_ecdsa.sign(llave_publica_ecdh, ec.ECDSA(hashes.SHA256()))

# verifica la firma con la llave publica ECDSA del otro lado
def verificar(llave_publica_ecdh: bytes, firma: bytes, pub_ecdsa) -> bool:
    try:
        pub_ecdsa.verify(firma, llave_publica_ecdh, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False

# convertir llaves a bytes para enviarlas por socket
def serializar_publica(llave_publica) -> bytes:
    return llave_publica.public_bytes(Encoding.X962,PublicFormat.UncompressedPoint)

# reconstruye una llave pública desde bytes
def deserializar_publica(datos: bytes):
    return ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP384R1(), datos)

# Eviar datos por el socket junto al delimitador
def mandar_datos(socket, datos: bytes):
    socket.sendall(base64.b64encode(datos) + DELIMITADOR)

# leer datos del socket hasta al delimitador
def leer_datos(socket) -> bytes:
    chunk = socket.recv(1024)
    datos = b''
    while not chunk.endswith(DELIMITADOR):
        datos += chunk
        chunk += socket.recv(1024)
    datos += chunk
    return base64.b64decode(datos[:-len(DELIMITADOR)])

