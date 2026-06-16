-- SEGURITECH - Base de Datos MySQL
DROP DATABASE IF EXISTS seguritech_db;
CREATE DATABASE seguritech_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE seguritech_db;

CREATE TABLE categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE servicios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    imagen VARCHAR(100) NOT NULL,
    categoria_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE solicitudes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    servicio_id INT NOT NULL,
    archivo VARCHAR(255),
    mensaje TEXT NOT NULL,
    estado ENUM('pendiente','en_proceso','completada','cancelada') DEFAULT 'pendiente',
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (servicio_id) REFERENCES servicios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO categorias (nombre, descripcion) VALUES
('Redes de Cómputo', 'Servicios de infraestructura de redes'),
('Ciberseguridad', 'Seguridad informática y auditorías'),
('Desarrollo de Software', 'Soluciones de software personalizadas'),
('Capacitación', 'Entrenamiento en tecnología');

INSERT INTO servicios (nombre, descripcion, imagen, categoria_id) VALUES
('Implementación de Redes de Cómputo', 'Diseño, instalación y configuración de infraestructura de redes cableadas e inalámbricas.', 'images.jpg', 1),
('Mantenimiento de Redes de Cómputo', 'Mantenimiento preventivo y correctivo para garantizar el óptimo funcionamiento de su red.', 'images1.jpg', 1),
('Implementación de Seguridad en Redes', 'Protección integral con firewalls, IDS/IPS y segmentación de red.', 'images2.jpg', 2),
('Automatización de Redes', 'Automatización de tareas mediante scripts y herramientas como Ansible.', 'images3.jpg', 1),
('Desarrollo de Software de Ciberseguridad', 'Creación de herramientas personalizadas: scanners, dashboards, etc.', 'images4.jpg', 3),
('Auditorías de Ciberseguridad', 'Evaluación de postura de seguridad: políticas, controles, cumplimiento normativo.', 'images5.jpg', 2),
('Pentesting', 'Pruebas de penetración éticas para identificar vulnerabilidades.', 'images6.jpg', 2),
('Administración de Servidores', 'Gestión de servidores Windows y Linux: instalación, monitoreo, backups.', 'images7.jpg', 1),
('Configuración de Firewalls', 'Implementación y hardening de firewalls de nueva generación.', 'images8.jpg', 2),
('Capacitación de Ciberseguridad', 'Programas de entrenamiento: concientización, certificaciones, talleres.', 'images9.jpg', 4);

INSERT INTO solicitudes (nombre, email, telefono, servicio_id, archivo, mensaje, estado) VALUES
('Juan Pérez', 'juan@email.com', '555-0101', 1, 'doc1.pdf', 'Cotización red 50 usuarios', 'pendiente'),
('María García', 'maria@email.com', '555-0102', 7, 'doc2.pdf', 'Pentesting app web', 'en_proceso'),
('Carlos López', 'carlos@email.com', '555-0103', 3, 'doc3.pdf', 'Seguridad en red actual', 'pendiente'),
('Ana Martínez', 'ana@email.com', '555-0104', 5, 'doc4.pdf', 'Herramienta monitoreo', 'en_proceso'),
('Luis Rodríguez', 'luis@email.com', '555-0105', 7, 'doc5.pdf', 'Pentesting infraestructura', 'completada'),
('Sofía Hernández', 'sofia@email.com', '555-0106', 2, 'doc6.pdf', 'Mantenimiento mensual', 'pendiente'),
('Diego Torres', 'diego@email.com', '555-0107', 9, 'doc7.pdf', 'Configuración firewall', 'en_proceso'),
('Laura Díaz', 'laura@email.com', '555-0108', 6, 'doc8.pdf', 'Auditoría ISO 27001', 'pendiente'),
('Pedro Sánchez', 'pedro@email.com', '555-0109', 10, 'doc9.pdf', 'Capacitación 15 personas', 'completada'),
('Carmen Ruiz', 'carmen@email.com', '555-0110', 4, 'doc10.pdf', 'Automatización switches', 'pendiente'),
('Roberto Vega', 'roberto@email.com', '555-0111', 8, 'doc11.pdf', 'Admin servidores Linux', 'en_proceso'),
('Patricia Morales', 'patricia@email.com', '555-0112', 7, 'doc12.pdf', 'Pentesting app móvil', 'pendiente'),
('Fernando Castillo', 'fernando@email.com', '555-0113', 1, 'doc13.pdf', 'Red nueva sucursal', 'completada'),
('Gabriela Flores', 'gabriela@email.com', '555-0114', 3, 'doc14.pdf', 'Seguridad data center', 'pendiente'),
('Andrés Mendoza', 'andres@email.com', '555-0115', 6, 'doc15.pdf', 'Auditoría completa', 'en_proceso');
