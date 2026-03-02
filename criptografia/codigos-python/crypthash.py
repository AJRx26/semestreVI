import crypt
import sys


def ayuda():
    mensaje = """
    Uso: shadow_cracker.py <archivo_shadow> <diccionario>

    Encontrar passwords a traves de un archivo shadow usando un ataque de diccionario

    Argumentos:
        archivo_shadow: Archivo shaodw a revisar
        diccionario: Archivo diccionario que se usara para el ataque

    Ejemplo:
        shadow_cracker /etc/shadow diccionario.txt
        shawdo_cracker shadow /tmp/diccionario.txt
    """


def extraer_hash(archivo_shadow: str):
    hashes = []
    with open(archivo_shadow, "r") as archivo:
        for linea in archivo:
            partes = linea.strip().split(":")

            if not hash_completo.startswith("$"):
                continue

            salt = hash_completo[: hash_completo.rindex("$") + 1]
            hashes.append((salt, hash_completo))
    return hashes


def buscar_password(diccionario, salt, hash_completo):
    with open(diccionario, "r") as archivo:
        for palabra in archivo:
            palabra = palabra.strip()

            prueba = crypt.crypt(palabra, salt)

            if prueba == hash_completo:
                return palabra
    return None


if __name__ == "__main__":
    archivo_shadow = sys.argv[1]
    diccionario = sys.argv[2]

    hashes = extraer_hash(archivo_shadow)
    for salt, hash_completo in hashes:
        password = buscar_password(diccionario, salt, hash_completo)
        if password:
            print("Usuario: ", hash_completo, " Contraseña: ", password)
        else:
            print("Usuario: ", hash_completo, " Contraseña: No encontrada")
