import firmas
import utils_maestro
import sys
import json
import generarLlaves
import os
import base64

ISSUER_NAME = 'WACKO'

def es_certificado_valido(subject, datos_certificado, datos_certificado_raw, firma, publica_issuer):
    if subject != datos_certificado['subject']:
        return False
    if ISSUER_NAME != datos_certificado['issuer']:
        return False
    if not firmas.es_firma_valida(publica_issuer, firma, datos_certificado_raw):
        return False
    return True

def regresar_llave_publica_certificado(subject, certificado, publica_issuer):
    datos_certificado_raw = certificado[:-256]
    datos_certificado = json.loads(datos_certificado_raw.decode('utf-8'))
    firma = certificado[-256:]
    if not es_certificado_valido(subject, datos_certificado, datos_certificado_raw, firma, publica_issuer):
        raise Exception('El certificado no es válido')

    llave_publica_raw = datos_certificado['public_key'].encode('utf-8')
    llave_publica = generarLlaves.convertir_bytes_llave_publica(llave_publica_raw)
    return llave_publica

def verificar_challenge_response(llave_publica_certificado):
    nonce = os.urandom(128)
    with open('nonce', 'rb') as archivo:
         nonce = archivo.read()
    firma_b64 = input() #recibir en base64
    #convertir firma a binario
    firma = base64.b64decode(firma_b64)
    if not firmas.es_firma_valida(llave_publica_certificado, firma, nonce):
        raise Exception('El supuesto subject no pasó el reto')

if __name__ == '__main__':
    subject_name = sys.argv[1]
    path_certificado = sys.argv[2]
    path_publica_issuer = sys.argv[3]

    certificado = utils_maestro.regresar_bytes(path_certificado)
    publica_issuer = generarLlaves.convertir_bytes_llave_publica(utils.regresar_bytes(path_publica_issuer))

    llave_publica_certificado = regresar_llave_publica_certificado(subject_name, certificado, publica_issuer)

    verificar_challenge_response(llave_publica_certificado)
