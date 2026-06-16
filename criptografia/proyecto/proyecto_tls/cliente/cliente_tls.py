import sys
import socket
import ssl
import json
import time
import argparse
import utils

# Establece la conexión con el servidor y realiza el handshake TLS.
def conectarse_a_servidor(host, puerto, contexto):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # wrap_socket: convierte el socket TCP en socket TLS
        cliente = contexto.wrap_socket(sock, server_hostname=host) # server_hostname: nombre esperado en el certificado
        
        # connect() dispara el handshake TLS automáticamente
        cliente.connect((host, int(puerto)))
        
        print(f"Conectado con TLS {cliente.version()}")
        return cliente

    except Exception as e:
        print(f'Error conectando: {e}')
        sys.exit(1)


def crear_contexto_tls(path_certificado_servidor):
    """
    Crea un contexto TLS cliente que confía explícitamente
    en el certificado auto-firmado del servidor.
    """
    # Cargar el certificado auto-firmado como CA de confianza
    # Esto permite que el cliente verifique que el servidor presenta exactamente este certificado durante el handshake
    context = ssl.create_default_context(cafile=path_certificado_servidor)
    
    # desactivar verificación de hostname dado que se conecta por IP en vez de nombre DNS
    context.check_hostname = False

    #desactivar verificación de certificado
    context.verify_mode = ssl.CERT_NONE
    
    return context


def autenticacion_valida(cliente, usuario, password):
    """
    Envía credenciales en texto plano (TLS las cifra automáticamente).
    """

    # Formato: "usuario:password" codificado en bytes
    credenciales = f'{usuario}:{password}'.encode('utf-8')

    # envia credenciales (TLS cifra automáticamente en el socket)
    utils.mandar_mensaje(cliente, credenciales)
    
    #recibe respuesta del servidor
    respuesta = utils.leer_mensaje(cliente)
    return respuesta == b'OK'


def upload(cliente, path_archivo):
    """
    Sube un archivo al servidor. TLS maneja la confidencialidad e integridad.
    """

    #extraer el nombre del archivo sin rutas
    nombre_archivo = path_archivo.split('/')[-1].encode('utf-8')

    #envia nombre del archivo
    utils.mandar_mensaje(cliente, nombre_archivo)

    # espera confirmación del servidor
    respuesta = utils.leer_mensaje(cliente)
    if respuesta != b'OK':
        print('El servidor rechazó la subida')
        return

    # leer y enviar por segmentos un archivo
    for pedazo in utils.crear_generador_lectura(path_archivo):
        utils.mandar_mensaje(cliente, pedazo)

    #fin de transferencia
    utils.mandar_mensaje(cliente, b'FIN')
    print(f"Archivo '{nombre_archivo.decode()}' subido correctamente.")


def download(cliente, path_archivo):
    """
    Descarga un archivo del servidor. TLS maneja la confidencialidad e integridad.
    """
    # extraer solo el nombre del archivo
    nombre_archivo = path_archivo.split('/')[-1].encode('utf-8')

    #solicitar archivo
    utils.mandar_mensaje(cliente, nombre_archivo)

    #verifica respuesta
    respuesta = utils.leer_mensaje(cliente)
    if respuesta != b'OK':
        print('No existe el archivo en el servidor')
        return

    # guardar archivo
    with open(path_archivo, 'wb') as archivo:
        while True:
            #recibe el siguiente segmento
            datos = utils.leer_mensaje(cliente)

            if datos == b'FIN':
                break

            archivo.write(datos)
    
    print(f"Archivo '{nombre_archivo.decode()}' descargado correctamente.")


def operar(cliente, operacion, path_archivo, usuario, password):
    # autenticacion
    if autenticacion_valida(cliente, usuario, password):
        print('Autenticación exitosa')

        #pedir operacion
        utils.mandar_mensaje(cliente, operacion.encode('utf-8'))
        confirmacion = utils.leer_mensaje(cliente).decode('utf-8')

        if confirmacion != 'OK':
            print('El servidor rechazó la operación')
            return

        #operacion descargar/subir
        if operacion == 'upload':
            upload(cliente, path_archivo)
        elif operacion == 'download':
            download(cliente, path_archivo)
        else:
            print('Operación no soportada')
            sys.exit(1)
    else:
        print('La autenticación falló')
        cliente.close()
        sys.exit(1)


if __name__ == '__main__':
    all_args = argparse.ArgumentParser(description="Proyecto Final Criptografia - Cliente TLS")
    all_args.add_argument("--ip", required=True, help="IP del servidor repositorio")
    all_args.add_argument("-p", "--puerto", type=int, required=True, help="Puerto del servidor repositorio")
    all_args.add_argument("-a", "--archivo", required=True, help="Archivo que se quiere descargar/subir")
    modo = all_args.add_mutually_exclusive_group(required=True)
    modo.add_argument("--upload", action="store_true", help="Sube un archivo al repositorio")
    modo.add_argument("--download", action="store_true", help="Descarga un archivo del repositorio")
    all_args.add_argument("-u", "--user", required=True, help="Usuario con el que se desea ingresar al servidor")
    all_args.add_argument("--password", required=True, help="Contrasena del usuario")
    all_args.add_argument("-c", "--certificado", required=True, help="Ruta del certificado del servidor (.crt)")

    args = all_args.parse_args()

    host = args.ip
    puerto = args.puerto
    path_archivo = args.archivo
    path_certificado = args.certificado

    if args.upload:
        operacion = "upload"
    elif args.download:
        operacion = "download"

    usuario = args.user
    password = args.password

    #Crear contexto TLS con certificado del servidor
    contexto = crear_contexto_tls(path_certificado)

    #conectar al servidor
    cliente = conectarse_a_servidor(host, puerto, contexto)

    try:
        operar(cliente, operacion, path_archivo, usuario, password)
        print("Operación completada con éxito")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cliente.close()
