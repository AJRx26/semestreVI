import os
import base64
import argparse


def generar_llave_cifrado():
    # AES-256 → 32 bytes
    return os.urandom(32)


def generar_llave_mac():
    # HMAC-SHA256 → 32 bytes recomendado
    return os.urandom(32)


def guardar_llave(ruta, llave):
    with open(ruta, 'wb') as f:
        f.write(base64.b64encode(llave))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--cifrado", help="Ruta salida llave cifrado", required=True)
    parser.add_argument("--mac", help="Ruta salida llave MAC", required=True)

    args = parser.parse_args()

    llave_cifrado = generar_llave_cifrado()
    llave_mac = generar_llave_mac()

    guardar_llave(args.cifrado, llave_cifrado)
    guardar_llave(args.mac, llave_mac)

    print("Llaves generadas correctamente")
