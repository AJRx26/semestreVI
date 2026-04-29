#!/usr/bin/env python3
import socket
import threading
import sys

import utils

RSA_SIZE = 256
HMAC_SIZE = 32


def ayuda():
    mensaje = """
    """


def crear_socket_servidor(puerto):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(("", int(puerto)))  # hace el bind en cualquier interfaz disponible
    return servidor


def recv_exact(sock, num_bytes):
    datos = b""
    while len(datos) < num_bytes:
        chunk = sock.recv(num_bytes - len(datos))
        if not chunk:
            raise ConnectionError("Conexion cerrada mientras se recibian datos")
        datos += chunk
    return datos


def recibir_paquete(cliente):
    encabezado = b""
    while b"---" not in encabezado:
        byte = cliente.recv(1)
        if not byte:
            raise ConnectionError("Conexion cerrada")
        encabezado += byte

    tam = int(encabezado.replace(b"---", b"").strip())
    paquete = recv_exact(cliente, tam)
    return paquete


def procesar_paquete(
    paquete,
    llave_privada_servidor,
    subject_cliente,
    certificado_cliente_bytes,
    publica_issuer,
):

    parte1 = paquete[:RSA_SIZE]
    parte2 = paquete[RSA_SIZE : RSA_SIZE + RSA_SIZE]
    parte3 = paquete[RSA_SIZE + RSA_SIZE : -HMAC_SIZE]
    parte4 = paquete[-HMAC_SIZE:]

    # Descifrar llaves simetricas con la privada del serv
    paquete_llaves = utils.descifrar_RSA(llave_privada_servidor, parte1)
    llave_aes = paquete_llaves[:16]
    iv = paquete_llaves[16:32]
    llave_mac = paquete_llaves[32:48]

    # verificar si la firma digital es autentica
    llave_publica_cliente = utils.regresar_llave_publica_certificado(
        subject_cliente, certificado_cliente, publica_issuer
    )
    if not utils.es_firma_valida(llave_publica_cliente, parte2, paquete_llaves):
        raise Exception("Firma digital invalida")

    # verificar hmac
    hmac_calculado = utils.calcular_hmac(parte1 + parte2 + parte3, llave_mac)
    if hmac_calculado != parte4:
        raise Exception("HMAC invalido - Mensaje alterado")

    # descifrar mensaje
    mensaje = utils.cifrar_ctr(parte3, llave_aes, iv)
    return mensaje


def atencion(
    cliente,
    direccion,
    llave_privada_servidor,
    subject_cliente,
    cert_cliente_bytes,
    publica_issuer,
):

    print(f"[+] Conexion aceptada de {direccion}")

    try:
        paquete = recibir_paquete(cliente)
        print(f"[+] Paquete recibido de {direccion} ({len(paquete)} bytes)")

        mensaje = procesar_paquete(
            paquete,
            llave_privada_servidor,
            subject_cliente,
            cert_cliente_bytes,
            publica_issuer,
        )

        print(f"-- Mensaje de {direccion} --")
        print(mensaje.decode("utf-8"))

    except Exception as e:
        print(f"[+] Error con {direccion}")
    finally:
        cliente.close()
        print(f"[+] Conexion cerrada: {direccion}")


def escuchar(
    servidor,
    llave_privada_servidor,
    subject_cliente,
    cert_cliente_bytes,
    publica_issuer,
):
    servidor.listen(5)

    print("[+] Escuchando...")
    while True:
        cliente, direccion = servidor.accept()
        hilo = threading.Thread(
            target=atencion,
            args=(
                cliente,
                direccion,
                llave_privada_servidor,
                subject_cliente,
                cert_cliente_bytes,
                publica_issuer,
            ),
        )
        hilo.daemon = True
        hilo.start()


if __name__ == "__main__":
    puerto = sys.argv[1]
    llave_privada = sys.argv[2]
    subject_cliente = sys.argv[3]
    certificado_cliente = sys.argv[4]
    publica_ca = sys.argv[5]

    with open(llave_privada, "rb") as f:
        llave_privada_servidor = utils.convertir_bytes_llave_privada(f.read())

    with open(certificado_cliente, "rb") as f:
        cert_cliente_bytes = f.read()

    with open(publica_ca, "rb") as f:
        publica_issuer = utils.convertir_bytes_llave_publica(f.read())

    servidor = crear_socket_servidor(puerto)
    escuchar(
        servidor,
        llave_privada_servidor,
        subject_cliente,
        cert_cliente_bytes,
        publica_issuer,
    )
