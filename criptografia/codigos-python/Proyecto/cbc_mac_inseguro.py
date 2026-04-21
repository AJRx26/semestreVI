
# PELIGRO esta implementación de CBC–MAC esta rota y es insegura
# NO LA USES
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def BROKEN_CBCMAC1(message, key):
    aesCipher = Cipher(algorithms.AES (key),
                       modes.CBC(bytes(16)), # 16 bytes cero
                       backend=default_backend())
    aesEncryptor = aesCipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message)+padder.finalize()    
    ciphertext = aesEncryptor.update(padded_message)
    return ciphertext[-16:] # el MAC son los ultimos 16 bytes

if __name__ == '__main__':
    key = os.urandom(32)
    print(BROKEN_CBCMAC1(b"hello world, hello world, hello world, hello world", key))
    print(BROKEN_CBCMAC1(b"Hello world, hello world, hello world, hello world", key))


