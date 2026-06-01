import sys
import socket
import os
import utils

USUARIO = 'pepito'
PASSWORD = 'pepito2020'

def crear_socket_servidor(puerto):
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind(('', int(puerto)))  # hace el bind en cualquier interfaz disponible
    return mySocket


def esperar_cliente(servidor):
    servidor.listen(1) # peticiones de conexion simultaneas
    cliente, addr = servidor.accept() # bloqueante, hasta que llegue una peticion
    return cliente

def autenticar_usuario(cliente):
    datos = cliente.recv(4096)
    credenciales = datos.decode('utf-8')
    usuario = credenciales.split(':')[0]
    password = credenciales.split(':')[1]
    if USUARIO == usuario and PASSWORD == password:
        return True
    return False

def upload(cliente, path_directorio_archivos):
    nombre_archivo = cliente.recv(100)
    cliente.send(b'OK')
    archivo = open('%s/%s' % (path_directorio_archivos, nombre_archivo.decode('utf-8')), 'wb')
    datos = cliente.recv(4096)
    while not datos.endswith(utils.FIN_MENSAJE):
        archivo.write(datos)
        datos = cliente.recv(4096)
    archivo.write(datos[:-len(utils.FIN_MENSAJE)])

def download(cliente, path_directorio_archivos):
    nombre_archivo = cliente.recv(100)
    nombre_archivo = nombre_archivo.decode('utf-8')
    path_archivo = f'{path_directorio_archivos}/{nombre_archivo}'
    if os.path.isfile(path_archivo):
        cliente.send(b'OK')
    else:
        cliente.send(b'ERROR')
    cliente.recv(100)
    for pedazo in utils.generador_lectura(path_archivo):
        cliente.send(pedazo)
    cliente.send(utils.FIN_MENSAJE) #no cifrar

def atender_cliente(cliente, path_directorio_archivos):
    if autenticar_usuario(cliente):
        cliente.send(b'OK')
        print('Entró el cliente')
        operacion = cliente.recv(4096)
        if operacion == b'upload':
            cliente.send(b'OK')
            upload(cliente, path_directorio_archivos)
        elif operacion == b'download':
            cliente.send(b'OK')
            download(cliente, path_directorio_archivos)
        else:
            print('Operación no soportada')
            cliente.close()
            exit(1)
    else:
        cliente.send(b'Denegado')
        print('Se denegó el acceso al cliente')
        cliente.close()
        servidor.close()
        exit(1)


if __name__ == '__main__':
    puerto = sys.argv[1]
    path_directorio_archivos = sys.argv[2]
    servidor = crear_socket_servidor(puerto)
    cliente = esperar_cliente(servidor)

    #Establecer sesion segura aqui
    
    atender_cliente(cliente, path_directorio_archivos)

    print('OK')

    cliente.close()
    servidor.close()


