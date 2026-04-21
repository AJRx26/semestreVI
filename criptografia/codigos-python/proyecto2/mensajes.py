"""
mensajes.py

Módulo utilitario para manejo de mensajes de chat (sin cambios respecto al original).
"""

DELIMITADOR = b'\r\n'


def quitar_delimitador(mensaje):
    if not mensaje.endswith(DELIMITADOR):
        return mensaje
    return mensaje[:-len(DELIMITADOR)]


def leer_mensaje(socket):
    chunk = socket.recv(4096)
    mensaje = b''
    while not chunk.endswith(DELIMITADOR):
        mensaje += chunk
        chunk = socket.recv(4096)
    mensaje += chunk
    return quitar_delimitador(mensaje)


def mandar_mensaje(socket, mensaje):
    socket.send(mensaje + DELIMITADOR)
