import gmpy2
import argparse
from cryptography.hazmat.primitives import serialization

def ayuda():
    mensaje = """
    - Supon que el atacante tiene un texto cifrado c que intercepto, obtenido al cifrar con llave publica el mensaje m. Sin la llave privada el atacante no puede descifrar el mensaje. La victima con la llave privada probablemente no le vaya a dar directamente el texto m descifrado. Pero, con ingenieria social, es posible que si le de un multiplo de m. Con ese multiplo, el atacante puede recuperar el original. Suponiendo que el atacante escogio como multiplo el 2. El atacante cifra con RSA y la llave publica el 2 para obtener "cr". El texto cifrado interceptado por el atacante se denota mediante "c0". Si se multiplica cr y c0 (mod n) se obtiene c1.

    - c1 = c0cr(mod n)
    - c1 = mere(mod n)
    - c1 = (mr)e (mod n)

    - El atacante envia c1 a la victima con la llave privada, la victima descifra el mensaje y obtiene mr, nota que no es legible y lo desecha. El atacante logra recuperar mr. Usando mr el atacante quiere recuperar m. Sin aritmetica modular lo tradicional seria: m = mr/r. Con aritmetica modular el equivalente es: m = mr * r-1modn (mod n)

    - m = (mr * gmpy2.powmod(r, -1, n)) % n

    Hacer una demostración del ataque de texto cifrado escogido para RSA con los siguientes elementos:

    - Utilizar archivos, a partir del código visto en clase, para los archivos de entrada y salida, esto incluye la multiplicación de los dos contenidos cifrados

    - Mostrar que se puede recuperar el texto plano original sin utilizar la llave privada directamente
    """

# =========================
# Cargar llave pública
# =========================
def load_public_key(path):
    with open(path, "rb") as f:
        return serialization.load_pem_public_key(f.read())

# Conversiones
# RSA opera con numeros enteros, no bytes
# es neceario convertir un archivo de bytes a un entero para procesarlo
def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')

def int_to_bytes(i):
    # asegurarse de que es un entero python
    return int(i).to_bytes((i.bit_length()+7)//8, byteorder='big')

# =========================
# Leer archivo binario
# =========================
def read_file(path):
    with open(path, "rb") as f:
        return f.read()

def write_file(path, data):
    with open(path, "wb") as f:
        f.write(data)

# =========================
# PASO 1: Generar c1
# =========================
def generar_c1(c0_path, pubkey_path, salida_c1, r):
    public_key = load_public_key(pubkey_path)
    pub = public_key.public_numbers()
    e, n = pub.e, pub.n

    # leer ciphertext original
    c0_bytes = read_file(c0_path)
    c0 = bytes_to_int(c0_bytes)

    print("[+] c0 cargado")

    # cifrar r
    cr = gmpy2.powmod(r, e, n)

    # generar c1
    c1 = (c0 * cr) % n

    print("[+] c1 generado")

    write_file(salida_c1, int_to_bytes(c1))
    print(f"[+] c1 guardado en {salida_c1}")

# =========================
# PASO 2: Descifrar m desde mr
# =========================
def descifrar_m(mr_path, pubkey_path, salida_m, r):
    public_key = load_public_key(pubkey_path)
    n = public_key.public_numbers().n

    # leer mr (resultado de descifrar c1)
    mr_bytes = read_file(mr_path)
    mr = bytes_to_int(mr_bytes)

    print("[+] mr cargado")

    # inverso modular
    r_inv = gmpy2.invert(r, n)

    # recuperar m
    m = (mr * r_inv) % n

    print("[+] mensaje original recuperado")

    write_file(salida_m, int_to_bytes(m))
    print(f"[+] mensaje guardado en {salida_m}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--modo", required=True, choices=["c1", "descifrar"])
    parser.add_argument("--entrada", required=True)
    parser.add_argument("--llave", required=True)
    parser.add_argument("--salida", required=True)
    parser.add_argument("--r", type=int, default=2)
    args = parser.parse_args()

    if args.modo == "c1":
        generar_c1(args.entrada, args.llave, args.salida, args.r)
    elif args.modo == "descifrar":
        descifrar_m(args.entrada, args.llave, args.salida, args.r)
