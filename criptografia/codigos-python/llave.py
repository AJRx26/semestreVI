#!/usr/bin/env python3

import os
import base64

llave = os.urandom(16)
print(base64.b64encode(llave).decode())
