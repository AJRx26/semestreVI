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
    # Generar llaves ECDSA para Servidor
    privada_servidor = generar_llave_privada()
    publica_servidor = generar_llave_publica(privada_servidor)
    guardar_llave_privada("servidor_privada.pem", privada_servidor)
    guardar_llave_publica("servidor_publica.pem", publica_servidor)

    # Generar llaves ECDSA para Cliente
    privada_cliente = generar_llave_privada()
    publica_cliente = generar_llave_publica(privada_cliente)
    guardar_llave_privada("cliente_privada.pem", privada_cliente)
    guardar_llave_publica("cliente_publica.pem", publica_cliente)
