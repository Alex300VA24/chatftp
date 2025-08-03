use TiendaCursos;



-- Item 1 (check - repair)
-- 1.1)
CHECK TABLE Usuario;
-- 1.2)
CHECK TABLE Usuario, Profesor;
-- 1.3)
CHECK TABLE Curso QUICK;
-- 1.4)
REPAIR TABLE Curso EXTENDED;

-- Item 2 (aes_sncrypt - aes_decrypt)
-- 2.1)
SELECT AES_ENCRYPT('texto', 'llave') AS EncryptedData;
-- 2.2)
INSERT INTO Usuario (Nombre, email, email_encriptado, TipoUsuarioID) VALUES 
('Diana', 'diana@example.com', AES_ENCRYPT('diana@example.com', 'llave'), 3);
select * from usuario;

-- Querys
select * from usuario;
alter table usuario auto_increment = 4;
alter table usuario add email_encriptado varbinary(100);
delete from usuario where usuarioid = 4;
-- 2.3)
SELECT cast(AES_DECRYPT(email_encriptado, 'llave') as char) AS DecryptedEmail FROM Usuario WHERE UsuarioID = 18;
-- 2.4)
UPDATE Usuario SET email_encriptado = AES_ENCRYPT('nuevo_email@example.com', 'llave') WHERE UsuarioID = 4;

-- Item 3 (subconsultas)
select * from compra;
select * from usuario;
select * from curso;
select * from compra inner join usuario on compra.usuarioid = usuario.usuarioid;
-- 3.1)
SELECT Nombre FROM Usuario WHERE UsuarioID = (SELECT UsuarioID FROM Compra WHERE CompraID = 1);
-- 3.2)
SELECT Nombre FROM Usuario WHERE UsuarioID = (SELECT UsuarioID FROM Compra WHERE CursoID = 2);
-- 3.3)
SELECT Nombre FROM Curso WHERE CursoID = (SELECT CursoID FROM Compra WHERE UsuarioID = 3 ORDER BY FechaCompra DESC LIMIT 1);
-- 3.4)
SELECT * FROM Usuario WHERE TipoUsuarioID = (SELECT TipoUsuarioID FROM Usuario WHERE Nombre = 'Alice');

-- Item 4 (subconsultas como expresion)
-- 4.1)
SELECT (SELECT COUNT(*) FROM Usuario) AS TotalUsuarios;
-- 4.2)
SELECT Nombre, (SELECT COUNT(*) FROM Compra WHERE Usuario.UsuarioID = Compra.UsuarioID) AS TotalCompras FROM Usuario;
-- 4.3)
SELECT Nombre, (SELECT AVG(Precio) FROM Curso WHERE Curso.ProfesorID = Profesor.ProfesorID) AS PrecioPromedio FROM Profesor;
-- 4.4)
SELECT Nombre, (SELECT SUM(Precio) FROM Curso WHERE ProfesorID = Profesor.ProfesorID) / (SELECT COUNT(*) FROM Curso WHERE ProfesorID = Profesor.ProfesorID) AS PrecioPromedio FROM Profesor;

-- Item 5 (suboconsultas in)
-- 5.1)
SELECT Nombre FROM Usuario WHERE UsuarioID IN (SELECT UsuarioID FROM Compra WHERE CursoID = 2);
-- 5.2)
SELECT Nombre FROM Curso WHERE CursoID IN (SELECT CursoID FROM Compra WHERE UsuarioID = 1);
-- 5.3)
SELECT Nombre FROM Usuario WHERE UsuarioID IN (SELECT UsuarioID FROM Compra WHERE CursoID IN (SELECT CursoID FROM Curso WHERE Precio > 49));
-- 5.4)
SELECT Nombre FROM Profesor WHERE ProfesorID IN (SELECT ProfesorID FROM Curso WHERE CursoID IN (SELECT CursoID FROM Compra WHERE UsuarioID IN (SELECT UsuarioID FROM Usuario WHERE TipoUsuarioID = 3)));

-- Item 6 (any, some, all)
-- 6.1) almenos uno (any, some)
SELECT Nombre FROM Curso WHERE Precio > any (SELECT Precio FROM Curso WHERE ProfesorID = 1);
-- 6.2)
SELECT Nombre FROM Curso WHERE Precio < some (SELECT Precio FROM Curso WHERE ProfesorID = 2);
-- 6.3)
SELECT Nombre FROM Usuario WHERE 
UsuarioID = ANY (SELECT UsuarioID FROM Compra WHERE CursoID = (SELECT CursoID FROM Curso WHERE Nombre = 'Python for Beginners'));
-- 
select * from usuario;
select * from curso;
select * from compra;
select * from profesor;
-- Con inner join
SELECT u.Nombre
FROM Usuario u
INNER JOIN Compra c ON u.UsuarioID = c.UsuarioID
INNER JOIN Curso cu ON c.CursoID = cu.CursoID
WHERE cu.Nombre = 'Python for Beginners';
-- 6.4)
SELECT Nombre FROM Usuario 
WHERE UsuarioID = ALL (SELECT UsuarioID FROM Compra WHERE CursoID IN (SELECT CursoID FROM Curso WHERE ProfesorID = 2));

SELECT u.Nombre
FROM Usuario u
INNER JOIN Compra c ON u.UsuarioID = c.UsuarioID
INNER JOIN Curso cu ON c.CursoID = cu.CursoID
WHERE cu.ProfesorID = 2
GROUP BY u.Nombre
HAVING COUNT(DISTINCT c.CursoID) = (
    SELECT COUNT(*) FROM Curso WHERE ProfesorID = 2
);

-- Item 7 (correlaciones)
-- 7.1)
SELECT Nombre FROM Usuario u WHERE EXISTS (SELECT 1 FROM Compra c WHERE c.UsuarioID = u.UsuarioID);
-- 7.2)
SELECT Nombre FROM Usuario u WHERE EXISTS (SELECT 1 FROM Compra c WHERE c.UsuarioID = u.UsuarioID AND c.CursoID = 2);
-- 7.3)
SELECT Nombre FROM Curso c WHERE EXISTS (SELECT 1 FROM Compra co WHERE co.CursoID = c.CursoID AND co.UsuarioID = (SELECT UsuarioID FROM Usuario WHERE Nombre = 'Charlie'));
-- 7.4)
select * from curso;
SELECT p.Nombre
FROM Profesor p
WHERE EXISTS (
    SELECT 1
    FROM Curso c
    WHERE c.ProfesorID = p.ProfesorID
    AND EXISTS (
        SELECT 1
        FROM Compra co
        WHERE co.CursoID = c.CursoID
        AND co.UsuarioID IN (
            SELECT UsuarioID 
            FROM Usuario 
            WHERE TipoUsuarioID = 3
        )
    )
);

-- Item 8 (exists - no exists)
-- 8.1)
SELECT Nombre FROM Usuario WHERE EXISTS (SELECT 1 FROM Compra WHERE Usuario.UsuarioID = Compra.UsuarioID);
-- 8.2)
SELECT Nombre FROM Usuario WHERE NOT EXISTS (SELECT 1 FROM Compra WHERE Usuario.UsuarioID = Compra.UsuarioID);
select * from Usuario;
-- 8.3)
SELECT Nombre FROM Curso WHERE EXISTS (SELECT 1 FROM Compra WHERE Curso.CursoID = Compra.CursoID AND UsuarioID = 3);
-- 8.4)
SELECT Nombre FROM Curso WHERE NOT EXISTS (SELECT 1 FROM Compra WHERE Curso.CursoID = Compra.CursoID);

-- 9 (simil autocombinacion)
-- 9.1)
SELECT Nombre FROM Usuario WHERE UsuarioID = (SELECT MAX(UsuarioID) FROM Usuario);
-- 9.2)
SELECT Nombre FROM Curso WHERE Precio = (SELECT MAX(Precio) FROM Curso);
-- 9.3)
SELECT Nombre FROM Curso WHERE Precio = (SELECT MIN(Precio) FROM Curso);
-- 9.4)
SELECT Nombre FROM Curso WHERE Precio = (SELECT AVG(Precio) FROM Curso);

-- 10 (en lugar de una tabla)
-- 10.1)
SELECT * FROM (SELECT Nombre FROM Usuario) AS Subconsulta;
-- 10.2)
SELECT Nombre FROM (SELECT * FROM Curso WHERE Precio > 50) AS Subconsulta;
-- 10.3)
SELECT Sub.Nombre, Sub.TotalCompras FROM (SELECT Usuario.Nombre, COUNT(Compra.CompraID) AS TotalCompras FROM Usuario LEFT JOIN Compra ON Usuario.UsuarioID = Compra.UsuarioID GROUP BY Usuario.Nombre) AS Sub WHERE Sub.TotalCompras > 1;
-- 10.4)
SELECT p.Especialidad, c.Nombre AS CursoNombre FROM Profesor p JOIN (SELECT ProfesorID, Nombre FROM Curso) AS c ON p.ProfesorID = c.ProfesorID;

select * from usuario;
select * from profesor;
select * from curso;
-- 11 (update - delete)
-- 11.1)
UPDATE Usuario SET Email = 'charlie@example.com' WHERE UsuarioID = (SELECT UsuarioID FROM Usuario WHERE Nombre = 'Charlie');
-- 11.2)
DELETE FROM Compra WHERE UsuarioID = (SELECT UsuarioID FROM Usuario WHERE Nombre = 'Bob');
-- 11.3)
UPDATE Curso SET Precio = ROUND(Precio * 1.10, 2) WHERE ProfesorID = (SELECT ProfesorID FROM Profesor WHERE Especialidad = 'Cyberseguridad');
-- 11.4)
SET SQL_SAFE_UPDATES = 0;
DELETE FROM Curso WHERE CursoID IN (SELECT CursoID FROM Curso WHERE ProfesorID = (SELECT ProfesorID FROM Profesor WHERE Especialidad= 'Web Development'));

-- 12 (insert)
-- 12.1)
INSERT INTO Usuario (Nombre, Email, TipoUsuarioID) SELECT 'Eva', 'eva@example.com', TipoUsuarioID FROM TipoUsuario WHERE TipoUsuario = 'Estudiante';

-- 12.2)
INSERT INTO Profesor (Especialidad, TipoUsuarioID) SELECT 'Cybersecurity', 2 WHERE NOT EXISTS (SELECT 1 FROM Profesor WHERE Especialidad = 'Cybersegurity');

-- 12.3)
INSERT INTO Curso (Nombre, Descripcion, Precio, ProfesorID) SELECT 'New Course', 'Description', 75.00, ProfesorID FROM Profesor WHERE Especialidad = 'Data Science';

-- 12.4)
INSERT INTO Compra (UsuarioID, CursoID, FechaCompra) SELECT UsuarioID, 1, CURDATE() FROM Usuario WHERE NOT EXISTS (SELECT 1 FROM Compra WHERE UsuarioID = Usuario.UsuarioID AND CursoID = 1);













