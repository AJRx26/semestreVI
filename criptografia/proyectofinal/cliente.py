import sys
import socket
import utils

USUARIO = 'pepito'
PASSWORD = 'pepito2020'

def conectarse_a_servidor(host, puerto):
    #crear socket ipv4 tcp
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((host, int(puerto)))
        return cliente
    except:
        print('Puerto cerrado')
        exit(1)

def autenticacion_valida():
    cliente.send(b'%s:%s' % (USUARIO.encode('utf-8'), PASSWORD.encode('utf-8')))
    respuesta = cliente.recv(4096)
    if respuesta == b'OK':
        return True
    else:
        return False

def upload(cliente, path_archivo):
    nombre_archivo = path_archivo.split('/')[-1]
    cliente.send(nombre_archivo.encode('utf-8'))
    cliente.recv(100)
    for pedazo in utils.generador_lectura(path_archivo):
        cliente.send(pedazo)
    cliente.send(utils.FIN_MENSAJE) #no cifrar

def download(cliente, path_archivo):
    nombre_archivo = path_archivo.split('/')[-1]
    cliente.send(nombre_archivo.encode('utf-8'))
    respuesta = cliente.recv(100)
    if respuesta != b'OK':
        print('No existe el archivo en el servidor')
        exit(1)
    cliente.send(b'ready')
    archivo = open(path_archivo, 'wb')
    datos = cliente.recv(4096)
    while not datos.endswith(utils.FIN_MENSAJE):
        archivo.write(datos)
        datos = cliente.recv(4096)
    archivo.write(datos[:-len(utils.FIN_MENSAJE)])
    
def operar(cliente, operacion, path_archivo):
    if autenticacion_valida():
        print('Pude entrar...')
        if(operacion == 'upload'):
            cliente.send(b'upload')
            confirmacion = cliente.recv(100)
            upload(cliente, path_archivo)
        elif(operacion == 'download'):
            cliente.send(b'download')
            confirmacion = cliente.recv(100)
            download(cliente, path_archivo)
        else:
            print('Operación no soportada')
            exit(1)
    else:
        print('La autenticación falló')
        cliente.close()
        exit(1)
    
if __name__ == '__main__':
    host = sys.argv[1]
    puerto = sys.argv[2]
    path_archivo = sys.argv[3]
    operacion = sys.argv[4] # upload/download
    
    cliente = conectarse_a_servidor(host, puerto)

    #Establecer sesion segura aqui

    operar(cliente, operacion, path_archivo)

    print('OK')

    cliente.close()

