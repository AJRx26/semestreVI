#!/usr/bin/env python3

import os
import base64

size_key = int(input("Tamaño llave: "))
size_iv = int(input("Tamaño IV: "))
iv = os.urandom(size_iv)
llave = os.urandom(size_key)
print("Llave: ",base64.b64encode(llave).decode())
print("IV: ",base64.b64encode(iv).decode())
