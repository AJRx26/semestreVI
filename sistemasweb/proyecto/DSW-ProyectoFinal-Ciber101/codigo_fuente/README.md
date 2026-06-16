# SeguriTech - Desarrollo Web

Proyecto universitario: Catálogo de servicios tecnológicos con Node.js + Express + EJS + MySQL.

## Requisitos previos
- Node.js
- npm
- MySQL

## Instalación
```b
# 1. Instalar dependencias en la carpeta del proyecto, ya que usa el archivo package.json
npm install
```

# 2. Crear y configurar base de datos con su usuario
mysql -u root -p
CREATE DATABASE seguritech_db;
exit;

# 2.1. Usuario de base de datos
Por seguridad, se recomienda utilizar un usuario exclusivo para la aplicación en lugar del usuario administrador `root`.

## Crear usuario MySQL

mysql -u root -p

CREATE USER 'seguritech_user'@'localhost' IDENTIFIED BY 'password_seguro';

GRANT SELECT, INSERT, UPDATE, DELETE ON seguritech_db.* TO 'seguritech_user'@'localhost';

FLUSH PRIVILEGES;

# 2.2. Editar .env y poner tu password de MySQL en DB_PASS
cp .env.example .env

DB_HOST=localhost
DB_USER=tu_usuario
DB_PASS=tu_password
DB_NAME=seguritech_db
DB_PORT=3306
MAX_FILE_SIZE=5242880

# 2.3. Importar la base de datos
mysql -u seguritech_user -p seguritech_db < bd.sql

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

## Arquitectura y Estructura
El sistema está desarrollado utilizando el patrón MVC:

- Model: gestión de datos y consultas MySQL
- View: interfaces creadas con EJS
- Controller: procesamiento de solicitudes y lógica del sistema
```
desarrollo_web_seguritech/
|-controllers/     # Manejo de solicitudes y comunicación entre vistas/modelos
|-models/          # Acceso y operaciones con la base de datos
|-routes/          # Definición de endpoints HTTP
|-views/           # Interfaces EJS del sistema
|-public/          # Recursos estáticos (CSS, JS, archivos)
|-middleware/      # Procesamiento adicional (subida de archivos)
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
