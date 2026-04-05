"""
=============================================================================
  DEMOSTRACIÓN: Ataque de Texto Cifrado Escogido (CCA) sobre RSA sin padding
  Basado en la propiedad homomórfica multiplicativa de RSA textbook
=============================================================================

  FLUJO DEL ATAQUE:
  1. El atacante intercepta c0 = m^e mod n
  2. El atacante elige r=2, calcula cr = r^e mod n (usando llave pública)
  3. El atacante construye c1 = c0 * cr mod n  → descifra como m*r
  4. La víctima descifra c1 (ingeniería social) y devuelve m*r
  5. El atacante recupera m = (m*r) * r^{-1} mod n

  NOTA: Este código es para fines educativos. RSA sin padding (textbook RSA)
        es inseguro. En producción siempre se usa RSA-OAEP o RSA-PSS.
=============================================================================
"""

import gmpy2
import os
import sys
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# ─────────────────────────────────────────────────────
#  Funciones reutilizadas de rsaManual.py
# ─────────────────────────────────────────────────────

def simple_rsa_encrypt(m, publickey):
    numbers = publickey.public_numbers()
    return gmpy2.powmod(m, numbers.e, numbers.n)

def simple_rsa_decrypt(c, privatekey):
    numbers = privatekey.private_numbers()
    return gmpy2.powmod(c, numbers.d, numbers.public_numbers.n)

def int_to_bytes(i):
    i = int(i)
    return i.to_bytes((i.bit_length() + 7) // 8, byteorder='big')

def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')

def leer_bytes(ruta):
    with open(ruta, 'rb') as f:
        return f.read()

def escribir_bytes(ruta, datos):
    with open(ruta, 'wb') as f:
        f.write(datos)

def desserializar_privada(ruta):
    with open(ruta, 'rb') as f:
        return serialization.load_pem_private_key(f.read(), backend=default_backend(), password=None)

def desserializar_publica(ruta):
    with open(ruta, 'rb') as f:
        return serialization.load_pem_public_key(f.read(), backend=default_backend())

# ─────────────────────────────────────────────────────
#  Utilidades de visualización
# ─────────────────────────────────────────────────────

LINE = "─" * 70
DLINE = "═" * 70

def titulo(texto):
    print(f"\n{DLINE}")
    print(f"  {texto}")
    print(DLINE)

def paso(num, texto):
    print(f"\n{'─'*70}")
    print(f"  PASO {num}: {texto}")
    print(f"{'─'*70}")

def info(etiqueta, valor, truncar=64):
    if isinstance(valor, (bytes, bytearray)):
        hex_val = valor.hex()
        mostrar = hex_val[:truncar] + ("..." if len(hex_val) > truncar else "")
        print(f"  {etiqueta}: {mostrar}")
    elif isinstance(valor, (int, gmpy2.mpz)):
        s = str(valor)
        mostrar = s[:truncar] + ("..." if len(s) > truncar else "")
        print(f"  {etiqueta}: {mostrar}")
    else:
        print(f"  {etiqueta}: {valor}")

def exito(texto):
    print(f"\n  ✓ {texto}")

def advertencia(texto):
    print(f"\n  ⚠  {texto}")


# ─────────────────────────────────────────────────────
#  ATAQUE CCA sobre RSA
# ─────────────────────────────────────────────────────

def atacante_multiplica_cifrados(ruta_c0, ruta_cr, ruta_salida, n):
    """
    Paso 3 del ataque: c1 = c0 * cr mod n
    Opera directamente sobre los archivos binarios de los textos cifrados.
    No necesita la llave privada.
    """
    # Leer los dos cifrados como enteros
    c0 = bytes_to_int(leer_bytes(ruta_c0))
    cr = bytes_to_int(leer_bytes(ruta_cr))

    # Multiplicación homomórfica: (m*r)^e mod n = m^e * r^e mod n
    c1 = (c0 * cr) % n

    # Guardar c1 como archivo binario
    escribir_bytes(ruta_salida, int_to_bytes(c1))
    return c0, cr, c1


def victima_descifra(ruta_cifrado, ruta_salida, llave_privada):
    """
    Simula a la víctima descifrando con su llave privada.
    En el escenario real, la víctima recibe c1 pensando que es legítimo.
    """
    cifrado_bytes = leer_bytes(ruta_cifrado)
    c = bytes_to_int(cifrado_bytes)
    m_resultado = simple_rsa_decrypt(c, llave_privada)
    resultado_bytes = int_to_bytes(m_resultado)
    escribir_bytes(ruta_salida, resultado_bytes)
    return m_resultado, resultado_bytes


def atacante_recupera_m(mr, r, n):
    """
    Paso 5: m = (m*r) * r^{-1} mod n
    El inverso modular se calcula con el algoritmo extendido de Euclides.
    No se necesita la llave privada en ningún momento.
    """
    r_inv = gmpy2.powmod(r, -1, n)   # r^{-1} mod n
    m_recuperado = (mr * r_inv) % n
    return m_recuperado, r_inv


# ─────────────────────────────────────────────────────
#  PROGRAMA PRINCIPAL
# ─────────────────────────────────────────────────────

def main():
    titulo("ATAQUE CCA — RSA SIN PADDING (TEXTBOOK RSA)")
    print("""
  Este script demuestra cómo un atacante puede recuperar el mensaje
  original m sin tener la llave privada, aprovechando la propiedad
  homomórfica multiplicativa de RSA y engañando a la víctima para
  que descifre un mensaje manipulado.
    """)

    # Rutas de archivos
    LLAVE_PUBLICA  = "llave_publica.pem"
    LLAVE_PRIVADA  = "llave_privada.pem"
    MENSAJE_ORIG   = "mensaje_original.txt"
    C0_BIN         = "mensaje_cifrado.bin"       # interceptado por atacante
    CR_BIN         = "cifrado_r.bin"             # atacante cifra r
    C1_BIN         = "mensaje_manipulado.bin"    # c0 * cr mod n
    MR_BIN         = "descifrado_victima.bin"    # víctima descifra c1
    M_RECUPERADO   = "mensaje_recuperado.txt"    # resultado del ataque

    # Verificar que existan los archivos necesarios
    for ruta in [LLAVE_PUBLICA, LLAVE_PRIVADA, MENSAJE_ORIG, C0_BIN]:
        if not os.path.exists(ruta):
            print(f"\n  ERROR: No se encontró '{ruta}'")
            print("  Ejecuta primero: python3 generarLlaves.py y cifra el mensaje.")
            sys.exit(1)

    # Cargar llaves
    llave_publica  = desserializar_publica(LLAVE_PUBLICA)
    llave_privada  = desserializar_privada(LLAVE_PRIVADA)
    numeros_pub    = llave_publica.public_numbers()
    n, e           = numeros_pub.n, numeros_pub.e

    # ──────────────────────────────────────────────
    paso(1, "ATACANTE intercepta el texto cifrado c0")
    # ──────────────────────────────────────────────

    c0_bytes = leer_bytes(C0_BIN)
    c0       = bytes_to_int(c0_bytes)

    print(f"\n  Archivo interceptado : {C0_BIN}  ({len(c0_bytes)} bytes)")
    info("c0 (hex, primeros 32B)", c0_bytes[:32])
    info("c0 (entero)", c0)
    advertencia("El atacante NO puede descifrar c0 directamente (no tiene 'd')")

    # ──────────────────────────────────────────────
    paso(2, "ATACANTE elige r=2 y lo cifra con la llave pública")
    # ──────────────────────────────────────────────

    r  = gmpy2.mpz(2)
    cr = simple_rsa_encrypt(r, llave_publica)   # cr = 2^e mod n
    escribir_bytes(CR_BIN, int_to_bytes(cr))

    print(f"\n  Factor elegido r     : {r}")
    print(f"  Llave pública (e)    : {e}")
    info("n (módulo RSA)", n)
    info("cr = r^e mod n", cr)
    print(f"\n  Fórmula: cr = {r}^e mod n  (usando sólo la llave PÚBLICA)")
    exito(f"cr guardado en: {CR_BIN}")

    # ──────────────────────────────────────────────
    paso(3, "ATACANTE construye c1 = c0 × cr mod n  (multiplicación homomórfica)")
    # ──────────────────────────────────────────────

    c0_val, cr_val, c1 = atacante_multiplica_cifrados(C0_BIN, CR_BIN, C1_BIN, n)

    print(f"""
  Propiedad homomórfica de RSA:
  ┌─────────────────────────────────────────────────────────────────┐
  │  c0 = m^e mod n                                                 │
  │  cr = r^e mod n                                                 │
  │  c1 = c0 × cr mod n = m^e × r^e mod n = (m×r)^e mod n         │
  │                                                                  │
  │  Al descifrar c1: c1^d = [(m×r)^e]^d = m×r  (Teorema de Euler) │
  └─────────────────────────────────────────────────────────────────┘
    """)
    info("c1 = c0*cr mod n", c1)
    exito(f"c1 guardado en: {C1_BIN}  — El atacante envía este archivo a la víctima")

    # ──────────────────────────────────────────────
    paso(4, "VÍCTIMA descifra c1 con su llave privada (ingeniería social)")
    # ──────────────────────────────────────────────

    mr_entero, mr_bytes = victima_descifra(C1_BIN, MR_BIN, llave_privada)

    print(f"\n  La víctima recibe '{C1_BIN}' y descifra con su llave privada d.")
    try:
        texto_victima = mr_bytes.decode('utf-8', errors='replace')
        print(f"\n  Resultado que ve la víctima (texto):")
        print(f"  ┌{'─'*60}┐")
        # Mostrar máximo 3 líneas del resultado
        for linea in repr(texto_victima[:120]).__str__().splitlines()[:3]:
            print(f"  │  {linea:<58}│")
        print(f"  └{'─'*60}┘")
    except Exception:
        pass

    info("m×r (entero)", mr_entero)
    advertencia("La víctima obtiene 'm×r' — parece basura — y lo descarta.")
    exito(f"Atacante recibe m×r guardado en: {MR_BIN}")

    # ──────────────────────────────────────────────
    paso(5, "ATACANTE recupera m = (m×r) × r⁻¹ mod n  (sin llave privada)")
    # ──────────────────────────────────────────────

    m_recuperado, r_inv = atacante_recupera_m(mr_entero, r, n)

    print(f"""
  Aritmética modular:
  ┌─────────────────────────────────────────────────────────────────┐
  │  Conocido: m×r (recibido de la víctima)                         │
  │  Conocido: r = {r}  (lo eligió el atacante)                       │
  │                                                                  │
  │  r⁻¹ = inverso modular de r  →  r × r⁻¹ ≡ 1 (mod n)           │
  │  m  = (m×r) × r⁻¹ mod n                                         │
  │  ≡ m × (r × r⁻¹) mod n  =  m × 1 mod n  =  m                  │
  └─────────────────────────────────────────────────────────────────┘
    """)

    info("r⁻¹ mod n (inverso modular)", r_inv)
    info("m recuperado (entero)", m_recuperado)

    # Convertir a bytes y guardar
    m_bytes = int_to_bytes(m_recuperado)
    escribir_bytes(M_RECUPERADO, m_bytes)

    # ──────────────────────────────────────────────
    titulo("RESULTADO FINAL — VERIFICACIÓN DEL ATAQUE")
    # ──────────────────────────────────────────────

    texto_original   = leer_bytes(MENSAJE_ORIG)
    texto_recuperado = leer_bytes(M_RECUPERADO)

    print(f"\n  Mensaje original  : {texto_original.decode('utf-8', errors='replace')}")
    print(f"  Mensaje recuperado: {texto_recuperado.decode('utf-8', errors='replace')}")
    print()

    if texto_original == texto_recuperado:
        print("  " + "★" * 68)
        print("  ★  ATAQUE EXITOSO: el mensaje original fue recuperado           ★")
        print("  ★  sin usar la llave privada directamente.                      ★")
        print("  " + "★" * 68)
    else:
        # Verificar como enteros (puede haber diferencia de bytes leading)
        orig_int = bytes_to_int(texto_original)
        rec_int  = int(m_recuperado)
        if orig_int == rec_int:
            print("  ✓  ATAQUE EXITOSO (valores enteros idénticos)")
        else:
            print("  ✗  Algo falló — verifica los archivos de entrada")

    print(f"""
  Archivos generados:
  ├── {MENSAJE_ORIG:<35} ← mensaje original
  ├── {C0_BIN:<35} ← cifrado interceptado por el atacante
  ├── {CR_BIN:<35} ← atacante cifra r=2 con llave pública
  ├── {C1_BIN:<35} ← c0*cr mod n (enviado a la víctima)
  ├── {MR_BIN:<35} ← la víctima descifra y devuelve m*r
  └── {M_RECUPERADO:<35} ← m recuperado por el atacante ✓

  CONCLUSIÓN:
  RSA sin padding (textbook) es vulnerable al ataque CCA porque su
  propiedad homomórfica permite manipular cifrados sin conocer la
  llave privada. La solución es usar RSA-OAEP (padding aleatorio),
  que destruye esta propiedad homomórfica.
    """)


if __name__ == '__main__':
    main()
