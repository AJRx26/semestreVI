import sys


def cifrarByte(byte: int, shift: int) -> int:
    """
    Función para cifrar un byte.

    byte: int, shift: int
    returns: int 
    """
    return (byte + shift) % 256


def descifrarByte(byte: int, shift: int) -> int:
    """
    Función para descifrar un byte.

    byte: int, shift: int
    returns: int 
    """
    return (byte - shift) % 256
    


def _procesar_archivo(path_entrada: str, path_salida: str, shift: int, funcion) -> None:
    """
    Cifra el archivo de entrada y lo guarda cifrado en la ruta destino.

    path_entrada: str
    path_salida: str
    shift: int
    returns: None 
    """
    with open(path_salida, 'wb') as salida:
        for chunk in open(path_entrada, 'rb'):
            chunk_cifrado = []
            for byte in chunk:
                byte_cifrado = funcion(byte, shift)
                chunk_cifrado.append(byte_cifrado)
            salida.write(bytes(chunk_cifrado))


            
def cifrar_archivo(path_entrada: str, path_salida: str, shift: int) -> None:
    """
    Cifra el archivo dado.

    
    returns: None 
    """
    _procesar_archivo(path_entrada, path_salida, shift, cifrarByte)


def descifrar_archivo(path_entrada: str, path_salida: str, shift: int) -> None:
    """
    Descifra el archivo dado.

    
    returns: None 
    """
    _procesar_archivo(path_entrada, path_salida, shift, descifrarByte)
    
if __name__ == '__main__':
    entrada = sys.argv[1]
    salida = sys.argv[2]
    shift = int(sys.argv[3])
    op = sys.argv[4]

    if op == 'cifrar':
        cifrar_archivo(entrada, salida, shift)
    elif op == 'descifrar':
        descifrar_archivo(entrada, salida, shift)
    else:
        print('Operación no soportada')
        exit(1)
    
    
