import sys
import socket
import utils
import json
import time
import argparse
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import ec as ec_module

import firmas
import generar_llaves


def conectarse_a_servidor(host, puerto):
    #crear socket ipv4 tcp
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente.connect((host, int(puerto)))
        return cliente
    except:
        print('Puerto cerrado')
        exit(1)

        
# FASE 1: PREPARACIÓN DE IDENTIDAD -----------------------------------------------------------------------------
def cargar_certificado(path_certificado):
    """
    Cargamos el certificado que proporcionó el servidor.
    El certificado se separa en: [contenido del certificado] [firma] [datos del certificado]
    """
    contenido = utils.regresar_bytes(path_certificado) # se lee todo el archivo
    firma = contenido[-256:] # obtener firma-últimos 256. Llave RSA de 2048, entonces -> 2048/8 = 256 bytes
    contenido_certificado = contenido[:-256] # obtener certificado-todo excepto los últimos 256
    datos = json.loads( # convertir JSON en un doccionario
        contenido_certificado.decode('utf-8') # se convierten los bytes a texto
    )
    return datos, contenido_certificado, firma # los datos son por ejemplo el issuer o el subject


def obtener_llave_publica_servidor(path_certificado, issuer_publica):
    """
    Función que válida que el cliente realmente está hablando con el servidor.
    El cliente sólo confía en certificados emitidos por WACKO, en este caso.
    """
    # se carga el certificado 
    datos, contenido_certificado, firma = cargar_certificado(path_certificado)

    if datos['issuer'] != 'WACKO': # verifica quién emitió el certificado
        raise Exception('Issuer inválido')
    # verifica la firma con la llave pública de WACKO (la autoridad ceritifcadora)
    if not firmas.es_firma_valida(issuer_publica, firma, contenido_certificado):
        raise Exception('Certificado inválido') # calcula hash, descifra firma usando llave pública de WACKO y compara ambos hashes
    # obtener la llave pública y se convierte a bytes
    llave_publica_pem = datos['public_key'].encode('utf-8')
    
    return generar_llaves.convertir_bytes_llave_publica(llave_publica_pem) # se convierte la llave PEM en llave RSA


# --- FASE 2: ESTABLECIMIENTO DE SESIÓN SEGURA (HANDSHAKE) ---------------------------------------------------

def realizar_handshake(cliente, path_certificado, path_issuer_publica):
    """
    Se realiza el handshake en el cliente.
    """
    # cargar la llave pública del issuer SÓLO para verificar certificados 
    issuer_publica = generar_llaves.convertir_bytes_llave_publica(
        utils.regresar_bytes(path_issuer_publica) # se obtiene la llave pública RSA
    )

    llave_publica_servidor = obtener_llave_publica_servidor( # obtener la llave pública del servidor 
        path_certificado, issuer_publica
    )

    llave_publica_efimera_servidor_bytes = utils.recibir_bytes(cliente) # recibir la llave efímera del servidor
    firma = utils.recibir_bytes(cliente) # se recibe la firma del servidor (firmó la llave efímera)

    try:
        llave_publica_servidor.verify( # se verifica la firma con la llave pública obtenida del certificado
            firma,
            llave_publica_efimera_servidor_bytes,
            ec_module.ECDSA(hashes.SHA256())
        )
    except Exception:
        raise Exception('La firma del servidor no es válida')

    print("Firma de la llave efímera válida")

    # se convierte llave efímera en objeto
    llave_publica_efimera_servidor = serialization.load_pem_public_key(
        llave_publica_efimera_servidor_bytes
    )

    # 1. Genera llave privada efímera del cliente
    llave_privada_efimera_cliente = utils.generar_llave_efimera()

    # 2. Genera llave pública efímera del cliente
    llave_publica_efimera_cliente_bytes = (
        llave_privada_efimera_cliente.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )
    utils.enviar_bytes(cliente, llave_publica_efimera_cliente_bytes) # se envía la llave al servidor

    # 3. Generar secreto compartido (cliente combina su llave privada con la pública del servidor)
    shared_key = llave_privada_efimera_cliente.exchange(
        ec.ECDH(), llave_publica_efimera_servidor
    )

    # 4. Derivar llaves cruzadas
    llave_a, llave_b = utils.derivar_llaves(shared_key)
    return llave_b, llave_a  # cliente recibe con llave_b y enviar con llave_a (cruzadas)   


# --- FASE 3: AUTENTICACIÓN DEL CLIENTE ---------------------------------------------------------------------
def autenticacion_valida(cliente, llave_sesion_enviar, llave_sesion_recibir, usuario, password):
    """
    Función donde el cliente demuestra quién es enviando su usuario y contraseña de forma segura.
    """
    credenciales = f'{usuario}:{password}'.encode('utf-8') # contruye las credenciales
        
    paquete = utils.cifrar( # cifra las credenciales usando la llave para enviar 
        llave_sesion_enviar,
        credenciales, # es por ejemplo b'grissel:contraseña'
        int(time.time()) # timestamp
    )
    utils.mandar_mensaje(cliente, paquete) # Se envía el paquete al servidor
    respuesta_paquete = utils.leer_mensaje(cliente) # se espera la respuesta del servidor (OK o ERROR)
    
    respuesta = utils.descifrar( # se descifra la respuesta del servidor 
        llave_sesion_recibir,
        respuesta_paquete
    )
    
    return respuesta == b'OK' # si la respuesta es OK, pues True
    

# FASE 4 - FASE 5: OPERACIONES DE REPOSITORIO (CIFRADO DE FLUJO) Y CIERRE ----------------------------------------
def upload(cliente, path_archivo, llave_sesion_enviar, llave_sesion_recibir):
    """
    Cliente envía un archivo al servidor para que lo guarde en su repositorio. 
    """
    # Ejemplo: /home/juan/Documentos/foto.png --> solo se obtiene foto.png
    nombre_archivo = path_archivo.split('/')[-1].encode('utf-8') #obtiene nombre del archivo y -1 para seleccionar último elemento

    paquete_nombre = utils.cifrar( # se cifra el nombre del archivo
        llave_sesion_enviar,
        nombre_archivo,
        int(time.time())
    )
    utils.mandar_mensaje(cliente, paquete_nombre) # envía el nombre al servidor

    respuesta = utils.descifrar( # se espera la confirmación del servidor
        llave_sesion_recibir,
        utils.leer_mensaje(cliente)
    )

    if respuesta != b'OK':
        print('El servidor rechazó la subida')
        return

    for pedazo in utils.crear_generador_lectura(path_archivo): # leer el archivo por segmentos 
        paquete = utils.cifrar( # se cifra cada bloque 
            llave_sesion_enviar, 
            pedazo, 
            int(time.time()))
        utils.mandar_mensaje(cliente, paquete) # se envía el bloque 
        #print(f"  Segmento {i} enviado: {len(pedazo)} bytes")

    utils.mandar_mensaje( # cuando se terminan de envíar bloques se termina con un FIN
        cliente,
        utils.cifrar(llave_sesion_enviar, b'FIN', int(time.time()))
    )


def download(cliente, path_archivo, llave_sesion_enviar, llave_sesion_recibir):
    """
    Cliente descarga un archivo del servidor que está en su repositorio.
    """
    nombre_archivo = path_archivo.split('/')[-1].encode('utf-8') # Se obtiene el nombre

    paquete_nombre = utils.cifrar( # se cifra el nombre del archivo
        llave_sesion_enviar,
        nombre_archivo,
        int(time.time())
    )
    utils.mandar_mensaje(cliente, paquete_nombre) # se envía el nombre al servidor 

    respuesta = utils.descifrar( # se espera una respuesta del servidor
        llave_sesion_recibir,
        utils.leer_mensaje(cliente)
    )

    if respuesta != b'OK': # si el archivo existe 
        print('No existe el archivo en el servidor')
        return

    with open(path_archivo, 'wb') as archivo: # se crea el archivo vacío
        while True: # confienza a recibir segmentos
            paquete = utils.leer_mensaje(cliente) # se recibe un bloque cifrado
            
            datos = utils.descifrar( # se descifra el paquete 
                llave_sesion_recibir,
                paquete
            )

            if datos == b'FIN': # si es FIN, termina el ciclo
                break

            archivo.write(datos) # se escriben los bloques hasta llegar al último


def operar(cliente, operacion, path_archivo, llave_sesion_enviar, llave_sesion_recibir, usuario, password):
    """
    Función que primero verifica que el usuario es autentico y si sale bien,
    decide si se subirá o se descargará un archivo.
    """
    if autenticacion_valida(cliente, llave_sesion_enviar, llave_sesion_recibir, usuario, password):    
        print('Pude entrar...') # si el servidor acepta las credenciales, True

        utils.mandar_mensaje(cliente, operacion.encode('utf-8')) # se manda la operación
        confirmacion = utils.leer_mensaje(cliente).decode('utf-8') # espera la confirmación del servidor

        if confirmacion != 'OK':
            print('El servidor rechazó la operación')
            return
        # Entonces se hace lo que el usuario escogió
        if operacion == 'upload':
            upload(cliente, path_archivo, llave_sesion_enviar, llave_sesion_recibir)
        elif operacion == 'download':
            download(cliente, path_archivo, llave_sesion_enviar, llave_sesion_recibir)
        else:
            print('Operación no soportada')
            exit(1)
    else:
        print('La autenticación falló')
        cliente.close()
        exit(1)

    
if __name__ == '__main__':
    all_args = argparse.ArgumentParser(description="Proyecto Final Criptografia - Cliente")
    all_args.add_argument("--ip", required=True, help="IP del servidor repositorio")
    all_args.add_argument("-p", "--puerto", required=True, type=int, help="Puerto del servidor repositorio")
    all_args.add_argument("-a", "--archivo", required=True, help="Archivo que se quiere descargar/subir")
 
    modo = all_args.add_mutually_exclusive_group(required=True)
    modo.add_argument("--upload", action="store_true", help="Sube un archivo al repositorio")
    modo.add_argument("--download", action="store_true", help="Descarga un archivo del repositorio")
 
    all_args.add_argument("-u", "--user", required=True, help="Usuario con el que se desea ingresar al servidor")
    all_args.add_argument("--password", required=True, help="Contrasena del usuario")
    all_args.add_argument("-c", "--certificado", required=True, help="Ruta del certificado")
    all_args.add_argument("-i", "--issuer", required=True, help="Ruta del issuer")

    args = all_args.parse_args()

    host = args.ip
    puerto = args.puerto
    path_archivo = args.archivo

    if args.upload:
        operacion = "upload"
    elif args.download:
        operacion = "download"

    usuario = args.user
    password = args.password
    path_certificado = args.certificado
    path_issuer = args.issuer
    
    cliente = conectarse_a_servidor(host, puerto)

    #Establecer sesion segura aqui
    try:
        llave_sesion_recibir, llave_sesion_enviar = realizar_handshake(
            cliente, path_certificado, path_issuer
        )
        print("Handshake correcto")
        operar(cliente, operacion, path_archivo, llave_sesion_enviar, llave_sesion_recibir, usuario, password)
        print("OK")
    except Exception as e:
        print(f"Error: {e}")

    #print(f"Llave de sesión envíar del cliente:{llave_sesion_enviar.hex()}")
    #print(f"Llave de sesión recibir del cliente:{llave_sesion_recibir.hex()}")
    
    cliente.close()
