import socket
import threading
import sys

import mensajes

def crear_socket_servidor(puerto):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind(('', int(puerto)))  # hace el bind en cualquier interfaz disponible
    return servidor

#ya con mutex
def recv_exact(sock, num_bytes):
    datos = b''
    while len(datos) < num_bytes:
        chunk = sock.recv(num_bytes - len(datos))
        if not chunk:
            raise ConnectionError('Conexion cerrada mientras se recibian datos')
        datos += chunk
    return datos

def broadcast(mensaje, clientes, lock):
    with lock:
        copia_clientes = list(clientes)

    for cliente, llaves in copia_clientes:
        if llaves['llave_cifrado'] is None or llaves['llave_mac'] is None:
            continue
        try:
            mensajes.mandar_mensaje(cliente, mensaje, llaves['llave_cifrado'], llaves['llave_mac'])
        except:
            # Si un cliente ya no esta disponible, el hilo de atencion lo limpiara.
            pass

# Hilo para leer mensajes de clientes
def atencion(cliente, clientes, lock):
    llave_cifrado = recv_exact(cliente, 16)  # recibir llave de cifrado
    llave_mac = recv_exact(cliente, 32)  # recibir llave de mac
    len_usuario = recv_exact(cliente, 1)[0] #recibir longitud de usuario
    usuario = recv_exact(cliente, len_usuario).decode('utf-8') #recibir nombre de usuario

    with lock:
        for cliente_item, llaves in clientes:
            if cliente_item is cliente:
                llaves['llave_cifrado'] = llave_cifrado
                llaves['llave_mac'] = llave_mac
                llaves['usuario'] = usuario
                break

    mensajes.mandar_mensaje(cliente, b'ACK: Conexion establecidad', llave_cifrado, llave_mac)

    print(f'[+] Cliente conectado: {usuario}')

    broadcast(f'--- {usuario} entro al chat ---'.encode(), clientes, lock)

    while True:
        try:
            mensaje = mensajes.leer_mensaje(cliente, llave_cifrado, llave_mac)
        except Exception:
            break

        if mensaje.strip() == b'exit':
            try:
                mensajes.mandar_mensaje(cliente, b'Conexion cerrada', llave_cifrado, llave_mac)
                exit()
            except:
                pass
            break
        mensaje_con_usuario = usuario.encode('utf-8') + b' --> ' + mensaje
        broadcast(mensaje_con_usuario, clientes, lock)

    # Esta linea modifica la lista de clientes conectados en caso que un cliente se desconecte, modifica la lista original
    with lock:
        clientes[:] = [par for par in clientes if par[0] is not cliente]

    # Muestra la desconexion a los demas clientes
    print(f'[+] Cliente desconectado: {usuario}')
    broadcast(f'--- {usuario} salio del chat ---'.encode(), clientes, lock)
    cliente.close()

def escuchar(servidor):
    servidor.listen(5) # peticiones de conexion simultaneas
    clientes = [] # lista con todos los clientes conectados actualmente
    lock = threading.Lock() #se crea el mutex

    while True:
        cliente, _ = servidor.accept() # bloqueante, hasta que llegue una peticion

        with lock: # se usa mutex para evitar condiciones de carrera al modificar/acceder al listado
            clientes.append((cliente, {'llave_cifrado': None, 'llave_mac': None}))
        hiloAtencion = threading.Thread(target=atencion, args=
                                        (cliente, clientes, lock)) # se crea un hilo de atención por cliente y se usa el mismo mutex para todos
        hiloAtencion.start()

if __name__ == '__main__':
    servidor = crear_socket_servidor(sys.argv[1])
    print('Escuchando...')
    escuchar(servidor)
