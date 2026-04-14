# PELIGRO esta implementación de CBC–MAC esta rota y es insegura
# NO LA USES
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def ayuda():
    mensaje = """
    Script que simula un ataque antepuesto en CBC-MAC.

    1. Cipher Block Chaining
    2. Un MAC es un tag, es info extra que se agrega al regalo (contenido principal)

    tag = t
    mensaje (cifrado) = m1
    MAC de mensaje = t1
    Se envian m1 y t1 al receptor

    AES se limita a cifrar 128 bits (16 bytes) de bloque a la vez. AES-CBC encadena la salida de un bloque cifrado con el siguiente. En si el ultimo bloque de CBC es un MAC.

    Si hay dos mensajes M1 y M2 con sus tags t1 y t2 generados con la misma llave k, se puede crear un nuevo mensaje M3 cuyo tag sea igual a t1 o t2.

    M1 es agregado al inicio de M2: M1+M2
    M3 es una mezcla de M1 y M2

    1. Recuperar el primer bloque de M2, es decir, M21 (16 bytes)
    2. Recupera el resto de bloques de M2, M2r
    3. Obtener M'2, que es el resultado de t1 XOR M21
    4. Finalmente M3 es el resultado de concatenar M1 + M'2 + M2r
    5. Con esto t3 = t2 (dado que antepusimos m1)
    """

def calcular_xor_bloque(bloque1: bytes, bloque2: bytes) -> bytes:
    """
    Calcula el XOR entre bloques.
    returns: None
    """
    tam_bloque = len(bloque1)
    if len(bloque2) < len(bloque1):
        tam_bloque = len(bloque2)

    res = []
    for i in range(tam_bloque):
        res.append(bloque1[i] ^ bloque2[i])
    return bytes(res)

def cifrar(message, key):
    aesCipher = Cipher(
        algorithms.AES(key), modes.CBC(bytes(16)), backend=default_backend()
    )
    aesEncryptor = aesCipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message) + padder.finalize()
    cifrado = aesEncryptor.update(padded_message)
    return cifrado

def descifrar(message, key):
    aesCipher = Cipher(
        algorithms.AES(key), modes.CBC(bytes(16)), backend=default_backend()
    )
    aesDecryptor = aesCipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()
    descifrado = aesDecryptor.update(message)
    mensaje = unpadder.update(descifrado) + unpadder.finalize()
    return mensaje

def ataque(M1, M2):
    t1 = M1[-16:]
    M21 = M2[:16]
    M2r = M2[16:]
    M_prima2 = calcular_xor_bloque(t1, M21)
    M3 = M1 + M_prima2 + M2r
    return M3, M_prima2, M2r

def descifrar_ataque(message, key):
    aesCipher = Cipher(
        algorithms.AES(key), modes.CBC(bytes(16)), backend=default_backend()
    )
    aesDecryptor = aesCipher.decryptor()
    # unpadder = padding.PKCS7(128).unpadder()
    descifrado = aesDecryptor.update(message)
    # mensaje = unpadder.update(descifrado) + unpadder.finalize()
    return descifrado

if __name__ == "__main__":
    key = os.urandom(32)
    message1 = b"Hola soy Skull!!"
    message2 = b"Quien eres ?????"
    #message1 = b"hello world, hello world, hello world, hello world"
    #message2 = b"Hello world, hello world, hello world, hello world"

    cifrado1 = cifrar(message1, key)
    cifrado2 = cifrar(message2, key)
    cifrado3, M_prima2, M2r = ataque(cifrado1, cifrado2)

    t1 = cifrado1[-16:]
    t2 = cifrado2[-16:]
    t3 = cifrado3[-16:]

    descifrado1 = descifrar(cifrado1, key)
    descifrado2 = descifrar(cifrado2, key)
    descifrado3 = descifrar_ataque(cifrado1, key) + descifrar_ataque(M_prima2, key) + descifrar_ataque(M2r, key)

    print(f"[+] Cifrado1: {cifrado1}")
    print(f"[+] CBC-MAC1: {t1}")
    print(f"[+] Mensaje1: {descifrado1}")
    print()

    print(f"[+] Cifrado2: {cifrado2}")
    print(f"[+] CBC-MAC2: {t2}")
    print(f"[+] Mensaje2: {descifrado2}")
    print()

    print(f"[+] Cifrado3: {cifrado3}")
    print(f"[+] Mensaje3: {descifrado3}")
    print(f"[+] CBC-MAC3: {t3}")
    print(f"[+] Verificacion: {t3 == t2}")
