#!/usr/bin/env python3

import sys


def cesar(archivo, accion, llave):
    with open(archivo, "r") as f:
        d = f.read()
        resultado = []

        # with open(archivo + "result", "w") as f:
        for i in d:
            if i.isalpha():
                if accion == "d":
                    if i.isupper():
                        resultado.append(chr((ord(i) - int(llave) - 65) % 26 + 65))
                    else:
                        resultado.append(chr((ord(i) - int(llave) - 97) % 26 + 97))
                elif accion == "c":
                    if i.isupper():
                        resultado.append(chr((ord(i) + int(llave) - 65) % 26 + 65))
                    else:
                        resultado.append(chr((ord(i) + int(llave) - 97) % 26 + 97))
                else:
                    print("Operacion no permitida")
                    exit(1)
            else:
                resultado.append(i)
        with open(archivo + "result", "w") as f:
            f.write("".join(resultado))


if __name__ == "__main__":
    archivo = sys.argv[1]
    accion = sys.argv[2]
    shift = int(sys.argv[3])

    cesar(archivo, accion, shift)
