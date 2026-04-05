import argparse
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

def archivo_a_bytes(ruta):
    with open(ruta, 'rb') as entrada:
        return entrada.read()

def desserializar_privada(ruta_pem):
    binario = b''
    with open(ruta_pem, 'rb') as entrada:
        binario = entrada.read()
    return serialization.load_pem_private_key(
        binario,
        backend=default_backend(),
        password=None)

def desserializar_publica(ruta_pem):
    binario = b''
    with open(ruta_pem, 'rb') as entrada:
        binario = entrada.read()
    return serialization.load_pem_public_key(
        binario,
        backend=default_backend())


if __name__ == '__main__':
    all_args =  argparse.ArgumentParser()    
    all_args.add_argument("--llave", help="Ruta de entrada llave a utilizar", required=True)
    all_args.add_argument("--entrada", help="Ruta de entrada del archivo a procesar", required=True)
    all_args.add_argument("--salida", help="Ruta de salida del proceso", required=True)
    all_args.add_argument("--operacion", help="cifrar o descifrar", required=True)
    args = vars(all_args.parse_args())
    op = args['operacion']
    if op == 'cifrar':
        publica = desserializar_publica(args['llave'])
        binario = archivo_a_bytes(args['entrada'])
        m = bytes_to_int(binario)
        c = simple_rsa_encrypt(m, publica)
        binario = int_to_bytes(c)
        with open(args['salida'], 'wb') as salida:
            salida.write(binario)
        
    elif op == 'descifrar':
        privada = desserializar_privada(args['llave'])
        binario = archivo_a_bytes(args['entrada'])
        c = bytes_to_int(binario)
        m = simple_rsa_decrypt(c, privada)
        binario = int_to_bytes(m)
        with open(args['salida'], 'wb') as salida:
            salida.write(binario)
    else:
        print('Operación no soportada')
        exit(1)
