def cifrado_cesar(alfabeto, shift, texto):
    texto_cifrado = ""
    for letra in texto:
        if letra in alfabeto:
            indice_actual = alfabeto.index(letra)
            indice_cesar = indice_actual + shift
            if indice_cesar > 25:
                indice_cesar -= 26
            texto_cifrado += alfabeto[indice_cesar]
        else:
            texto_cifrado += letra
    return texto_cifrado

if __name__ == '__main__':
    alfabeto=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    shift = int(input())
    frase = input()
    frase_cifrada=cifrado_cesar(alfabeto,shift,frase)
    print(frase_cifrada)
