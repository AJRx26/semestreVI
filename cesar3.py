def cifrado_cesar(alfabeto, shift, texto):
    if shift < 0:
        exit()
    texto_cifrado = ""
    for letra in texto:
        if letra in alfabeto:
            x = int((alfabeto.index(letra) + shift) % 26)
            texto_cifrado += alfabeto[x]
        else:
            texto_cifrado += letra
    return texto_cifrado

if __name__ == '__main__':
    alfabeto=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    shift = int(input())
    frase = input()
    frase_cifrada=cifrado_cesar(alfabeto,shift,frase)
    print(frase_cifrada)