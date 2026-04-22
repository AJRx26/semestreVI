"""
Servidor.

Servidor de un chat. Es una implementación incompleta:
- Falta manejo de exclusión mutua
- Falta poder desconectar de forma limpia clientes
- Falta poder identificar clientes
"""


import socket
import threading
import sys

import mensajes


def crear_socket_servidor(puerto):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('', int(puerto)))  # hace el bind en cualquier interfaz disponible
    return servidor


def recv_exact(sock, num_bytes):
    datos = b''
    while len(datos) < num_bytes:
        chunk = sock.recv(num_bytes - len(datos))
        if not chunk:
            raise ConnectionError('Conexion cerrada mientras se recibian datos')
        datos += chunk
    return datos


def broadcast(mensaje, clientes):
    for cliente, llaves in clientes:
        if llaves['llave_cifrado'] is None or llaves['llave_mac'] is None:
            continue
        try:
            mensajes.mandar_mensaje(cliente, mensaje, llaves['llave_cifrado'], llaves['llave_mac'])
        except Exception:
            # Si un cliente ya no esta disponible, el hilo de atencion lo limpiara.
            pass

        
# Hilo para leer mensajes de clientes
def atencion(cliente, clientes):
    llave_cifrado = recv_exact(cliente, 16)  # recibir llave de cifrado
    llave_mac = recv_exact(cliente, 32)  # recibir llave de mac

    for cliente_item, llaves in clientes:
        if cliente_item is cliente:
            llaves['llave_cifrado'] = llave_cifrado
            llaves['llave_mac'] = llave_mac
            break

    while True:
        try:
            mensaje = mensajes.leer_mensaje(cliente, llave_cifrado, llave_mac)
        except Exception:
            break

        if mensaje.strip() == b'exit':
            break

        broadcast(mensaje, clientes)

    clientes[:] = [par for par in clientes if par[0] is not cliente]
    cliente.close()
    

def escuchar(servidor):
    servidor.listen(5) # peticiones de conexion simultaneas
    clientes = []
    while True:
        cliente, _ = servidor.accept() # bloqueante, hasta que llegue una peticion
        clientes.append((cliente, {'llave_cifrado': None, 'llave_mac': None}))
        hiloAtencion = threading.Thread(target=atencion, args=
                                        (cliente, clientes)) # se crea un hilo de atención por cliente
        hiloAtencion.start()


if __name__ == '__main__':
    
    servidor = crear_socket_servidor(sys.argv[1])
    print('Escuchando...')
    escuchar(servidor)
