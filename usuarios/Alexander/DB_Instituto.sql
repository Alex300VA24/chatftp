drop database if exists DB_Instituto;
create database if not exists DB_Instituto;
use DB_Instituto;

-- Crear Tabla Alumnos
create table Alumnos (
	CodAlu CHAR(5) PRIMARY KEY,
    Nombre VARCHAR(50) NOT NULL,
	Edad INT NOT NULL,
	Sexo ENUM('Masculino', 'Femenino') NOT NULL
);
-- Crer tabla Cursos
create table Cursos(
	 Cod_Curso CHAR(5) PRIMARY KEY,
     Descripcion VARCHAR(20) NOT NULL,
     Estado ENUM('ACTIVO', 'INACTIVO') NOT NULL
);
-- Crear tabla Profesor
create table Profesor(
	 Cod_Prof CHAR(5) PRIMARY KEY,
     Nombre VARCHAR(50) NOT NULL,
     Profesion VARCHAR(35) NOT NULL,
     Sexo ENUM('Masculino', 'Femenino') NOT NULL,
     Edad INT
);

-- Crear tabla Notas
create table Notas(
	 Cod_Alu CHAR(5) NOT NULL,
     Cod_Curso CHAR(5) NOT NULL,
     Cod_Prof CHAR(5) NOT NULL,
     Nota1 INT NOT NULL,
     Nota2 INT NOT NULL,
     Nota3 INT NOT NULL,
     Nota4 INT NOT NULL,
     Fecha DATE,
     FOREIGN KEY (Cod_Alu) REFERENCES Alumnos(CodAlu),
     FOREIGN KEY (Cod_Curso) REFERENCES Cursos(Cod_Curso),
     FOREIGN KEY (Cod_Prof) REFERENCES Profesor(Cod_Prof)
);


-- Insertar registro de alumnos
insert into Alumnos (CodAlu, Nombre, Edad, Sexo)
values  ('A0001', 'PEREZ SANCHEZ JUAN', 19, 'Masculino'),
		('A0002', 'SARMIENTO CESPEDES CARMEN', 15, 'Femenino'),
		('A0003', 'ALCANTARA VARGAS CARLOS', 16, 'Masculino'),
		('A0004', 'SANCHEZ SALCEDO LUIS', 19, 'Masculino'),
		('A0005', 'VALDIVIA SALCEDO ELIZABETH', 15, 'Femenino'),
		('A0006', 'ESPINOZA VARGAS CELINA', 16, 'Femenino'),
		('A0007', 'CAMPOS FLORES EDUARDO', 20, 'Masculino'),
		('A0008', 'NAVARRO RODRIGUEZ CELESTE', 19, 'Femenino'),
		('A0009', 'RAMIREZ OCHOA ALEJANDRA', 17, 'Femenino'),
		('A0010', 'SALAS FERNANDEZ JULIAN', 17, 'Masculino'),
        ('A0011', 'ESPINOZA VARGAS CELINA', 16, 'Femenino');

-- Insertar registro de Profesor
INSERT INTO Profesor (Cod_Prof, Nombre, Profesion, Sexo,  Edad)
VALUES ('P0001', 'ALVAREZ SANCHEZ JULIA', 'ING DE SISTEMAS', 'Femenino', 39),
	   ('P0002', 'SALAS ORMEA ELIZABETH', 'CONTADORA PUBLICA', 'Femenino', 29),
       ('P0003', 'SANCHEZ VERASTEGUI JULIAN', 'DR. EN MEDICINA GENERAL', 'Masculino', 49),
       ('P0004', 'LOPEZ ALCANTARA CLARA', 'DR. GINECOLOGIA', 'Femenino', 34),
       ('P0005', 'SANDOVAL PEREZ MELISSA', 'SECRETARIA EJECUTIVA', 'Femenino', 29);

-- Insertar registro de Cursos
INSERT INTO Cursos (Cod_Curso, Descripcion, Estado)
VALUES 	('C0001', 'MATEMATICA', 'ACTIVO'),
        ('C0002', 'LENGUAJE', 'ACTIVO'),
        ('C0003', 'QUIMICA', 'ACTIVO'),
        ('C0004', 'HISTORIA', 'ACTIVO'),
        ('C0005', 'GEOGRAFIA', 'ACTIVO');
        
-- RESTRICCIONES
-- El valor para el campo “Edad” de la tabla Alumnos debe ser mayor o igual que 15:

ALTER TABLE Alumnos
ADD CONSTRAINT chk_edad CHECK (Edad >= 15);

-- El valor para el campo “Edad” de la tabla Profesor debe ser mayor o igual que 25:

ALTER TABLE Profesor
ADD CONSTRAINT chk_edad_profesor CHECK (Edad >= 25);

-- Los valores ingresados para los campos Nota1, Nota2, Nota3 y Nota4 deben ser menores o iguales que 20:

ALTER TABLE Notas
ADD CONSTRAINT chk_nota1 CHECK (Nota1 <= 20),
ADD CONSTRAINT chk_nota2 CHECK (Nota2 <= 20),
ADD CONSTRAINT chk_nota3 CHECK (Nota3 <= 20),
ADD CONSTRAINT chk_nota4 CHECK (Nota4 <= 20);

-- Insertar registro a Alumnos (Evelyn Lázaro)

INSERT INTO Alumnos (CodAlu, Nombre, Edad, Sexo)
VALUES ('A0020', 'EVELYN MIRELLA LAZARO RODRIGUEZ', 18, 'Femenino');

-- Insertar registros a Cursos

INSERT INTO Notas (Cod_Alu, Cod_Curso, Cod_Prof, Nota1, Nota2, Nota3, Nota4, Fecha) 
VALUES		('A0001', 'C0001', 'P0001', 15, 18, 14, 20, '2025-01-01'),
			('A0002', 'C0002', 'P0002', 12, 16, 19, 17, '2025-01-02'),
			('A0003', 'C0003', 'P0003', 20, 20, 20, 20, '2025-01-03'),
			('A0004', 'C0004', 'P0004', 10, 11, 12, 13, '2025-01-04'),
			('A0005', 'C0005', 'P0005', 18, 19, 17, 16, '2025-01-05'),
			('A0006', 'C0001', 'P0001', 14, 15, 16, 17, '2025-01-06'),
			('A0007', 'C0002', 'P0002', 19, 18, 17, 16, '2025-01-07'),
			('A0008', 'C0003', 'P0003', 13, 14, 15, 16, '2025-01-08'),
			('A0009', 'C0004', 'P0004', 12, 13, 14, 15, '2025-01-09'),
            ('A0010', 'C0004', 'P0004', 12, 13, 14, 15, '2025-01-09'),
            ('A0011', 'C0004', 'P0004', 12, 13, 14, 15, '2025-01-09'),
			('A0020', 'C0005', 'P0005', 20, 19, 18, 17, '2025-01-10');

-- Mostrar tablas

select * from Alumnos;
select * from Profesor;
select * from Cursos;
select * from Notas;
















