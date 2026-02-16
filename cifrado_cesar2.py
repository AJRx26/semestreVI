#!/usr/bin/env python3

import sys


def cesar(archivo, accion, llave):
    """
    Funcion que cifra y descrifa el contenido de un archivo
    archivo: str
    accion: str
    llave: int

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

        # with open(archivo + "result", "w") as f:
        for i in d:
            if i.isalpha():
                if accion == "d":
                    if i.isupper():
                        x = int((alfabeto_mayus.index(i) - llave) % 26)
                        resultado += alfabeto_mayus[x]
                    else:
                        x = int((alfabeto_minus.index(i) - llave) % 26)
                        resultado += alfabeto_minus[x]
                elif accion == "c":
                    if i.isupper():
                        x = int((alfabeto_mayus.index(i) + llave) % 26)
                        resultado += alfabeto_mayus[x]
                    else:
                        x = int((alfabeto_minus.index(i) + llave) % 26)
                        resultado += alfabeto_minus[x]
                else:
                    print("Operacion no permitida")
                    print("Use <c> (cifrado) o <d> (descifrado)")
                    print("'archivo' 'accion' 'shift'")
                    exit(1)
            else:
                resultado.append(i)
        with open(archivo + "result", "w") as f:
            f.write("".join(resultado))


if __name__ == "__main__":
    archivo = sys.argv[1]
    accion = sys.argv[2]
    shift = int(sys.argv[3])

    if shift > 0:
        cesar(archivo, accion, shift)
    elif shift == 0:
        print("Debe de ingresar un numero mayor a 0")
        exit(1)
