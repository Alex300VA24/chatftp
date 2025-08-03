CREATE DATABASE CursosOnline;
USE CursosOnline;


CREATE TABLE Cursos (
    curso_id INT,
    usuario_id INT,
    nombre_curso VARCHAR(100),
    descripcion TEXT,
    fecha_inicio DATE,
    PRIMARY KEY (curso_id, usuario_id)
);

CREATE TABLE Estudiantes (
    id_estudiante INT,
    usuario_id INT,
    curso_id INT,
    nombre VARCHAR(100),
    fecha_registro DATETIME,
    PRIMARY KEY (id_estudiante, usuario_id, curso_id),
    FOREIGN KEY (curso_id, usuario_id) REFERENCES Cursos(curso_id, usuario_id)
);

INSERT INTO Cursos (curso_id, usuario_id, nombre_curso, descripcion, fecha_inicio) VALUES
(101, 1, 'Matemáticas Básicas', 'Curso de introducción a las matemáticas', '2024-01-10'),
(102, 2, 'Física General', 'Curso de fundamentos de física', '2024-01-12'),
(103, 3, 'Química Orgánica', 'Curso sobre los principios de la química orgánica', '2024-01-15'),
(104, 4, 'Biología Molecular', 'Curso sobre la biología a nivel molecular', '2024-01-17'),
(105, 5, 'Historia del Arte', 'Curso sobre la historia del arte mundial', '2024-01-20'),
(106, 6, 'Literatura Inglesa', 'Curso sobre literatura inglesa clásica', '2024-01-22'),
(107, 7, 'Programación en Python', 'Curso de introducción a la programación en Python', '2024-01-25'),
(108, 8, 'Economía Básica', 'Curso sobre los fundamentos de la economía', '2024-01-28'),
(109, 9, 'Psicología General', 'Curso introductorio a la psicología', '2024-01-30'),
(110, 10, 'Filosofía Moderna', 'Curso sobre los principales filósofos modernos', '2024-02-01');

-- Insertar datos en la tabla Estudiantes
INSERT INTO Estudiantes (id_estudiante, usuario_id, curso_id, nombre, fecha_registro) VALUES
(1, 1, 101, 'Juan Perez', '2024-01-10'),
(2, 2, 102, 'Maria Gomez', '2024-01-12'),
(3, 3, 103, 'Luis Fernandez', '2024-01-15'),
(4, 4, 104, 'Ana Martinez', '2024-01-17'),
(5, 5, 105, 'Carlos Diaz', '2024-01-20'),
(6, 6, 106, 'Laura Sanchez', '2024-01-22'),
(7, 7, 107, 'Pedro Rodriguez', '2024-01-25'),
(8, 8, 108, 'Carmen Jimenez', '2024-01-28'),
(9, 9, 109, 'Jose Ramirez', '2024-01-30'),
(10, 10, 110, 'Elena Torres', '2024-02-01');

ALTER TABLE Cursos
ADD COLUMN duracion INT;

ALTER TABLE Estudiantes
ADD COLUMN Genero VARCHAR(15);
//--------------------------------------------
ALTER TABLE Cursos
DROP COLUMN duracion;

ALTER TABLE Estudiantes
DROP COLUMN Genero;
//--------------------------------------------
ALTER TABLE Estudiantes
MODIFY COLUMN nombre VARCHAR(150);

ALTER TABLE Cursos
MODIFY COLUMN inicio_curso datetime;
//--------------------------------------------
ALTER TABLE Cursos
CHANGE COLUMN fecha_inicio inicio_curso DATE;

ALTER TABLE Estudiantes
CHANGE COLUMN nombre name TEXT;
//--------------------------------------------
ALTER TABLE Alumnos
DROP PRIMARY KEY;

ALTER TABLE Asignaturas
DROP PRIMARY KEY;
//--------------------------------------------
ALTER TABLE Alumnos
ADD PRIMARY KEY (id_estudiante, usuario_id, curso_id);

ALTER TABLE Cursos
ADD PRIMARY KEY (curso_id, usuario_id);
//--------------------------------------------
ALTER TABLE Estudiantes
RENAME TO Alumnos;

ALTER TABLE Cursos
RENAME TO Asignaturas;
//--------------------------------------------
 
select * from Asignaturas; 
select * from Alumnos;

drop table Estudiantes;



