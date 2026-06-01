
FIN_MENSAJE = b'#!#!*'

def generador_lectura(path_archivo, tam_lectura=4096):
    archivo = open(path_archivo, 'rb')
    contenido = archivo.read(tam_lectura)
    yield contenido
    while len(contenido) == tam_lectura:
        contenido = archivo.read(tam_lectura)
        yield contenido
    archivo.close()
