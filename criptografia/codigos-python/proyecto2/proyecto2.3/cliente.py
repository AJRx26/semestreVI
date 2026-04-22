
import socket
import threading
import sys
import base64

import mensajes

def conectar_servidor(host, puerto):
    # socket para IP v4
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((host, int(puerto)))
        return cliente
    except:
        print('Servidor inalcanzable')
        exit()

# leer llave de cifrado
def leer_llave(path):
    with open(path, 'rb') as f:
        return base64.b64decode(f.read())

# ya madamas agrege llave cifrado y mac 
def leer_mensajes(cliente, llave_cifrado, llave_mac):
    while True:
        try:
            mensaje = mensajes.leer_mensaje(cliente, llave_cifrado, llave_mac)
        except Exception:
            break
        print(mensaje.decode('utf-8'))

def enviar_mensaje_loop(cliente, llave_cifrado, llave_mac):
    mensaje = b''
    while mensaje.strip() != b'exit':
        mensaje = input('Mensaje: ')
        mensaje = mensaje.encode('utf-8')
        mensajes.mandar_mensaje(cliente, mensaje, llave_cifrado, llave_mac)

# agregue llave cifrado y mac a la funcion main para que se puedan usar en los mensajes
if __name__ == '__main__':
    host = sys.argv[1]
    puerto = sys.argv[2]
    path_key = sys.argv[3]
    path_mac = sys.argv[4]
    usuario = sys.argv[5]
    llave_cifrado = leer_llave(path_key)
    llave_mac = leer_llave(path_mac)
    cliente = conectar_servidor(host, puerto)
    cliente.sendall(llave_cifrado) # enviar llave de cifrado al servidor
    cliente.sendall(llave_mac) # enviar llave de mac al servidor
    cliente.sendall(bytes([len(usuario)]))
    cliente.sendall(usuario.encode('utf-8'))
    hilo = threading.Thread(target=leer_mensajes, args=(cliente, llave_cifrado, llave_mac))
    hilo.start()
    enviar_mensaje_loop(cliente, llave_cifrado, llave_mac)
    cliente.close()
    hilo.join()
