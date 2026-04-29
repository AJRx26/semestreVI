import socket
import sys
import os
import utils


def conectar_servidor(host, puerto):
    # socket para IP v4
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((host, int(puerto)))
        return cliente
    except:
        print("Servidor inalcanzable")
        exit(1)


def enviar_archivo(
    socket,
    archivo,
    llave_privada,
    subject_servidor,
    cert_servidor_bytes,
    publica_issuer,
):
    llave_aes = os.urandom(16)
    iv = os.urandom(16)
    llave_mac = os.urandom(16)

    with open(archivo, "rb") as ar:
        mensaje = ar.read()  # solo para archivos pequeños

    llave_publica = utils.regresar_llave_publica_certificado(
        subject_servidor, cert_servidor_bytes, publica_issuer
    )

    paquete = llave_aes + iv + llave_mac
    paso1 = utils.cifrar_RSA(llave_publica, paquete)
    paso2 = utils.firmar_RSA(llave_privada, paquete)
    paso3 = utils.cifrar_ctr(mensaje, llave_aes, iv)
    paso4 = utils.calcular_hmac(paso1 + paso2 + paso3, llave_mac)

    paquete = paso1 + paso2 + paso3 + paso4
    tam_bytes = str(len(paquete)).encode("utf-8")

    socket.send(tam_bytes)
    socket.send(b"---")
    socket.send(paquete)
    print("[+] Enviado correctamente")


if __name__ == "__main__":
    host = sys.argv[1]
    puerto = sys.argv[2]
    llave_privada_cliente = sys.argv[3]
    subject = sys.argv[4]
    certificado_servidor = sys.argv[5]
    llave_publica_ca = sys.argv[6]
    archivo = sys.argv[7]

    with open(llave_privada_cliente, "rb") as f:
        llave_privada = utils.convertir_bytes_llave_privada(f.read())

    with open(certificado_servidor, "rb") as f:
        cert_servidor_bytes = f.read()

    with open(llave_publica_ca, "rb") as f:
        publica_issuer = utils.convertir_bytes_llave_publica(f.read())

    cliente = conectar_servidor(host, puerto)
    enviar_archivo(
        cliente, archivo, llave_privada, subject, cert_servidor_bytes, publica_issuer
    )
    cliente.close()
