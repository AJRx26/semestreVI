def cifrado(cadena):
    alfabeto = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    cadena2 = ''
    for i in (cadena):
        if i == ' ' :
            cadena2 += ' '
        elif i in alfabeto:
            x = int((alfabeto.index(i) + cambio) % 26)
            cadena2 += alfabeto[x]
    return cadena2

if __name__ == '__main__':
    cambio = int(input())
    if cambio >= 0:
        cadena = str(input())
        cadena2 = cifrado(cadena)
        print(cadena2)
    else:
        exit