#!/usr/bin/env python3

import sys


def ayuda():
    mensaje = """
    Uso: cifrado_cesar2 <archivo> <accion> <shift> <destino>

    Cifra y descifra el contenido de un archivo usando el cifrado Cesar.

    Argumentos:
        archivo: Nombre del archivo a cifrar o descifrar
        accion: c para cifrar y d para descifrar
        shift: Numero de recorrimeinto
        destino: Nombre del archivo final

    cifrado_cesar2 prueba.txt -c 3 resultado.txt
    cifrado_cesar2 prueba.txt -d 3 resultado.txt
    """
    print(mensaje)
    exit(0)


def cesar(archivo, accion, llave, destino):
    """
    Funcion que cifra y descrifa el contenido de un archivo
    archivo: str
    accion: str
    llave: int
    destino: str

    return: str
    """
    with open(archivo, "r") as f:
        d = f.read()

        alfabeto_minus = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "ñ",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
        ]
        alfabeto_mayus = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "Ñ",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]

        resultado = []

        for i in d:
            if i.isalpha():
                if accion == "-d":
                    if i.isupper():
                        x = int((alafabeto_mayus.index(i) - llave) % 26)
                        resultado += alfabeto_mayus[x]
                    else:
                        x = int((alfabeto_minus.index(i) - llave) % 26)
                        resultado += alfabeto_minus[x]
                elif accion == "-c":
                    if i.isupper():
                        x = int((alfabeto_mayus.index(i) + llave) % 26)
                        resultado += alfabeto_mayus[x]
                    else:
                        x = int((alfabeto_minus.index(i) + llave) % 26)
                        resultado += alfabeto_minus[x]
                else:
                    print("Operacion no permitida")
                    ayuda()
                    exit(1)
            else:
                resultado.append(i)

        with open(destino, "w") as f:
            f.write("".join(resultado))


if __name__ == "__main__":
    archivo = sys.argv[1]
    accion = sys.argv[2]
    shift = int(sys.argv[3])
    destino = sys.argv[4]

    """
    if archivo == "-h" or "--help":
        ayuda()
    """

    if shift > 0:
        cesar(archivo, accion, shift, destino)
    else:
        ayuda()
