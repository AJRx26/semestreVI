Proyecto 1:

Hacer implementación manual de AES CBC:

- Usar modo ECB como base para el cifrado por bloque
- Usar el padding visto clase (no es seguro pero es lo que tenemos)
- Generar un IV aleatorio al cifrar, este se pega al inicio o final
  del archivo, al descifrar se toma en cuenta
- Hacer comprobación de integridad (pegar hash al final del cifrado,
  comprobar hash al descifrar)
- La solución debe recibir 3 parámetros:
  - Archivo de entrada
  - Archivo de salida
  - Llave (base 64)
