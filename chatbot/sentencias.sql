-- Eliminar la tabla carrera si existe
DROP TABLE IF EXISTS carrera;

-- Crear la tabla carrera con la nueva estructura
CREATE TABLE carrera (
    codigo TEXT PRIMARY KEY,
    descripcion TEXT NOT NULL UNIQUE
);

-- Insertar datos en carrera
INSERT OR IGNORE INTO carrera (codigo, descripcion) VALUES
('IS001', 'Ingeniería en Sistemas de Información'),
('LS001', 'Licenciatura en Sistemas de Información'),
('TP001', 'Tecnicatura en Programación'),
('TA001', 'Tecnicatura en Análisis de Sistemas'),
('TR001', 'Tecnicatura en Redes y Telecomunicaciones');

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