#!/bin/bash
# generar_cert_tls.sh
# Genera un certificado autofirmado EC (P-384) para desarrollo local.
# En producción se usaría un certificado de una CA real (ej. Let's Encrypt).

openssl req -x509 \
  -newkey ec \
  -pkeyopt ec_paramgen_curve:P-384 \
  -keyout domain_key.pem \
  -out domain_cert.crt \
  -days 365 \
  -nodes \
  -subj "/CN=localhost/O=SeguriTech/C=MX"

echo ""
echo "Archivos generados:"
echo "  domain_cert.crt  → certificado (compartir con el cliente)"
echo "  domain_key.pem   → llave privada (solo el servidor)"
