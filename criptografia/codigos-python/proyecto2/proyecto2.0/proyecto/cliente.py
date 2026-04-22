
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
    except Exception:
        print('Servidor inalcanzable')
        exit()

# leer llave de cifrado
def leer_llave(path):
    with open(path, 'rb') as f:
        return base64.b64decode(f.read())

# ya madamas agrege llave cifrado y mac 
def leer_mensajes(cliente, llave_cifrado, llave_mac):
    try:
        while True:
            mensaje = mensajes.leer_mensaje(cliente, llave_cifrado, llave_mac)
            print('-->' + mensaje.decode('utf-8'))
            print('Mensaje: ', end='', flush=True)
    except Exception:
        print('\n[!] Conexion cerrada por el servidor.')

#agregue la funcion de salida, se lee el mensaje y se envia
def enviar_mensaje_loop(cliente, llave_cifrado, llave_mac):
    while True:
        try:
            texto = input("Mensaje: ")
        except EOFError:
            break
        mensaje = texto.encode('utf-8')
        mensajes.mandar_mensaje(cliente, mensaje, llave_cifrado, llave_mac)
        if texto.strip() == "exit":
            print("Desconectandose...")
            cliente.close()
            break

# agregue llave cifrado y mac a la funcion main para que se puedan usar en los mensajes
if __name__ == '__main__':
    host = sys.argv[1]
    puerto = sys.argv[2]
    path_key = sys.argv[3]
    path_mac = sys.argv[4]
    nombre = sys.argv[5]

    llave_cifrado = leer_llave(path_key)
    llave_mac = leer_llave(path_mac)

    cliente = conectar_servidor(host, puerto)

    cliente.send(nombre.encode('utf-8') + b'\r\n') # enviar nombre del usuario para identificarlo

    cliente.send(llave_cifrado) # enviar llave de cifrado al servidor
    cliente.send(llave_mac) # enviar llave de mac al servidor

    hilo = threading.Thread(target=leer_mensajes, args=(cliente, llave_cifrado, llave_mac))
    hilo.start()

    enviar_mensaje_loop(cliente, llave_cifrado, llave_mac)
