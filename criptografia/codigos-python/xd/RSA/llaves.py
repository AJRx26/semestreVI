from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generar llave privada
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Extraer llave publica de llave privada
public_key = private_key.public_key()

# Convertir llave privada a bytes, sin cifrar los bytes
# Obviamente a partir de los bytes se puede guardar en un archivo binario
private_key_bytes = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

# Convertir la llave publica en bytes
public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Convertir la llave privada de bytes a objeto llave
# Como no se cifraron los bytes no hace falta un password
private_key = serialization.load_pem_private_key(
    private_key_bytes,
    backend=default_backend(),
    password=None)

# Convertir la llave publica de bytes a objeto llave
public_key = serialization.load_pem_public_key(
    public_key_bytes,
    backend=default_backend())
