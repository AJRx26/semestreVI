import sys
import socket
import ssl
import os
import hashlib
import time
import utils
import argparse

# crear socket
def crear_socket_servidor(puerto):
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mySocket.bind(('', int(puerto)))
    return mySocket

def esperar_cliente(servidor):
    servidor.listen(1)
    cliente, addr = servidor.accept()
    return cliente

# Configura el contexto TLS del lado SERVIDOR
def crear_contexto_tls(path_cert, path_privada):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_3 # permitir a partir de TLS 1.3
    context.load_cert_chain(path_cert, path_privada) # Cert + Key del servidor
    return context

#Las credenciales viajan en texto plano DENTRO del túnel TLS por lo que no necesitan cifrado adicional (AES-GCM manual). 
def autenticar_usuario(cliente_sock):
    """
    Verifica usuario y hash SHA-512 desde el archivo usuarios.txt.
    """
    try:
        # Leer mensaje del cliente
        credenciales = utils.leer_mensaje(cliente_sock).decode('utf-8')
        usuario, password = credenciales.split(':', 1)
        #password_hash = hashlib.sha512(password.encode()).hexdigest() # Hash SHA-512 de la contraseña para comparar

        # Buscar en la base de usuarios locales
        with open("usuarios.txt", "r", encoding="utf-8") as f:
            for linea in f:
                user, salt, hashp = linea.strip().split(':', 2)
                if usuario == user:
                    if utils.hashear_password(password, salt) == hashp:
                        utils.mandar_mensaje(cliente_sock, b"OK")
                        return True
                    break
                

        # No se encontró coincidencia
        utils.mandar_mensaje(cliente_sock, b"ERROR")
        return False

    except Exception as e:
        print(f"Error autenticando: {e}")
        try:
            utils.mandar_mensaje(cliente_sock, b"ERROR")
        except:
            pass
        return False

# recibe un archivo del cliente y lo guarda en disco.
def upload(cliente, path_directorio_archivos):
    """
    TLS garantiza confidencialidad e integridad, no se necesita cifrar/descifrar manualmente cada segmento.
    """
    # recibe nombre del archivo
    nombre_archivo = utils.leer_mensaje(cliente).decode('utf-8')
    utils.mandar_mensaje(cliente, b"OK")

    # contruye la ruta completa de destino
    path_final = os.path.join(path_directorio_archivos, nombre_archivo)

    with open(path_final, 'wb') as archivo:
        print(f"Recibiendo archivo: {nombre_archivo}...")

        while True:
            # recibe siguiente segmento
            datos = utils.leer_mensaje(cliente)

            if datos == b'FIN': 
                break

            archivo.write(datos) #escribe en disco

    print(f"Transferencia de '{nombre_archivo}' finalizada.")

# envia un archivo al cliente.
def download(cliente, path_directorio_archivos):
    """
    El archivo se lee en segmentos para no saturar RAM.
    TLS garantiza confidencialidad e integridad del canal.
    """
    # recibe nombre del archivo solicitado
    nombre_archivo = utils.leer_mensaje(cliente).decode('utf-8')
    path_archivo = os.path.join(path_directorio_archivos, nombre_archivo)

    # verifica existencia del archivo
    if not os.path.isfile(path_archivo):
        utils.mandar_mensaje(cliente, b"ERROR")
        print(f"Archivo no encontrado: {nombre_archivo}")
        return

    utils.mandar_mensaje(cliente, b"OK")
    print(f"Enviando archivo: {nombre_archivo}...")

    #lee y envia por segmentos
    for pedazo in utils.crear_generador_lectura(path_archivo):
        utils.mandar_mensaje(cliente, pedazo)

    utils.mandar_mensaje(cliente, b"FIN")
    print(f"Archivo '{nombre_archivo}' enviado correctamente.")


if __name__ == '__main__':
    all_args = argparse.ArgumentParser(description="Proyecto Final Criptografia — Servidor TLS")
    all_args.add_argument("-p", "--puerto", required=True, help="Puerto donde escuchara el servidor")
    all_args.add_argument("--cert", required=True, help="Ruta del certificado del servidor (.crt)")
    all_args.add_argument("--privada", required=True, help="Ruta de la llave privada del servidor (.pem)")
    all_args.add_argument("-d", "--directorio", required=True, help="Ruta de la carpeta directorio")

    args = all_args.parse_args()

    if not os.path.isdir(args.directorio):
        print(f"[!] El directorio no existe: {args.directorio}")
        sys.exit(1)

    puerto = args.puerto
    path_directorio_archivos = args.directorio

    #configurar tls
    ctx = crear_contexto_tls(args.cert, args.privada)

    #crear socket con tls
    servidor = crear_socket_servidor(puerto)
    print(f"Servidor TLS listo en puerto {puerto}...")

    # wrap_socket convierte el socket TCP en socket TLS
    ssock = ctx.wrap_socket(servidor, server_side=True) # server_side=True indica que este es el servidor (espera handshake entrante)
    ssock.listen(1)

    try:
        cliente, addr = ssock.accept()
        print(f"Conexión de {addr} — {cliente.version()}")

        try:
            #autenticacion
            if autenticar_usuario(cliente):
                print("Cliente autenticado. Esperando operaciones...")

                #operacion solicitada
                operacion = utils.leer_mensaje(cliente).decode('utf-8')

                if operacion == 'upload':
                    utils.mandar_mensaje(cliente, b'OK')
                    upload(cliente, path_directorio_archivos)

                elif operacion == 'download':
                    utils.mandar_mensaje(cliente, b'OK')
                    download(cliente, path_directorio_archivos)

                else:
                    utils.mandar_mensaje(cliente, b'ERROR')
                    print("Operación no soportada")

            else:
                print("Fallo de autenticación.")

        except Exception as e:
            print(f"Error durante la conexión: {e}")

        finally:
            # cierra conexión con el cliente específico
            cliente.close()
            print("Conexión con cliente cerrada.")

    except Exception as e:
        print(f"Error aceptando conexión: {e}")

    finally:
        # Cerrar socket servidor y liberar puerto
        ssock.close()
        print("Servidor cerrado.")

