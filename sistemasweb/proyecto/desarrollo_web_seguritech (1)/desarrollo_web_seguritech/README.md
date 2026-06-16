# SeguriTech - Desarrollo Web

Proyecto universitario: Catálogo de servicios tecnológicos con Node.js + Express + EJS + MySQL.

## Instalación

```bash
# 1. Instalar dependencias
npm install

# 2. Configurar base de datos
cp .env.example .env
# Editar .env y poner tu contraseña de MySQL en DB_PASS

# 3. Crear base de datos
mysql -u root -p < bd.sql

# 4. Iniciar servidor
node index.js

# 5. Abrir en navegador
# PC:     http://localhost:3000
# Celular (misma red WiFi): http://IP_DEL_PC:3000
```

## Para ver desde el celular

1. PC y celular en la **misma red WiFi**
2. Obtener IP del PC: `ip addr` (Linux) o `ipconfig` (Windows)
3. En el celular abrir: `http://192.168.x.x:3000`

## Estructura

```
desarrollo_web_seguritech/
├── controllers/     # Lógica de negocio
├── models/          # Acceso a MySQL (consultas parametrizadas)
├── routes/          # Rutas web y API
├── views/           # Plantillas EJS
├── public/          # CSS, JS, uploads
├── middleware/      # Multer (subida de archivos)
├── bd.sql           # Script de base de datos
├── index.js         # Servidor Express
└── .env             # Variables de entorno
```

## Seguridad

- Consultas parametrizadas (anti SQL Injection)
- Escape automático en EJS (anti XSS)
- Validación en cliente (JS) y servidor (Node.js)
- Validación de archivos (extensión, MIME, tamaño 5MB)
- Variables de entorno (.env)

## Funcionalidades

- Catálogo de 10 servicios desde BD
- Formulario de cotización con archivo adjunto
- Dashboard con estadísticas vía AJAX/fetch
- Diseño responsive (funciona en celular)
