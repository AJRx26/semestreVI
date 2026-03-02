import sys       # Permite acceder a los argumentos enviados por línea de comandos
import hashlib   # Proporciona funciones de hash criptográfico (usamos SHA-256)
import os        # Permite interactuar con el sistema operativo (ej. tamaño de archivos)


def ayuda():
    """
    Muestra en pantalla las instrucciones de uso del script.
    Se ejecuta cuando los argumentos no son válidos o hay error.
    """
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
    exit(0)  # Termina la ejecución del programa


def cifrarByte(byte: int, shift: int) -> int:
    """
    Aplica un desplazamiento tipo César a un byte.

    Parámetros:
        byte  : valor entero entre 0 y 255
        shift : número de desplazamiento

    Retorna:
        Nuevo valor del byte desplazado dentro del rango 0-255
    """
    return (byte + shift) % 256  # Módulo 256 mantiene el resultado como byte válido


def descifrarByte(byte: int, shift: int) -> int:
    """
    Revierte el desplazamiento aplicado al byte.

    Parámetros:
        byte  : valor entero entre 0 y 255
        shift : número de desplazamiento

    Retorna:
        Byte original antes del cifrado
    """
    return (byte - shift) % 256  # Operación inversa al cifrado


def _procesar_archivo(path_entrada: str, path_salida: str, shift: int, funcion) -> None:
    """
    Procesa el archivo para aplicar una transformación byte a byte (cifrado o descifrado).

    Parámetros:
        path_entrada : ruta del archivo original
        path_salida  : ruta donde se guardará el resultado
        shift        : desplazamiento a aplicar
        funcion      : función que se aplicará a cada byte (cifrarByte o descifrarByte)

    Funcionamiento:
        - Lee el archivo de entrada en modo binario.
        - Aplica la función byte a byte.
        - Escribe el resultado en el archivo de salida.
        - Calcula el hash SHA-256 del contenido original.
        - Añade el hash al final del archivo generado.
    """

    # Inicializa objeto SHA-256 para calcular el hash
    hasher = hashlib.sha256()

    # Abre archivo de salida en modo binario escritura
    with open(path_salida, "wb") as salida:

        # Recorre el archivo de entrada en modo binario
        for chunk in open(path_entrada, "rb"):

            # Lista temporal para almacenar bytes transformados
            chunk_cifrado = []

            # Procesa cada byte individualmente
            for byte in chunk:
                byte_cifrado = funcion(byte, shift)
                chunk_cifrado.append(byte_cifrado)

            # Escribe los bytes procesados al archivo de salida
            salida.write(bytes(chunk_cifrado))

            # Actualiza el hash con el contenido ORIGINAL (no el transformado)
            hasher.update(chunk)

        # Obtiene el hash final en formato binario (32 bytes)
        hash = hasher.digest()

        # Añade el hash al final del archivo
        salida.write(hash)

    # Muestra el hash generado
    print("Hash generado: ", hash)


def _procesar_cifrado(path_entrada: str, path_salida: str, shift: int, funcion, tamano: int) -> None:
    """
    Procesa el archivo cifrado para descifrarlo y verificar integridad.

    Parámetros:
        path_entrada : archivo cifrado
        path_salida  : archivo descifrado resultante
        shift        : desplazamiento usado
        funcion      : función de transformación (normalmente descifrarByte)
        tamano       : tamaño real del contenido sin incluir el hash

    Funcionamiento:
        - Lee únicamente los primeros 'tamano' bytes (datos cifrados).
        - Descifra byte a byte.
        - Calcula el SHA-256 del contenido descifrado.
        - Lee los últimos 32 bytes (hash guardado).
        - Compara ambos hashes para verificar integridad.
    """

    hasher = hashlib.sha256()  # Inicializa objeto hash
    leido = 0                  # Contador de bytes leídos
    tam_chunk = 4096           # Tamaño de bloque de lectura

    # Abre archivo de entrada y salida en modo binario
    with open(path_entrada, "rb") as entrada, open(path_salida, "wb") as salida:

        # Procesa solo los bytes correspondientes al contenido cifrado
        while leido < tamano:

            bytes_restantes = tamano - leido

            # Lee en bloques de hasta 4096 bytes
            chunk = entrada.read(min(tam_chunk, bytes_restantes))

            if not chunk:
                break

            # Aplica transformación byte a byte
            chunk_descifrado = bytes(funcion(b, shift) for b in chunk)

            # Escribe datos descifrados
            salida.write(chunk_descifrado)

            # Actualiza hash con contenido descifrado
            hasher.update(chunk_descifrado)

            leido += len(chunk)

        # Lee los últimos 32 bytes (hash almacenado)
        hash_guardado = entrada.read(32)

        # Calcula hash del contenido descifrado
        hash_calculado = hasher.digest()

        # Compara ambos hashes
        if hash_calculado == hash_guardado:
            print("Archivo no modificado")
            print("Hash original: ", hash_guardado)
            print("Hash nuevo: ", hash_calculado)
        else:
            print("CUIDADO!!! ARCHIVO MODIFICADO")
            print("Hash original: ", hash_guardado)
            print("Hash nuevo: ", hash_calculado)


def cifrar_archivo(path_entrada: str, path_salida: str, shift: int) -> None:
    """
    Función envoltura para cifrado.
    Llama a _procesar_archivo usando la función cifrarByte.
    """
    _procesar_archivo(path_entrada, path_salida, shift, cifrarByte)


def descifrar_archivo(path_entrada: str, path_salida: str, shift: int, tamano) -> None:
    """
    Función envoltura para descifrado.
    Llama a _procesar_cifrado usando descifrarByte.
    """
    _procesar_cifrado(path_entrada, path_salida, shift, descifrarByte, tamano)


# ==========================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ==========================================================

if __name__ == "__main__":

    # Argumentos recibidos desde la terminal
    entrada = sys.argv[1]   # Archivo de entrada
    salida = sys.argv[2]    # Archivo de salida
    shift = int(sys.argv[3])  # Desplazamiento convertido a entero
    accion = sys.argv[4]    # Tipo de operación (-c o -d)

    if accion == "-c":
        # Cifrado
        cifrar_archivo(entrada, salida, shift)

    elif accion == "-d":
        # Calcula tamaño real excluyendo los 32 bytes del hash
        tamano = os.path.getsize(entrada) - 32

        # Descifrado
        descifrar_archivo(entrada, salida, shift, tamano)

    else:
        print("Operación no valida")
        ayuda()
