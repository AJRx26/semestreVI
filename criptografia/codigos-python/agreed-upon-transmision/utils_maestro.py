def regresar_bytes(path_archivo):
    contenido = ''
    with open(path_archivo, 'rb') as archivo:
        contenido = archivo.read()
    return contenido
