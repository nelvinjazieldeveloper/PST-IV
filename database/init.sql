-- ==============================================================================
-- BASE DE DATOS VENVIDRIO - ZONA CALIENTE (PRODUCCIÓN E INSPECCIÓN)
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS venvidrio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE venvidrio;

-- 1. TABLAS MAESTRAS E INDEPENDIENTES
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    clave VARCHAR(255) NOT NULL,
    cargo VARCHAR(100),
    rol VARCHAR(50),
    estado ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS turnos (
    id_turno INT AUTO_INCREMENT PRIMARY KEY,
    codigo_turno VARCHAR(20) NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    descripcion VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS maquinas (
    id_maquina INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(150),
    cantidad_secciones INT,
    estado ENUM('ACTIVA','INACTIVA','MANTENIMIENTO') DEFAULT 'ACTIVA'
);

CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo_producto VARCHAR(50) UNIQUE NOT NULL,
    nombre_producto VARCHAR(150) NOT NULL,
    capacidad_ml DECIMAL(10,2),
    peso_teorico DECIMAL(10,2),
    cliente VARCHAR(150),
    estado ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS moldes (
    id_molde INT AUTO_INCREMENT PRIMARY KEY,
    codigo_molde VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(150),
    fecha_instalacion DATE,
    estado ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS premoldes (
    id_premolde INT AUTO_INCREMENT PRIMARY KEY,
    codigo_premolde VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(150),
    fecha_instalacion DATE,
    estado ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS defectos (
    id_defecto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    categoria VARCHAR(100),
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS catalogo_defectos (
    id_defecto INT AUTO_INCREMENT PRIMARY KEY,
    codigo_defecto VARCHAR(20),
    nombre VARCHAR(150) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    descripcion TEXT,
    criticidad ENUM('CRITICO','MAYOR','MENOR') NOT NULL,
    estado ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tipos_paradas (
    id_tipo_parada INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS inspectores (
    id_inspector INT AUTO_INCREMENT PRIMARY KEY,
    cedula VARCHAR(20) UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    cargo VARCHAR(100),
    telefono VARCHAR(20),
    correo VARCHAR(100),
    estado ENUM('ACTIVO','INACTIVO') DEFAULT 'ACTIVO',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metas_produccion (
    id_meta INT AUTO_INCREMENT PRIMARY KEY,
    fecha_inicio DATE,
    fecha_fin DATE,
    meta_eee DECIMAL(6,2),
    meta_empaque DECIMAL(6,2),
    meta_formacion DECIMAL(6,2),
    meta_produccion DECIMAL(12,2)
);

CREATE TABLE IF NOT EXISTS reportes_generados (
    id_reporte INT AUTO_INCREMENT PRIMARY KEY,
    fecha_generacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    tipo_reporte VARCHAR(100),
    fecha_inicio DATE,
    fecha_fin DATE,
    generado_por INT,
    ruta_archivo VARCHAR(255),
    FOREIGN KEY (generado_por) REFERENCES usuarios(id_usuario)
);

-- 2. TABLAS DE PRIMER NIVEL DE DEPENDENCIA
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS secciones (
    id_seccion INT AUTO_INCREMENT PRIMARY KEY,
    id_maquina INT NOT NULL,
    numero_seccion INT NOT NULL,
    estado ENUM('ACTIVA','INACTIVA') DEFAULT 'ACTIVA',
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina) ON DELETE CASCADE
);

-- 3. TABLAS TRANSACCIONALES PRINCIPALES
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS produccion (
    id_produccion INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_turno INT NOT NULL,
    id_maquina INT NOT NULL,
    id_producto INT NOT NULL,
    id_usuario INT NOT NULL,
    paletas_producidas DECIMAL(12,2),
    gruesas_producidas DECIMAL(12,2),
    gruesas_empacadas DECIMAL(12,2),
    gruesas_retenidas DECIMAL(12,2),
    observaciones TEXT,
    FOREIGN KEY (id_turno) REFERENCES turnos(id_turno),
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS inspecciones (
    id_inspeccion INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    id_turno INT NOT NULL,
    id_inspector INT NOT NULL,
    id_maquina INT NOT NULL,
    id_seccion INT NOT NULL,
    id_producto INT NOT NULL,
    lote VARCHAR(50),
    temperatura_maquina DECIMAL(10,2),
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_turno) REFERENCES turnos(id_turno),
    FOREIGN KEY (id_inspector) REFERENCES inspectores(id_inspector),
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- 4. TABLAS DE DETALLE Y DEPENDENCIAS SECUNDARIAS (PRODUCCIÓN)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS indicadores_eficiencia (
    id_indicador INT AUTO_INCREMENT PRIMARY KEY,
    id_produccion INT NOT NULL,
    porcentaje_formacion DECIMAL(6,2),
    porcentaje_empaque DECIMAL(6,2),
    porcentaje_retenido DECIMAL(6,2),
    eee_fisico DECIMAL(6,2),
    eee_pic DECIMAL(6,2),
    meta_eficiencia DECIMAL(6,2),
    diferencia_pic_fisico DECIMAL(6,2),
    FOREIGN KEY (id_produccion) REFERENCES produccion(id_produccion) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS retenidos (
    id_retenido INT AUTO_INCREMENT PRIMARY KEY,
    id_produccion INT NOT NULL,
    id_defecto INT NOT NULL,
    cantidad_gruesas DECIMAL(12,2),
    cantidad_paletas DECIMAL(12,2),
    porcentaje DECIMAL(6,2),
    observacion TEXT,
    FOREIGN KEY (id_produccion) REFERENCES produccion(id_produccion) ON DELETE CASCADE,
    FOREIGN KEY (id_defecto) REFERENCES defectos(id_defecto)
);

CREATE TABLE IF NOT EXISTS paradas (
    id_parada INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_turno INT NOT NULL,
    id_maquina INT NOT NULL,
    id_seccion INT NOT NULL,
    id_tipo_parada INT NOT NULL,
    hora_inicio DATETIME,
    hora_fin DATETIME,
    minutos_parada INT,
    descripcion TEXT,
    FOREIGN KEY (id_turno) REFERENCES turnos(id_turno),
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_tipo_parada) REFERENCES tipos_paradas(id_tipo_parada)
);

CREATE TABLE IF NOT EXISTS eventos_operacionales (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME NOT NULL,
    id_turno INT,
    id_maquina INT,
    id_seccion INT,
    categoria VARCHAR(100),
    descripcion TEXT,
    usuario_registro INT,
    FOREIGN KEY (id_turno) REFERENCES turnos(id_turno),
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (usuario_registro) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS comentarios_produccion (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME NOT NULL,
    id_turno INT,
    id_maquina INT,
    comentario TEXT NOT NULL,
    categoria VARCHAR(100),
    usuario INT,
    FOREIGN KEY (id_turno) REFERENCES turnos(id_turno),
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
    FOREIGN KEY (usuario) REFERENCES usuarios(id_usuario)
);

CREATE TABLE IF NOT EXISTS cambios_moldes (
    id_cambio INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_maquina INT NOT NULL,
    id_seccion INT NOT NULL,
    id_molde INT NOT NULL,
    motivo VARCHAR(255),
    observacion TEXT,
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_molde) REFERENCES moldes(id_molde)
);

CREATE TABLE IF NOT EXISTS cambios_premoldes (
    id_cambio INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_maquina INT NOT NULL,
    id_seccion INT NOT NULL,
    id_premolde INT NOT NULL,
    motivo VARCHAR(255),
    observacion TEXT,
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_premolde) REFERENCES premoldes(id_premolde)
);

-- 5. TABLAS DE DETALLE Y DEPENDENCIAS SECUNDARIAS (INSPECCIÓN)
-- ------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS detalle_inspeccion (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY,
    id_inspeccion INT NOT NULL,
    id_defecto INT NOT NULL,
    cantidad_detectada INT DEFAULT 0,
    porcentaje_defecto DECIMAL(10,2),
    observacion TEXT,
    FOREIGN KEY (id_inspeccion) REFERENCES inspecciones(id_inspeccion) ON DELETE CASCADE,
    FOREIGN KEY (id_defecto) REFERENCES catalogo_defectos(id_defecto)
);

CREATE TABLE IF NOT EXISTS retenidos_inspeccion (
    id_retenido INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_maquina INT NOT NULL,
    id_seccion INT NOT NULL,
    id_producto INT NOT NULL,
    id_defecto INT NOT NULL,
    cantidad_gruesas DECIMAL(10,2),
    cantidad_paletas DECIMAL(10,2),
    observacion TEXT,
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_defecto) REFERENCES catalogo_defectos(id_defecto)
);

CREATE TABLE IF NOT EXISTS acciones_correctivas (
    id_accion INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_inspeccion INT NOT NULL,
    problema_detectado TEXT NOT NULL,
    accion_realizada TEXT NOT NULL,
    responsable VARCHAR(150),
    fecha_cierre DATE,
    estado ENUM('ABIERTA', 'EN_PROCESO', 'CERRADA') DEFAULT 'ABIERTA',
    FOREIGN KEY (id_inspeccion) REFERENCES inspecciones(id_inspeccion) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS muestreos (
    id_muestreo INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_maquina INT NOT NULL,
    id_seccion INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad_muestra INT NOT NULL,
    piezas_conformes INT DEFAULT 0,
    piezas_defectuosas INT DEFAULT 0,
    porcentaje_defecto DECIMAL(10,2),
    observaciones TEXT,
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE IF NOT EXISTS historial_defectos (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    id_defecto INT NOT NULL,
    id_maquina INT NOT NULL,
    id_seccion INT NOT NULL,
    cantidad_detectada INT,
    porcentaje DECIMAL(10,2),
    FOREIGN KEY (id_defecto) REFERENCES catalogo_defectos(id_defecto),
    FOREIGN KEY (id_maquina) REFERENCES maquinas(id_maquina),
    FOREIGN KEY (id_seccion) REFERENCES secciones(id_seccion)
);

CREATE TABLE IF NOT EXISTS evidencias_inspeccion (
    id_evidencia INT AUTO_INCREMENT PRIMARY KEY,
    id_inspeccion INT NOT NULL,
    nombre_archivo VARCHAR(255),
    ruta_archivo VARCHAR(255),
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_inspeccion) REFERENCES inspecciones(id_inspeccion) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comentarios_inspeccion (
    id_comentario INT AUTO_INCREMENT PRIMARY KEY,
    id_inspeccion INT NOT NULL,
    comentario TEXT NOT NULL,
    usuario_registra INT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_inspeccion) REFERENCES inspecciones(id_inspeccion) ON DELETE CASCADE,
    FOREIGN KEY (usuario_registra) REFERENCES usuarios(id_usuario)
);

-- ==============================================================================
-- INSERCIÓN DE DATOS SEMILLA
-- ==============================================================================

-- Usuarios
INSERT INTO usuarios (nombre, apellido, usuario, clave, cargo, rol, estado) VALUES
('Super', 'Administrador', 'admin', 'admin123', 'Superintendente de Planta', 'Administrador', 'ACTIVO'),
('Juan', 'Mendoza', 'jmendoza', 'operario123', 'Operador Especialista IS', 'Operador', 'ACTIVO'),
('María', 'García', 'mgarcia', 'inspectora123', 'Inspectora de Calidad', 'Inspector', 'ACTIVO')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre), apellido=VALUES(apellido);

-- Turnos
INSERT INTO turnos (codigo_turno, hora_inicio, hora_fin, descripcion) VALUES
('Turno A (Mañana)', '06:00:00', '14:00:00', 'Turno matutino de producción continua'),
('Turno B (Tarde)', '14:00:00', '22:00:00', 'Turno vespertino de producción continua'),
('Turno C (Noche)', '22:00:00', '06:00:00', 'Turno nocturno de producción continua')
ON DUPLICATE KEY UPDATE codigo_turno=VALUES(codigo_turno);

-- Máquinas
INSERT INTO maquinas (codigo, descripcion, cantidad_secciones, estado) VALUES
('MAQ-IS-01', 'Máquina Formadora IS de 8 Secciones - Línea 1', 8, 'ACTIVA'),
('MAQ-IS-02', 'Máquina Formadora IS de 6 Secciones - Línea 2', 6, 'ACTIVA'),
('MAQ-IS-03', 'Máquina Formadora IS de 10 Secciones - Línea 3', 10, 'MANTENIMIENTO')
ON DUPLICATE KEY UPDATE descripcion=VALUES(descripcion), cantidad_secciones=VALUES(cantidad_secciones);

-- Secciones (Línea 1: 8 Secciones, Línea 2: 6 Secciones)
INSERT INTO secciones (id_maquina, numero_seccion, estado) VALUES
(1, 1, 'ACTIVA'), (1, 2, 'ACTIVA'), (1, 3, 'ACTIVA'), (1, 4, 'ACTIVA'),
(1, 5, 'ACTIVA'), (1, 6, 'ACTIVA'), (1, 7, 'ACTIVA'), (1, 8, 'ACTIVA'),
(2, 1, 'ACTIVA'), (2, 2, 'ACTIVA'), (2, 3, 'ACTIVA'), (2, 4, 'ACTIVA'),
(2, 5, 'ACTIVA'), (2, 6, 'ACTIVA')
ON DUPLICATE KEY UPDATE estado=VALUES(estado);

-- Productos
INSERT INTO productos (codigo_producto, nombre_producto, capacidad_ml, peso_teorico, cliente, estado) VALUES
('PROD-CERV-330', 'Botella Cerveza 330ml Ámbar', 330.00, 210.00, 'Cervecería Polar', 'ACTIVO'),
('PROD-SALS-500', 'Frasco Salsa de Tomate 500g Flint', 500.00, 280.00, 'Alimentos Kraft', 'ACTIVO'),
('PROD-REF-1000', 'Botella Refresco Retornable 1L Verde', 1000.00, 520.00, 'Coca-Cola FEMSA', 'ACTIVO')
ON DUPLICATE KEY UPDATE nombre_producto=VALUES(nombre_producto);

-- Moldes y Premoldes
INSERT INTO moldes (codigo_molde, descripcion, fecha_instalacion, estado) VALUES
('MOL-CERV-330-A1', 'Molde de soplado Cerveza 330ml Cavidad 1', '2026-01-15', 'ACTIVO'),
('MOL-CERV-330-A2', 'Molde de soplado Cerveza 330ml Cavidad 2', '2026-01-15', 'ACTIVO')
ON DUPLICATE KEY UPDATE descripcion=VALUES(descripcion);

INSERT INTO premoldes (codigo_premolde, descripcion, fecha_instalacion, estado) VALUES
('PREM-CERV-330-B1', 'Premolde de preforma Cerveza 330ml Cavidad 1', '2026-01-15', 'ACTIVO'),
('PREM-CERV-330-B2', 'Premolde de preforma Cerveza 330ml Cavidad 2', '2026-01-15', 'ACTIVO')
ON DUPLICATE KEY UPDATE descripcion=VALUES(descripcion);

-- Defectos (Genérica)
INSERT INTO defectos (nombre, categoria, descripcion, activo) VALUES
('Burbuja en el fondo', 'Formación', 'Burbujas atrapadas en la base de la botella.', 1),
('Grieta en cuello', 'Formación', 'Fisuras pequeñas en la rosca o corona del envase.', 1)
ON DUPLICATE KEY UPDATE categoria=VALUES(categoria);

-- Catálogo Defectos
INSERT INTO catalogo_defectos (codigo_defecto, nombre, categoria, descripcion, criticidad, estado) VALUES
('DEF-C001', 'Grieta en Corona (Corona Rota)', 'Zona Caliente', 'Fisuras severas en la corona del envase que impiden el sellado hermético.', 'CRITICO', 'ACTIVO'),
('DEF-M002', 'Burbuja en Cuerpo (Grande)', 'Formación', 'Presencia de burbujas de aire de diámetro mayor a 3mm en las paredes.', 'MAYOR', 'ACTIVO'),
('DEF-N003', 'Hilos de vidrio internos', 'Formación', 'Hilos finos de vidrio atravesando el interior del envase (peligro severo).', 'CRITICO', 'ACTIVO'),
('DEF-L004', 'Variación de Espesor', 'Espesor', 'Espesor de pared no uniforme fuera de la tolerancia de diseño.', 'MAYOR', 'ACTIVO'),
('DEF-P005', 'Desviación de Peso', 'Físico', 'Envases con peso fuera de los límites superior o inferior de ficha técnica.', 'MENOR', 'ACTIVO')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- Tipos Paradas
INSERT INTO tipos_paradas (nombre, descripcion) VALUES
('Ajuste Mecánico IS', 'Ajustes de tiempo, soplado, pinzas o transferencia en la máquina formadora.'),
('Cambio de Molde', 'Cambio de accesorios por desgaste o por cambio de orden de producto.'),
('Fallo de Vidrio (Gota)', 'Problemas en el canal del alimentador, temperatura o cizalla de gota.'),
('Limpieza y Lubricación', 'Lubricación periódica programada de moldes y mecanismos.')
ON DUPLICATE KEY UPDATE descripcion=VALUES(descripcion);

-- Inspectores
INSERT INTO inspectores (cedula, nombre, apellido, cargo, telefono, correo, estado) VALUES
('V-12345678', 'Carlos', 'Rojas', 'Inspector de Zona Caliente', '0412-5551234', 'crojas@venvidrio.com', 'ACTIVO'),
('V-87654321', 'Ana', 'Rondón', 'Inspectora de Turno B', '0414-9998877', 'arondon@venvidrio.com', 'ACTIVO')
ON DUPLICATE KEY UPDATE nombre=VALUES(nombre);

-- Registros de Producción de prueba
INSERT INTO produccion (fecha, id_turno, id_maquina, id_producto, id_usuario, paletas_producidas, gruesas_producidas, gruesas_empacadas, gruesas_retenidas, observaciones) VALUES
('2026-06-10', 1, 1, 1, 2, 12.00, 320.00, 310.00, 10.00, 'Producción estable. Se detectaron algunas burbujas aisladas.'),
('2026-06-10', 2, 1, 1, 2, 14.50, 385.00, 380.00, 5.00, 'Excelente corrida del producto PROD-CERV-330.')
ON DUPLICATE KEY UPDATE observaciones=VALUES(observaciones);

-- Inspección de prueba
INSERT INTO inspecciones (fecha, hora, id_turno, id_inspector, id_maquina, id_seccion, id_producto, lote, temperatura_maquina, observaciones) VALUES
('2026-06-10', '08:30:00', 1, 1, 1, 3, 1, 'LOTE-20260610-A', 1150.00, 'Inspección de rutina. Se detecta pequeña fisura en cuello.')
ON DUPLICATE KEY UPDATE observaciones=VALUES(observaciones);

-- Detalle Inspección de prueba
INSERT INTO detalle_inspeccion (id_inspeccion, id_defecto, cantidad_detectada, porcentaje_defecto, observacion) VALUES
(1, 1, 2, 0.50, 'Fisuras leves en corona (defecto crítico pero bajo control)')
ON DUPLICATE KEY UPDATE observacion=VALUES(observacion);
