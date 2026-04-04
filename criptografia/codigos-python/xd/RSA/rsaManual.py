import gmpy2, os, binascii
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

#Estas funciones son inseguras
def simple_rsa_encrypt(m, publickey):
    # public_numbers regresa una estructura de datos con 'e' y 'n'
    numbers = publickey.public_numbers()
    # el cifrado es (m ** e) % n
    return gmpy2.powmod(m, numbers.e, numbers.n)

def simple_rsa_decrypt(c, privatekey):
    # private_numbers regresa una estructura de datos con 'd' y 'n'
    numbers = privatekey.private_numbers()
    # el descifrado es (c ** d) % n
    return gmpy2.powmod(c, numbers.d, numbers.public_numbers.n)

# RSA opera con numeros enteros, no bytes
# es neceario convertir un archivo de bytes a un entero para procesarlo
def int_to_bytes(i):
    # asegurarse de que es un entero python
    i = int(i)
    return i.to_bytes((i.bit_length()+7)//8, byteorder='big')

def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')

