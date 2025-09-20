-- Tabla carrera (existente)
CREATE TABLE IF NOT EXISTS carrera (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descripcion TEXT NOT NULL UNIQUE
);

-- Insertar datos en carrera
INSERT OR IGNORE INTO carrera (descripcion) VALUES
('Ingeniería en Sistemas de Información'),
('Licenciatura en Sistemas de Información'),
('Tecnicatura en Programación'),
('Tecnicatura en Análisis de Sistemas'),
('Tecnicatura en Redes y Telecomunicaciones');

-- Nueva tabla ciudad
CREATE TABLE IF NOT EXISTS ciudad (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    pais TEXT NOT NULL,
    poblacion INTEGER,
    fecha_fundacion DATE,
    codigo_postal TEXT,
    UNIQUE(nombre, pais)
);

-- Insertar datos en ciudad
INSERT OR IGNORE INTO ciudad (nombre, pais, poblacion, fecha_fundacion, codigo_postal) VALUES
('Bogotá', 'Colombia', 7743955, '1538-08-06', '110001'),
('Medellín', 'Colombia', 2529403, '1616-11-02', '050001'),
('Cali', 'Colombia', 2228111, '1536-07-25', '760001'),
('Barranquilla', 'Colombia', 1220533, '1629-04-07', '080001'),
('Cartagena', 'Colombia', 914552, '1533-06-01', '130001'),
('Buenos Aires', 'Argentina', 2890151, '1536-06-11', 'C1000'),
('Lima', 'Perú', 8575000, '1535-01-18', 'LIMA'),
('Ciudad de México', 'México', 9209944, '1521-08-13', '06000'),
('Santiago', 'Chile', 5672000, '1541-02-12', '8320000'),
('Caracas', 'Venezuela', 2832000, '1567-07-25', '1010');