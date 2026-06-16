from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

import sys

def generar_llave_privada():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return private_key

def generar_llave_publica(llave_privada):
    return llave_privada.public_key()

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


if __name__ == '__main__':
    path_salida_privada = sys.argv[1]
    path_salida_publica = sys.argv[2]

    llave_privada = generar_llave_privada()
    llave_publica = generar_llave_publica(llave_privada)

    with open(path_salida_privada, 'wb') as salida_privada:
        contenido = convertir_llave_privada_bytes(llave_privada)
        salida_privada.write(contenido)

    with open(path_salida_publica, 'wb') as salida_publica:
        contenido = convertir_llave_publica_bytes(llave_publica)
        salida_publica.write(contenido)
