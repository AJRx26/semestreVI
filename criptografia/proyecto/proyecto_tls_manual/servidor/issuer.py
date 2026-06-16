import generar_llaves
import sys
import firmas
import utils
import json

ISSUER_NAME = 'WACKO'
    

def generar_certificado(subject_name, llave_publica_subject, llave_privada_issuer):
    certificado = {}
    certificado['subject'] = subject_name
    certificado['issuer'] = ISSUER_NAME
    certificado['public_key'] = llave_publica_subject.decode('utf-8')
    mensaje = json.dumps(certificado).encode('utf-8')
    firma = firmas.firmar(mensaje, llave_privada_issuer)
    print(len(firma))
    return mensaje + firma

if __name__ == '__main__':
    nombre_subject = sys.argv[1]
    path_subject_public = sys.argv[2]
    path_issuer_private = sys.argv[3]
    path_salida = sys.argv[4]

    llave_publica_subject = utils.regresar_bytes(path_subject_public)
    contenido = utils.regresar_bytes(path_issuer_private)
    llave_privada_issuer = generar_llaves.convertir_bytes_llave_privada(contenido)

    certificado = generar_certificado(nombre_subject, llave_publica_subject, llave_privada_issuer)
    with open(path_salida, 'wb') as archivo:
        archivo.write(certificado)
    
