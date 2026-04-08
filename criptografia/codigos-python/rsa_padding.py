#!/usr/bin/env python3
import argparse
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding


def ayuda():
    mensaje = """
    Adaptar el script de cifrado/descifrado con RSA para utilizar padding OAEP.

    python3 rsa_padding.py --llave key.pem --entrada mensaje --salida cifrado --operacion cifrar/descifrar
    """


def archivo_a_bytes(ruta):
    with open(ruta, "rb") as entrada:
        return entrada.read()


def desserializar_publica(ruta_pem):
    binario = b""
    with open(ruta_pem, "rb") as entrada:
        binario = entrada.read()
    return serialization.load_pem_public_key(binario, backend=default_backend())


def desserializar_privada(ruta_pem):
    binario = b""
    with open(ruta_pem, "rb") as entrada:
        binario = entrada.read()
    return serialization.load_pem_private_key(
        binario, backend=default_backend(), password=None
    )


def cifrar(key, archivo_entrada, archivo_salida):
    llave = desserializar_publica(key)
    archivo = archivo_a_bytes(archivo_entrada)
    cifrado = llave.encrypt(
        archivo,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )  # Se usa rara vez dejar None
    with open(archivo_salida, "wb") as salida:
        salida.write(cifrado)
    print(f"Archivo cifrado: {archivo_salida}")


def descifrar(key, archivo_entrada, archivo_salida):
    llave = desserializar_privada(key)
    cifrado = archivo_a_bytes(archivo_entrada)
    mensaje = llave.decrypt(
        cifrado,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    with open(archivo_salida, "wb") as salida:
        salida.write(mensaje)
    print(f"Archivo descifrado: {archivo_salida}")


if __name__ == "__main__":
    all_args = argparse.ArgumentParser()
    all_args.add_argument("--llave", help="Ruta de entrada a utilizar", required=True)
    all_args.add_argument(
        "--entrada", help="Ruta de la entrada del archivo a procesar", required=True
    )
    all_args.add_argument("--salida", help="Ruta de salida del proceso", required=True)
    all_args.add_argument("--operacion", help="cifrar o descifrar", required=True)
    args = vars(all_args.parse_args())

    op = args["operacion"]

    if op == "cifrar":
        cifrar(args["llave"], args["entrada"], args["salida"])
    elif op == "descifrar":
        descifrar(args["llave"], args["entrada"], args["salida"])
    else:
        print("Operacion no soportada, perdedor")
        exit(1)
