import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes, hmac
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

ISSUER_NAME = 'WACKO'  # debe coincidir con ISSUER_NAME en issuer.py del maestro


def convertir_llave_privada_bytes(llave_privada):
    resultado = llave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return resultado

def convertir_bytes_llave_privada(contenido_binario):
    resultado = serialization.load_pem_private_key(
        contenido_binario,
        backend=default_backend(),
        password=None)
    return resultado

def convertir_llave_publica_bytes(llave_publica):
    resultado = llave_publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return resultado

def convertir_bytes_llave_publica(contenido_binario):
    resultado = serialization.load_pem_public_key(
        contenido_binario,
        backend=default_backend())
    return resultado


def es_firma_valida(llave_publica, firma, datos):
    try:
        llave_publica.verify(
            firma,
            datos,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
        return True
    except Exception:
        return False


def es_certificado_valido(subject, datos_certificado, datos_certificado_raw, firma, publica_issuer):
    if subject != datos_certificado['subject']:
        return False
    if ISSUER_NAME != datos_certificado['issuer']:
        return False
    if not es_firma_valida(publica_issuer, firma, datos_certificado_raw):
        return False
    return True

def regresar_llave_publica_certificado(subject, certificado, publica_issuer):
    """
    Extrae y valida la llave pública de un certificado.
    - certificado:    bytes del archivo .bin generado por issuer.py
    - publica_issuer: objeto llave pública de la CA (generarLlaves.convertir_bytes_llave_publica)
    """
    datos_certificado_raw = certificado[:-256]
    datos_certificado = json.loads(datos_certificado_raw.decode('utf-8'))
    firma = certificado[-256:]
    if not es_certificado_valido(subject, datos_certificado, datos_certificado_raw, firma, publica_issuer):
        raise Exception('El certificado no es válido')
    llave_publica_raw = datos_certificado['public_key'].encode('utf-8')
    llave_publica = convertir_bytes_llave_publica(llave_publica_raw)
    return llave_publica


def cifrar_RSA(llave_publica, mensaje):
    ciphertext = llave_publica.encrypt(
        mensaje,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None))
    return ciphertext


def descifrar_RSA(llave_privada, cifrado):
    mensaje = llave_privada.decrypt(
        cifrado,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None))
    return mensaje


def firmar_RSA(llave_privada, mensaje):
    signature = llave_privada.sign(
        mensaje,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256())
    return signature


def cifrar_ctr(mensaje, llave, iv):
    aesCipher = Cipher(
        algorithms.AES(llave),
        modes.CTR(iv),
        backend=default_backend())
    aesEncryptor = aesCipher.encryptor()
    cifrado = aesEncryptor.update(mensaje)
    aesEncryptor.finalize()
    return cifrado


def calcular_hmac(mensaje, llave):
    h = hmac.HMAC(llave, hashes.SHA256(), backend=default_backend())
    h.update(mensaje)
    return h.finalize()
