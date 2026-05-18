#!/usr/bin/env python3

# Generar las llaves publica y privada permanentes
def generar_llaves():

def recibir_segmentos():
    #Recibe los segmentos de la llave privada local del ransomware

def descifrar_segmentos():
    #Descifra cada segmento de la llave privada local

def unir_segmentos():
    #Une los segmentos de la llave privada local

def enviar_llave_privada(ip_destino, puerto):
    #Envia la llave privada local al ransomware

def recuperar():
    """
    1. recibe los segmentos - llama a la funcion de recibir segmentos
    2. descifra los segmentos - llama a la funcion de descifrar segmentos
    3. une los segmentos - llama a la funcion de unir segmentos
    4. envia la llave privada completa y descifrada - llama a la funcion de enviar llave privada

    - Puede llamar a mas funciones como de creacion de sockets por ejemplo.
    """

if __name__ == "__main__":
    """pasar argumentos
    1. puerto: puerto donde funcionara el socket para recibir los segmentos y enviar la llave privada
    2. llave_privada_permanente: ubicacion exacta de la llave privada que descifrara 
    
    - modos de uso:
        1. --generar-llaves (genera las llaves permanentes, guarda en un archivo la llave privada e imprime la llave publica para que sea copiada y pegada en el script del ransomware) - Llama a la funcion de generar llaves
        2. --escuchar (para escuchar mediante sockets, recibir los segmentos, descifrarlos, unirlos y enviarlos al ransomware) - llama a la funcion de recuperacion 
    """
