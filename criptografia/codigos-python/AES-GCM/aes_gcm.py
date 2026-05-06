#!/usr/bin/env python3

import os
import argparse
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

CHUNK_SIZE = 1024
SIZE_SALT = 16
SIZE_IV = 12
SIZE_TAG = 16


def ayuda():
    mensaje = """
    - Script que cifra y descifra un archivo con AES-GCM

    python3 aes_ctr.py -p OPERACION -i archivo_entrada -o archivo_salida -l password

    - Argumentos:
        - Operacion: cifrar o descifrar
        - Archivo de entrada
        - Archivo de salida
        - password: Parametro para cifrar y descifrar
    """


def cifrar(archivo_entrada: str, archivo_salida: str, password: str) -> None:
    salt = os.urandom(SIZE_SALT)
    iv = os.urandom(SIZE_IV)

    kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=default_backend())
    key = kdf.derive(password.encode())

    encryptor = Cipher(
        algorithms.AES(key), modes.GCM(iv), backend=default_backend()
    ).encryptor()

    associated_data = iv + salt
    encryptor.authenticate_additional_data(associated_data)

    with open(archivo_entrada, "rb") as entrada:
        with open(archivo_salida, "wb") as salida:
            while True:
                chunk = entrada.read(CHUNK_SIZE)
                if not chunk:
                    break
                salida.write(encryptor.update(chunk))

            salida.write(encryptor.finalize())
            tag = encryptor.tag
            salida.write(tag)
            salida.write(iv)
            salida.write(salt)
    print("[+] Archivo cifrado")


def descifrar(archivo_entrada: str, archivo_salida: str, password: str) -> None:

    with open(archivo_entrada, "rb") as entrada:
        datos = entrada.read()

        salt = datos[-SIZE_SALT:]
        iv = datos[-(SIZE_SALT + SIZE_IV) : -SIZE_SALT]
        tag = datos[-(SIZE_SALT + SIZE_IV + SIZE_TAG) : -(SIZE_SALT + SIZE_IV)]
        cifrado = datos[: -(SIZE_SALT + SIZE_IV + SIZE_TAG)]

        kdf = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1, backend=default_backend())

        key = kdf.derive(password.encode())

        decryptor = Cipher(
            algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend()
        ).decryptor()

        associated_data = iv + salt
        decryptor.authenticate_additional_data(associated_data)

        try:
            texto_plano = decryptor.update(cifrado) + decryptor.finalize()
        except Exception:
            print("[+] Error, archivo alterado o llave incorrecta")
            return

        with open(archivo_salida, "wb") as salida:
            salida.write(texto_plano)
        print("[+] Archivo descifrado")


if __name__ == "__main__":
    all_args = argparse.ArgumentParser()
    all_args.add_argument(
        "-p", "--Operacion", help="Aplicar operación, cifrar/descifrar"
    )
    all_args.add_argument("-i", "--input", help="Archivo de entrada", required=True)
    all_args.add_argument("-o", "--output", help="Archivo de salida", required=True)
    all_args.add_argument("-l", "--password", help="Password", required=False)
    args = vars(all_args.parse_args())
    operacion = args["Operacion"]

    if operacion == "cifrar":
        cifrar(args["input"], args["output"], args["password"])
    else:
        descifrar(args["input"], args["output"], args["password"])
