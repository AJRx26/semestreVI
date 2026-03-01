import sys
import hashlib
import os


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
    hasher = hashlib.sha256()
    with open(path_salida, 'wb') as salida:
        for chunk in open(path_entrada, 'rb'):
            chunk_cifrado = []
            for byte in chunk:
                byte_cifrado = funcion(byte, shift)
                chunk_cifrado.append(byte_cifrado)
            salida.write(bytes(chunk_cifrado))
            hasher.update(chunk)
        salida.write(hasher.digest())





def _DESprocesar_archivo(path_entrada: str, path_salida: str, shift: int, funcion, tamano: int) -> None:
    """
    Descifra hasta 'tamano' bytes,
    verifica hash
    """

    hasher = hashlib.sha256()
    leido = 0
    tam_chunk = 4096

    with open(path_entrada, 'rb') as entrada, open(path_salida, 'wb') as salida:

        while leido < tamano:
            bytes_restantes = tamano - leido
            chunk = entrada.read(min(tam_chunk, bytes_restantes))
            if not chunk:
                break

            chunk_descifrado = bytes(funcion(b, shift) for b in chunk)
            salida.write(chunk_descifrado)

            hasher.update(chunk_descifrado)


            leido += len(chunk)

        hash_guardado = entrada.read(32)

        hash_calculado = hasher.digest()


#        print("\n--- HASHES ---") USO DE VOSUAL DE COMPROBACION
#        print(f"Hash calculado : {hash_calculado.hex()}") 1
#        print(f"Hash guardado  : {hash_guardado.hex()}")2

        if hash_calculado == hash_guardado:
            print(" Archivo SIN  modificaciones")
        else:
            print("CUIDADO ARCHIVO MODIFICADO ")


            
def cifrar_archivo(path_entrada: str, path_salida: str, shift: int) -> None:
    """
    Cifra el archivo dado.

    
    returns: None 
    """
    _procesar_archivo(path_entrada, path_salida, shift, cifrarByte)


def descifrar_archivo(path_entrada: str, path_salida: str, shift: int,tamano) -> None:
    """
    Descifra el archivo dado.

    
    returns: None 
    """
    _DESprocesar_archivo(path_entrada, path_salida, shift, descifrarByte, tamano)
    
if __name__ == '__main__':
    entrada = sys.argv[1]
    salida = sys.argv[2]
    shift = int(sys.argv[3])
    op = sys.argv[4]

    if op == 'cifrar':
        cifrar_archivo(entrada, salida, shift)
    elif op == 'descifrar':
        tamano = (os.path.getsize(entrada)-32)
        descifrar_archivo(entrada, salida, shift,tamano)
    else:
        print('Operación no soportada')
        exit(1)
    
    
