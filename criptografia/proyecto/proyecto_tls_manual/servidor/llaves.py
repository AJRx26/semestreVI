from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

def generar_llave_privada():
    """
    Generar llave privada usando ECDSA y curvas elípticas
    """
    return ec.generate_private_key(
            ec.SECP384R1(), default_backend())

def guardar_llave_privada(ruta, privada):
    """
    Se guarda la llave pública en un archivo de formato PEM
    """
    private_key_bytes = privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(ruta, 'wb') as salida:
        salida.write(private_key_bytes)

def generar_llave_publica(privada):
    return privada.public_key()

def guardar_llave_publica(ruta, publica):
    public_key_bytes = publica.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(ruta, 'wb') as salida:
        salida.write(public_key_bytes)

if __name__ == '__main__':
    privada = generar_llave_privada()
    publica = generar_llave_publica(privada)
    guardar_llave_privada("llave_privada_servidor.pem", privada)
    guardar_llave_publica("llave_publica_servidor.pem", publica)
