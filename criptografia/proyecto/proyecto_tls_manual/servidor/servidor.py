import sys
import socket
import os
import hashlib
import time
import argparse
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature, InvalidTag

import utils


def crear_socket_servidor(puerto):
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind(('', int(puerto)))  # hace el bind en cualquier interfaz disponible
    return mySocket


def esperar_cliente(servidor):
    servidor.listen(1) # peticiones de conexion simultaneas
    cliente, addr = servidor.accept() # bloqueante, hasta que llegue una peticion
    return cliente


# --- FASE 2: ESTABLECIMIENTO DE SESIÓN SEGURA (HANDSHAKE) --------------------------------------------
def realizar_handshake(cliente_sock, llave_privada_servidor):
    """
    Se realiza toda la fase del Handshake.
    1. Servidor genera sus llaves efímeras
    2. Servidor firma su llave pública efímera con su llave privada permanente
    3. Envía al cliente llave pública efímera y firma
    4. Una vez que el cliente verificó: issuer, firma del certificado,
       obtuvo llave pública permanente del servidor y verificó firma de la llave efímera;
       entonces genera su llave efímera y la envía al servidor.
    5. Servidor recibe la llave pública efímera del cliente
    6. Servidor y CLiente generan secreto compartido
    7. Se derivan las llaves para obtener dos llaves simétricas 
    """
    # 1. Generar llave privada efímera del servidor
    llave_privada_efimera_servidor = utils.generar_llave_efimera()

    # 2. Generar llave pública efímera del servidor y se convierte a PEM
    llave_publica_efimera_servidor_bytes = (
        llave_privada_efimera_servidor.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )

    # 3. Firmar la llave pública efímera con la llave privada permanente del servidor
    firma = llave_privada_servidor.sign(
        llave_publica_efimera_servidor_bytes,
        ec.ECDSA(hashes.SHA256())
    )

    # 4. Envia al cliente la llave pública efímera junto con firma
    utils.enviar_bytes(cliente_sock, llave_publica_efimera_servidor_bytes)
    utils.enviar_bytes(cliente_sock, firma)

    # 5. Recibir llave pública efímera del cliente
    pub_cliente_bytes = utils.recibir_bytes(cliente_sock)
    llave_publica_efimera_cliente = serialization.load_pem_public_key(pub_cliente_bytes)

    # 6. Generar secreto compartido
    shared_key = llave_privada_efimera_servidor.exchange(ec.ECDH(), llave_publica_efimera_cliente)

    # 7. Derivar llaves cruzadas
    llave_a, llave_b = utils.derivar_llaves(shared_key)
    return llave_a, llave_b  # recibir, enviar


# --- FASE 3: AUTENTICACIÓN DEL CLIENTE (CAPA DE APLICACIÓN) -------------------------------------------    
def autenticar_usuario(cliente_sock, llave_sesion_recibir, llave_sesion_enviar, path_users):
    """
    Verifica usuario y hash SHA-512 desde el archivo usuarios.txt.
    Todo viaja cifrado.
    """
    try:
        credenciales = utils.descifrar( # Descifra las credenciales envíadas por el cliente
            llave_sesion_recibir,
            utils.leer_mensaje(cliente_sock) # Recibe [IV] [TIMESTAMP] [TAG] [TEXTO_CIFRADO]
        ).decode('utf-8')

        usuario, password = credenciales.split(':', 1)

        with open(path_users, "r", encoding="utf-8") as f:
            for linea in f:
                user, salt, hashp = linea.strip().split(':', 2)  # ahora son 3 campos user:salt:hash
                if usuario == user:
                    if utils.hashear_password(password, salt) == hashp: # genera hash del salt + contraseña y la comapra con el hash en usuarios.txr
                        utils.mandar_mensaje(
                            cliente_sock,
                            # envía OK con la llave envíar
                            utils.cifrar(llave_sesion_enviar, b"OK", int(time.time())) # time -> generar el timestamp
                        )
                        return True

                    # Si el usuario existe pero el password es incorrecto, se manda un mensaje de error
                    break

        #si no hay coincidencias en usuarios.txt
        utils.mandar_mensaje(
            cliente_sock,
            utils.cifrar(llave_sesion_enviar, b"ERROR", int(time.time()))
        )
        return False
    
    except Exception as e:
        print(f"Error autenticando: {e}")
        try:
            utils.mandar_mensaje(
                cliente_sock,
                utils.cifrar(llave_sesion_enviar, b"ERROR", int(time.time()))
            )
        except:
            pass #se cierra la conexion
        return False


# --- FASE 4 - FASE 5: OPERACIONES DE REPOSITORIO (CIFRADO DE FLUJO) y CIERRE -----------------------------------

def upload(cliente, path_directorio_archivos, llave_sesion_recibir, llave_sesion_enviar):
    """
    Procesa la subida de un archivo cifrado por segmentos.
        cliente: socket conectado al cliente
        path_directorio_archivos: carpeta donde se guardarán los archivos
        llave_sesion_recibir: llave AES efímera usada para descifrar mensajes que vienen de cliente
        llave_sesion_enviar: llave AES efímera usada para cifrar mensajes que servidor manda a cliente
    """
    nombre_archivo = utils.descifrar(
        llave_sesion_recibir,
        utils.leer_mensaje(cliente) # lee un mensaje completo y luego descifra y lo convierte con utf-8
    ).decode('utf-8')

    utils.mandar_mensaje(
        cliente,
        # Servidor responde al cliente que ya recibió el nombre del archivo
        utils.cifrar(llave_sesion_enviar, b"OK", int(time.time())) 
    )
    # contruye la ruta final /tmp/repo --> foto.jpg
    path_final = os.path.join(path_directorio_archivos, nombre_archivo) 

    with open(path_final, 'wb') as archivo: # se abre el archivo, si no existe lo crea, sino, sobreescribe
        print(f"Recibiendo archivo: {nombre_archivo}...")
        while True: # comienza a recibir segmentos
            paquete = utils.leer_mensaje(cliente) # recibe un paquete, seg1 - seg2 - seg3
            datos_plano = utils.descifrar(llave_sesion_recibir, paquete) # descifra el segmento, verifica tag, timestamp, AAD

            if datos_plano == b'FIN': # cuando servidor descifra obtiene un FIN
                break

            archivo.write(datos_plano) # si no era FIN, se agregan esos bytes al archivo
            #print(f"  Segmento recibido y descifrado: {len(datos_plano)} bytes")

    print(f"Transferencia de '{nombre_archivo}' finalizada y validada.")


def download(cliente, path_directorio_archivos, llave_sesion_enviar, llave_sesion_recibir):
    """
    Procesa la descarga cifrada hacia el cliente.
        cliente: socket conectado al cliente
        path_directorio_archivos: carpeta donde están guardados los archivos
        llave_sesion_enviar: llave AES efímera que servidor usa para enviar datos
        llave_sesion_recibir: llave AES efímera que servidor usa para descifrar datos recibidos
    """
    nombre_archivo = utils.descifrar( # descifra el paquete y lo convierte al archivo
        llave_sesion_recibir, 
        utils.leer_mensaje(cliente) # Servidor recibe paquete: [IV] [TIMESTAMP] [TAG] [TEXTO_CIFRADO]
    ).decode('utf-8')
    # Construye la ruta completa
    path_archivo = os.path.join(path_directorio_archivos, nombre_archivo)

    if not os.path.isfile(path_archivo): # Verifica si el archivo existe
        utils.mandar_mensaje(
            cliente,
            utils.cifrar(llave_sesion_enviar, b"ERROR", int(time.time())) # Si no existe envía ERROR (forma cifrada)
        )
        print(f"Archivo no encontrado: {nombre_archivo}")
        return

    utils.mandar_mensaje( # Si sí existe, envía OK
        cliente,
        utils.cifrar(llave_sesion_enviar, b"OK", int(time.time())) 
    )

    print(f"Iniciando descarga cifrada: {nombre_archivo}...")

    for pedazo in utils.crear_generador_lectura(path_archivo): # lee el archivo por pedazos [bloques de 4096 bytes]
        paquete_cifrado = utils.cifrar( # cifra cada bloque -> [IV][TIMESTAMP][TAG][BLOQUE_CIFRADO]
            llave_sesion_enviar,
            pedazo,
            int(time.time())
        )
        utils.mandar_mensaje(cliente, paquete_cifrado) # Se envía el bloque cifrado

    utils.mandar_mensaje( # Cuando ya no quedan bloques, FIN (lo manda cifrado)
        cliente,
        utils.cifrar(llave_sesion_enviar, b"FIN", int(time.time()))
    )

    print(f"Archivo '{nombre_archivo}' enviado correctamente.")


if __name__ == '__main__':
    all_args = argparse.ArgumentParser(description="Proyecto Final Criptografía — Servidor")
    all_args.add_argument("-p", "--puerto", required=True, help="Puerto donde escuchara el servidor")
    all_args.add_argument("--privada", required=True, help="Ruta de la llave privada permanente (.pem)")
    all_args.add_argument("-d", "--directorio", required=True, help="Ruta de la carpeta directorio")
    all_args.add_argument("--users", required=True, help="Ruta del archivo de usuarios.txt")

    args = all_args.parse_args()

    if not os.path.isdir(args.directorio):
        print(f"[!] El directorio no existe: {args.directorio}")
        sys.exit(1)

    puerto = args.puerto
    path_directorio_archivos = args.directorio
    path_llave_privada = args.privada
    path_users = args.users

    with open(path_llave_privada, "rb") as f:
        llave_priv_perm = serialization.load_pem_private_key(f.read(), password=None)

    servidor = crear_socket_servidor(puerto)
    print(f"Servidor listo en puerto {puerto}...")
    cliente = esperar_cliente(servidor)

    try:
        llave_sesion_recibir, llave_sesion_enviar = realizar_handshake(
            cliente,
            llave_priv_perm
        )
        print("Sesión segura establecida.")

        if autenticar_usuario(cliente, llave_sesion_recibir, llave_sesion_enviar, path_users):
            print("Cliente autenticado. Esperando operaciones...")

            operacion = utils.leer_mensaje(cliente).decode('utf-8')

            if operacion == 'upload':
                utils.mandar_mensaje(cliente, b'OK')
                upload(cliente, path_directorio_archivos, llave_sesion_recibir, llave_sesion_enviar)

            elif operacion == 'download':
                utils.mandar_mensaje(cliente, b'OK')
                download(cliente, path_directorio_archivos, llave_sesion_enviar, llave_sesion_recibir)

            else:
                utils.mandar_mensaje(cliente, b'ERROR')
                print("Operación no soportada")

        else:
            print("Fallo de autenticación.")
            cliente.close()

    except Exception as e:
        print(f"Error durante la conexión: {e}")
        cliente.close()

    #print(f"Llave de sesión envíar del servidor:{llave_sesion_enviar.hex()}")
    #print(f"Llave de sesión recibir del servidor:{llave_sesion_recibir.hex()}")

    cliente.close()
    servidor.close()
