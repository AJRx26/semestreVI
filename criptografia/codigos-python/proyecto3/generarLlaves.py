from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import argparse


def generar_privada():
    return rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
    )


def guardar_privada(ruta, privada):
    private_key_bytes = privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(ruta, 'wb') as salida:
        salida.write(private_key_bytes)


def generar_publica(privada):
    return privada.public_key()
    

def guardar_publica(ruta, publica):
    public_key_bytes = publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(ruta, 'wb') as salida:
        salida.write(public_key_bytes)

if __name__ == '__main__':
    all_args =  argparse.ArgumentParser()    
    all_args.add_argument("--privada", help="Ruta de salida llave privada", required=True)
    all_args.add_argument("--publica", help="Ruta de salida llave pública", required=True)    
    args = vars(all_args.parse_args())
    ruta_privada = args['privada']
    ruta_publica = args['publica']
    llave_privada = generar_privada()
    llave_publica = generar_publica(llave_privada)
    guardar_privada(ruta_privada, llave_privada)
    guardar_publica(ruta_publica, llave_publica)
