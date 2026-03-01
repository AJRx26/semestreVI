import string 

def cifrado_cesar(alfabeto, n, texto):
    texto_cifrado = ""
    for letra in texto:
        if letra in alfabeto:
            x = int((alfabeto.index(letra) + n) % 26)
            texto_cifrado += alfabeto[x]
        else:
            texto_cifrado += letra
    return texto_cifrado

if __name__ == '__main__':
    alfabeto=list(string.ascii_lowercase)
    n = int(input())
    frase = input()
    frase_cifrada=cifrado_cesar(alfabeto,n,frase)
    print(frase_cifrada)

