#!/usr/bin/env python3

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat, PrivateFormat, NoEncryption,
    load_pem_private_key, load_pem_public_key
)
from cryptography.exceptions import InvalidSignature

#  GENERACIÓN DE LLAVES
def generar_llaves_ecdh():
    """Genera un par de llaves ECDH efímeras (privada, publica)."""
    privada = ec.generate_private_key(ec.SECP384R1(), default_backend())
    publica = privada.public_key()
    return privada, publica


#  CARGA DE LLAVES ECDSA DESDE ARCHIVO PEM
def cargar_llave_privada(ruta: str):
    """
    Carga una llave privada ECDSA desde un archivo PEM.
    Usada por cada lado para cargar su propia identidad.
    """
    with open(ruta, 'rb') as f:
        return load_pem_private_key(f.read(), password=None)


def cargar_llave_publica(ruta: str):
    """
    Carga una llave pública ECDSA desde un archivo PEM.
    Usada por cada lado para cargar la identidad del contrario.
    """
    with open(ruta, 'rb') as f:
        return load_pem_public_key(f.read())

#  SERIALIZACIÓN
#  Convertir llaves a bytes para enviarlas por socket
def serializar_publica(llave_publica) -> bytes:
    """Convierte una llave pública (ECDH o ECDSA) a bytes."""
    return llave_publica.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)

def deserializar_publica(datos: bytes):
    """Reconstruye una llave pública desde bytes."""
    return ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP384R1(), datos)


#  FIRMA Y VERIFICACIÓN (ECDSA)
def firmar(llave_publica_ecdh: bytes, priv_ecdsa) -> bytes:
    """
    Firma los bytes de la llave pública ECDH con la llave privada ECDSA.
    Devuelve la firma en bytes.
    """
    return priv_ecdsa.sign(llave_publica_ecdh, ec.ECDSA(hashes.SHA256()))

def verificar(llave_publica_ecdh: bytes, firma: bytes, pub_ecdsa) -> bool:
    """
    Verifica que la firma corresponde a la llave pública ECDH recibida.
    Usa la llave pública ECDSA del lado contrario.
    Devuelve True si es válida, False si no.
    """
    try:
        pub_ecdsa.verify(firma, llave_publica_ecdh, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False

#  INTERCAMBIO ECDH
def derivar_llave(priv_ecdh, pub_ecdh_remota) -> bytes:
    """
    Realiza el intercambio ECDH y deriva una llave AES-256 con HKDF.
    priv_ecdh      → llave privada ECDH propia
    pub_ecdh_remota → llave pública ECDH del otro lado
    Devuelve 32 bytes (256 bits) listos para usar como llave AES.
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
