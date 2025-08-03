DROP DATABASE IF EXISTS comisaria;
CREATE DATABASE comisaria;
USE comisaria;

CREATE TABLE Personal (
    DNI CHAR(8) PRIMARY KEY,
    Nombre VARCHAR(50),
    Apellido VARCHAR(50),
    Usuario VARCHAR(50) UNIQUE NOT NULL,
    Contraseña VARCHAR(80) NOT NULL,
    Fecha_Entrada DATE,
    Cargo VARCHAR(50)
);

CREATE TABLE Ubicacion (
    id_ubicacion INT AUTO_INCREMENT PRIMARY KEY,
    nombre_ubicacion VARCHAR(255)
);

CREATE TABLE Delito (
    id_delito INT AUTO_INCREMENT PRIMARY KEY,
    Tipo ENUM('Robos y Asaltos', 'Microcomercializacion de Drogas', 'Violencia Familiar', 'Pandillaje', 'Homicidios', 'Secuestros'),
    Fecha_Delito DATE,
    id_ubicacion INT,
    DNI CHAR(8),
    FOREIGN KEY (id_ubicacion) REFERENCES Ubicacion(id_ubicacion),
    FOREIGN KEY (DNI) REFERENCES Personal(DNI)
);

-- Insertar Personal (3 registros)
INSERT INTO Personal (DNI, Nombre, Apellido, Usuario, Contraseña, Fecha_Entrada, Cargo) VALUES
('87654321', 'Carlos', 'Pérez', 'cperez', 'hashed12345', '2024-01-15', 'Oficial'),
('98765432', 'María', 'López', 'mlopez', 'hashedabcdef', '2024-03-10', 'Suboficial'),
('12345678', 'Juan', 'Martínez', 'jmartinez', 'hashedghijkl', '2024-05-20', 'Inspector');


-- Insertar Ubicaciones (13 zonas)
INSERT INTO Ubicacion (nombre_ubicacion) VALUES
('Zona 1'), ('Zona 2'), ('Zona 3'), ('Zona 4'),
('Zona 5'), ('Zona 6'), ('Zona 7'), ('Zona 8'),
('Zona 9'), ('Zona 10'), ('Zona 11'), ('Zona 12'),
('Zona 13');

-- Aproximadamente 71.5% Robos y Asaltos (6721) - Ajustado para la comisaría
-- Aproximadamente 13.7% Seguridad Pública (1288) -  Microcomercializacion de Drogas 
-- Aproximadamente 3.9% Contra la vida (366) - Homicidios
-- Aproximadamente 6.2% Contra la libertad (581) - Secuestros
-- Aproximadamente 2.0% Contra la administración pública (188) - Pandillaje
-- Aproximadamente 2.7% Otros (256) - Violencia Familiar


DELIMITER //

CREATE PROCEDURE insertar_delitos(IN num_delitos INT, IN id_ubicacion INT, IN tipo_delito VARCHAR(255))
BEGIN
    DECLARE i INT DEFAULT 1;
    WHILE i <= num_delitos DO
        INSERT INTO Delito (Tipo, Fecha_Delito, id_ubicacion, DNI) VALUES (tipo_delito, DATE_ADD('2024-11-01', INTERVAL (RAND() * 30) DAY), id_ubicacion, (SELECT DNI FROM Personal ORDER BY RAND() LIMIT 1));
        SET i = i + 1;
    END WHILE;
END //

DELIMITER ;

-- Ejemplo de uso del procedimiento para la Zona 1 (Robos y Asaltos)
CALL insertar_delitos(157, 1, 'Robos y Asaltos');  -- 71.4% de 300
CALL insertar_delitos(68, 1, 'Microcomercializacion de Drogas'); -- 13.6% de 300
CALL insertar_delitos(19, 1, 'Homicidios'); -- 3.8% de 300
CALL insertar_delitos(31, 1, 'Secuestros');  -- 6.2% de 300
CALL insertar_delitos(10, 1, 'Pandillaje'); -- 2.0% de 300
CALL insertar_delitos(15, 1, 'Violencia Familiar'); -- 3.0% de 300


-- Zona 2 (Ejemplo: 200 delitos totales)
CALL insertar_delitos(86, 2, 'Robos y Asaltos'); -- 71.5%
CALL insertar_delitos(54, 2, 'Microcomercializacion de Drogas'); -- 13.5%
CALL insertar_delitos(15, 2, 'Homicidios'); -- 3.75%
CALL insertar_delitos(25, 2, 'Secuestros'); -- 6.25%
CALL insertar_delitos(8, 2, 'Pandillaje');  -- 2%
CALL insertar_delitos(12, 2, 'Violencia Familiar'); -- 3%

-- Zona 3 (Ejemplo: 200 delitos totales)
CALL insertar_delitos(114, 3, 'Robos y Asaltos');  -- 71.33%
CALL insertar_delitos(41, 3, 'Microcomercializacion de Drogas'); -- 13.67%
CALL insertar_delitos(11, 3, 'Homicidios'); -- 3.67%
CALL insertar_delitos(19, 3, 'Secuestros'); -- 6.33%
CALL insertar_delitos(6, 3, 'Pandillaje'); -- 2%
CALL insertar_delitos(9, 3, 'Violencia Familiar'); -- 3%

-- Zona 4 (con un total de 300 delitos, para mostrar la variación)
CALL insertar_delitos(129, 4, 'Robos y Asaltos'); -- 71.5%
CALL insertar_delitos(81, 4, 'Microcomercializacion de Drogas'); -- 13.5%
CALL insertar_delitos(23, 4, 'Homicidios'); -- 3.83%
CALL insertar_delitos(37, 4, 'Secuestros'); -- 6.17%
CALL insertar_delitos(12, 4, 'Pandillaje'); -- 2%
CALL insertar_delitos(18, 4, 'Violencia Familiar'); -- 3%


-- Zona 5 (Ejemplo: 350 delitos totales)
CALL insertar_delitos(193, 5, 'Robos y Asaltos'); -- 71.45%
CALL insertar_delitos(74, 5, 'Microcomercializacion de Drogas'); -- 13.45%
CALL insertar_delitos(21, 5, 'Homicidios'); -- 3.82%
CALL insertar_delitos(34, 5, 'Secuestros'); -- 6.18%
CALL insertar_delitos(11, 5, 'Pandillaje'); -- 2%
CALL insertar_delitos(17, 5, 'Violencia Familiar'); -- 3.09%


-- Zona 6 (Ejemplo: 280 delitos totales)
CALL insertar_delitos(143, 6, 'Robos y Asaltos'); -- 71.46%
CALL insertar_delitos(65, 6, 'Microcomercializacion de Drogas'); -- 13.54%
CALL insertar_delitos(18, 6, 'Homicidios'); -- 3.75%
CALL insertar_delitos(30, 6, 'Secuestros'); -- 6.25%
CALL insertar_delitos(10, 6, 'Pandillaje'); -- 2.08%
CALL insertar_delitos(14, 6, 'Violencia Familiar'); -- 2.92%

-- Zona 7 (Ejemplo: 250 delitos totales)
CALL insertar_delitos(150, 7, 'Robos y Asaltos'); -- 71.43%
CALL insertar_delitos(47, 7, 'Microcomercializacion de Drogas'); -- 13.43%
CALL insertar_delitos(13, 7, 'Homicidios'); -- 3.71%
CALL insertar_delitos(22, 7, 'Secuestros'); -- 6.29%
CALL insertar_delitos(7, 7, 'Pandillaje'); -- 2%
CALL insertar_delitos(11, 7, 'Violencia Familiar'); -- 3.14%

-- Zona 8 (Ejemplo: 320 delitos totales)
CALL insertar_delitos(143, 8, 'Robos y Asaltos'); -- 71.45%
CALL insertar_delitos(84, 8, 'Microcomercializacion de Drogas'); -- 13.55%
CALL insertar_delitos(24, 8, 'Homicidios'); -- 3.87%
CALL insertar_delitos(39, 8, 'Secuestros'); -- 6.29%
CALL insertar_delitos(13, 8, 'Pandillaje'); -- 2.1%
CALL insertar_delitos(17, 8, 'Violencia Familiar'); -- 2.74%


-- Zona 9 (Ejemplo: 300 delitos totales -  igual que la zona 2 para mostrar que se pueden repetir totales)
CALL insertar_delitos(186, 9, 'Robos y Asaltos'); -- 71.5%
CALL insertar_delitos(54, 9, 'Microcomercializacion de Drogas'); -- 13.5%
CALL insertar_delitos(15, 9, 'Homicidios'); -- 3.75%
CALL insertar_delitos(25, 9, 'Secuestros'); -- 6.25%
CALL insertar_delitos(8, 9, 'Pandillaje'); -- 2%
CALL insertar_delitos(12, 9, 'Violencia Familiar'); -- 3%

-- Zona 10 (Ejemplo: 180 delitos totales)
CALL insertar_delitos(100, 10, 'Robos y Asaltos');  -- 71.43%
CALL insertar_delitos(38, 10, 'Microcomercializacion de Drogas'); -- 13.57%
CALL insertar_delitos(11, 10, 'Homicidios'); -- 3.93%
CALL insertar_delitos(17, 10, 'Secuestros'); -- 6.07%
CALL insertar_delitos(6, 10, 'Pandillaje'); -- 2.14%
CALL insertar_delitos(8, 10, 'Violencia Familiar'); -- 2.86%


-- Zona 11 (Ejemplo: 320 delitos totales)
CALL insertar_delitos(171, 11, 'Robos y Asaltos');  -- 71.35%
CALL insertar_delitos(70, 11, 'Microcomercializacion de Drogas');  -- 13.46%
CALL insertar_delitos(19, 11, 'Homicidios'); -- 3.65%
CALL insertar_delitos(33, 11, 'Secuestros');  -- 6.35%
CALL insertar_delitos(11, 11, 'Pandillaje');  -- 2.12%
CALL insertar_delitos(16, 11, 'Violencia Familiar');  -- 3.08%

-- Zona 12 (Ejemplo: 250 delitos totales)
CALL insertar_delitos(121, 12, 'Robos y Asaltos'); -- 71.33%
CALL insertar_delitos(61, 12, 'Microcomercializacion de Drogas'); -- 13.56%
CALL insertar_delitos(17, 12, 'Homicidios'); -- 3.78%
CALL insertar_delitos(27, 12, 'Secuestros'); -- 6%
CALL insertar_delitos(9, 12, 'Pandillaje'); -- 2%
CALL insertar_delitos(15, 12, 'Violencia Familiar'); -- 3.33%


-- Zona 13 (Ejemplo: 280 delitos totales)
CALL insertar_delitos(171, 13, 'Robos y Asaltos'); -- 71.32%
CALL insertar_delitos(51, 13, 'Microcomercializacion de Drogas');  -- 13.42%
CALL insertar_delitos(14, 13, 'Homicidios');  -- 3.68%
CALL insertar_delitos(23, 13, 'Secuestros'); -- 6.05%
CALL insertar_delitos(8, 13, 'Pandillaje');  -- 2.11%
CALL insertar_delitos(13, 13, 'Violencia Familiar');  -- 3.42%

select * from delito;
select * from personal;
select * from ubicacion;