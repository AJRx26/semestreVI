import base64
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend

def ayuda():
    mensaje = """
    Dada una contraseña hasheada mediante scrypt y un salt dado en base64, crackea el password mediante fuerza bruta: el password solo tiene 3 caracteres y los caracteres posibles son cualquier letra mayuscula o minuscula sin incluir ñ y cualquier digito.
    """

def decodificar_salt(salt_base64):
    salt = base64.b64decode(salt_base64)
    return salt

def decodificar_key(key_base64):
    key = base64.b64decode(key_base64)
    return key

def fuerza_bruta(salt, key):
    caracteres = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    for mayusculas in caracteres:
        for minusculas in caracteres:
            for numeros in caracteres:
                password = (mayusculas + minusculas + numeros).encode()
                #print(f"{password.decode()}")

                #Esta linea de codigo es (())
                print(f"Probando: {password.decode()}", end="\r")

                kdf = Scrypt(
                salt=salt, length=32,
                n=2**14, r=8, p=1,
                backend=default_backend())

                if kdf.derive(password) == key:
                    print("La contraseña es: ", password.decode())
                    return
    print("Contraseña no encontrada")

if __name__ == "__main__":
    salt_base64 = "GNWpRwSWikgzq1vzkEnk8Q=="
    key_base64 = "zfd4fY4zkcSPUBu8HmfaN7YPW3lh3Xm4ByDSqcK7xvA="

    salt = decodificar_salt(salt_base64)
    key = decodificar_key(key_base64)

    fuerza_bruta(salt, key)
