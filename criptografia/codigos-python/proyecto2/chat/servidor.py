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

_lock = threading.lock()

def crear_socket_servidor(puerto):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('', int(puerto)))  # hace el bind en cualquier interfaz disponible
    return servidor

# ya con mutex
def broadcast(mensaje, remitente, clientes):
    mensaje_nombre = f"[{remitente}]: ".encode('utf-8') + mensaje
    with _lock:
        destinos = list(clientes)
    for cliente,llaves in destinos:
        try:
            mensajes.mandar_mensaje(cliente, mensaje_nombre, llaves['llave_cifrado'], llaves['llave_mac']) # agregar mutex
        except Exception:
            # si falla, el hilo lo limpia
            pass

#elimina un cliente de la lista
def eliminar_cliente(cliente, clientes):
    with _lock:
        clientes[:] = [(c, l) for c, l in clientes if c is not cliente]

# Hilo para leer mensajes de clientes
def atencion(cliente, clientes):
    # recibe el nombre del cliente
    chunk = cliente.recv(1024)
    nombre_bytes = b''

    while not chunk.endswith(b'\r\n'):
        nombre_bytes += chunk
        chunk = cliente.recv(1024)
    nombre = mensajes.quitar_delimitador(nombre_bytes + chunk).decode('utf-8')

    llave_cifrado = cliente.recv(32) # recibir llave de cifrado
    llave_mac = cliente.recv(32) # recibir llave de mac

    llaves = {'llave_cifrado': llave_cifrado, 'llave_mac': llave_mac}

    with _lock:
        clientes.append((cliente, llaves))

    print(f'[+] Cliente conectado: {nombre}')
    aviso = f'--- {nombre} se unio al chat ---'.encode('utf-8')
    broadcast(aviso, 'Servidor', cliente)

    try:
        while True:
            mensaje = mensajes.leer_mensaje(cliente, llave_cifrado, llave_mac)
            if mensaje.strip() == b'exit':
                break
            broadcast(mensaje, nombre, clientes)
    except Exception as e:
        print(f'Error en el cliente {nombre}: {e}')
    finally:
        eliminar_cliente(cliente, clientes)
        cliente.close()
        print(f'Cliente desconectado: {nombre}')
        aviso = f'--- {nombre} ha abandonado el chatt ---'.encode('utf-8')
        broadcast(aviso, 'Servidor', clientes)

def escuchar(servidor):
    servidor.listen(5) # peticiones de conexion simultaneas
    clientes = []
    print("Escuchando...")
    while True:
        cliente, direccion = servidor.accept() # bloqueante, hasta que llegue una peticion
        print(f'[+] Conexion entrante desde {direccion}')
        hiloAtencion = threading.Thread(target=atencion, args=
                                        (cliente, clientes)) # se crea un hilo de atención por cliente
        hiloAtencion.start()

if __name__ == '__main__':
    servidor = crear_socket_servidor(sys.argv[1])
    escuchar(servidor)
