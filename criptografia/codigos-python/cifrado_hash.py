import sys
import hashlib
import os


def ayuda():
    mensaje = """
    Uso: python3 cifrado_hash.py <archivo_entrada> <archivo_salida> <shift> <operacion>

    Cifra y descifra cualquier archivo usando cifrado cesar en los bytes y que verifica el hash SHA-256

    Argumentos:
        archivo_entrada: Nombre del archivo de origen a cifrar o descifrar
        archivo_salida: Nombre del archivo resultante
        shift: Numero de recorrimiento
        accion: c para cifrar y d para descifrar

    cifrado_hash prueba.txt prueba.enc 3 -c
    cifrado_hash prueba.enc prueba.txt 3 -d
    """
    print(mensaje)
    exit(0)


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
    with open(path_salida, "wb") as salida:
        for chunk in open(path_entrada, "rb"):
            chunk_cifrado = []
            for byte in chunk:
                byte_cifrado = funcion(byte, shift)
                chunk_cifrado.append(byte_cifrado)
            salida.write(bytes(chunk_cifrado))
            hasher.update(chunk)
        salida.write(hasher.digest())


def _DESprocesar_archivo(
    path_entrada: str, path_salida: str, shift: int, funcion, tamano: int
) -> None:
    """
    Descifra hasta 'tamano' bytes,
    verifica hash
    """

    hasher = hashlib.sha256()
    leido = 0
    tam_chunk = 4096

    with open(path_entrada, "rb") as entrada, open(path_salida, "wb") as salida:

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

        if hash_calculado == hash_guardado:
            print("Archivo no modificado")
            print("Hash original: ", hash_guardado)
            print("Hash nuevo: ", hash_calculado)
        else:
            print("CUIDADO!!! ARCHIVO MODIFICADO")
            print("Hash orignal: ", hash_guardado)
            print("Hash nuevo: ", hash_calculado)


def cifrar_archivo(path_entrada: str, path_salida: str, shift: int) -> None:
    """
    Cifra el archivo dado.
    returns: None
    """
    _procesar_archivo(path_entrada, path_salida, shift, cifrarByte)


def descifrar_archivo(path_entrada: str, path_salida: str, shift: int, tamano) -> None:
    """
    Descifra el archivo dado.
    returns: None
    """
    _DESprocesar_archivo(path_entrada, path_salida, shift, descifrarByte, tamano)


if __name__ == "__main__":
    entrada = sys.argv[1]
    salida = sys.argv[2]
    shift = int(sys.argv[3])
    accion = sys.argv[4]

    if accion == "-c":
        cifrar_archivo(entrada, salida, shift)
    elif accion == "-d":
        tamano = os.path.getsize(entrada) - 32
        descifrar_archivo(entrada, salida, shift, tamano)
    else:
        print("Operación no valida")
        ayuda()
        exit(1)
