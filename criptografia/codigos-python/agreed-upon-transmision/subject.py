import firmas
import sys
import generarLlaves
import utils
import base64

if __name__ == '__main__':
    path_nonce = sys.argv[1]
    path_privada_subject = sys.argv[2]

    nonce = utils.regresar_bytes(path_nonce)
    llave_privada = generarLlaves.convertir_bytes_llave_privada(utils.regresar_bytes(path_privada_subject))
    firma = firmas.firmar(nonce, llave_privada)
    print(base64.b64encode(firma))
