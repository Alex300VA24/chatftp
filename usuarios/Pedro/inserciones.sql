use cochera2;

INSERT INTO TipoEspacio (TipoEspacio) VALUES
('Estándar'),         
('Extenso'),          
('Motocicleta'),     
('Especial'); 

INSERT INTO ClaseCliente (Clase, Frecuencia, Descuento) VALUES
('Premium', 12, 0.15),
('Gold', 8, 0.10),
('Silver', 5, 0.05),
('Bronze', 2, 0.02),
('Standard', 1, 0.00);


INSERT INTO TipoChofer (Tipo) VALUES
('Personal'),
('Taxi'),
('Carga Pesada'),
('Transporte Escolar'),
('Conductor de Empresa'),
('Privado');

INSERT INTO TiempoReserva (Periodo) VALUES
('Por hora'),
('Por día'),
('Por semana'),
('Por mes'),
('Por año');

INSERT INTO Tarifa (TipoVehiculoID, TiempoReservaID, Precio) VALUES
(1, 1, 5.00),   -- Vehículo Compacto, por hora, 5.00
(1, 2, 50.00),  -- Vehículo Compacto, por día, 50.00
(2, 1, 7.50),   -- Vehículo Mediano, por hora, 7.50
(2, 2, 70.00),  -- Vehículo Mediano, por día, 70.00
(3, 3, 350.00), -- Vehículo Grande, por semana, 350.00
(4, 1, 2.00),   -- Motocicleta, por hora, 2.00
(4, 4, 200.00), -- Motocicleta, por mes, 200.00
(5, 5, 1800.00); -- Vehículo Especial, por año, 1800.00

INSERT INTO TipoEspacio (TipoEspacio) VALUES
('Compacto'),        -- Espacio para vehículos pequeños
('Mediano'),         -- Espacio para vehículos medianos
('Grande'),          -- Espacio para vehículos grandes
('Motocicleta'),     -- Espacio para motocicletas
('Especial');        -- Espacio reservado para discapacitados u otros usos especiales

INSERT INTO EspacioEstacionamiento (TipoEspacioID, Estado) VALUES
(1, 'Disponible'),  -- Espacio Compacto disponible
(1, 'Ocupado'),     -- Espacio Compacto ocupado
(2, 'Disponible'),  -- Espacio Mediano disponible
(2, 'Disponible'),  -- Espacio Mediano disponible
(3, 'Ocupado'),     -- Espacio Grande ocupado
(4, 'Disponible'),  -- Espacio Motocicleta disponible
(5, 'Reservado');   -- Espacio Especial reservado

INSERT INTO Cliente (DniCliente, Nombres, ApePaterno, ApeMaterno, Telefono, Direccion, ClaseClienteID) VALUES
('12345678', 'Alexander', 'Perez', 'Lopez', '999888777', 'Av. Principal 123', 1),
('87654321', 'Maria', 'Rodriguez', 'Gomez', '988777666', 'Calle Secundaria 456', 2),
('11223344', 'Jose', 'Garcia', 'Hernandez', '977666555', 'Jr. Las Flores 789', 3),
('44332211', 'Lucia', 'Martinez', 'Salazar', '966555444', 'Psj. Los Rosales 321', 4),
('55667788', 'Carlos', 'Ramirez', NULL, '955444333', 'Urbanización Central 654', 5),
('66778899', 'Adriana', 'Gomez', 'Vargas', '944333222', 'Conjunto Residencial 987', 2),
('77889900', 'Fernando', 'Sanchez', NULL, '933222111', 'Barrio Nuevo 741', 1),
('88990011', 'Elena', 'Torres', 'Quispe', '922111000', 'Zona Industrial 852', 3);

INSERT INTO TipoVehiculo (Tipo) VALUES
('Automóvil'),
('Motocicleta'),
('Camioneta'),
('SUV'),
('Bus');
INSERT INTO Vehiculo (Placa, TipoVehiculoID, TarjetaPropiedad, DniCliente) VALUES
('ABC133', 2, 'TP-010-2024', '12345678'); -- Cliente Alexander, Automóvil
INSERT INTO Vehiculo (Placa, TipoVehiculoID, TarjetaPropiedad, DniCliente) VALUES
('ABC123', 1, 'TP-001-2024', '12345678'), -- Cliente Alexander, Automóvil
('XYZ789', 2, 'TP-002-2024', '87654321'), -- Cliente Maria, Motocicleta
('LMN456', 3, 'TP-003-2024', '11223344'), -- Cliente Jose, Camioneta
('JKL321', 4, 'TP-004-2024', '44332211'), -- Cliente Lucia, SUV
('DEF987', 5, 'TP-005-2024', '55667788'), -- Cliente Carlos, Bus
('GHI654', 1, 'TP-006-2024', '66778899'), -- Cliente Adriana, Automóvil
('OPQ852', 2, 'TP-007-2024', '77889900'), -- Cliente Fernando, Motocicleta
('RST963', 3, 'TP-008-2024', '88990011'); -- Cliente Elena, Camioneta

INSERT INTO Chofer (DniChofer, Nombres, ApePaterno, ApeMaterno, Telefono, TipoChoferID, Placa, DniCliente) VALUES
('87654321', 'Carlos', 'Ramirez', 'Lopez', '987654321', 1, 'ABC123', '12345678'),
('12345678', 'Carlos', 'Ramirez', 'Lopez', '987654321', 1, 'JKL321', '12345678'); -- Chofer para cliente 12345678 y vehículo ABC123
-- ('12345678', 'Lucia', 'Gomez', NULL, '912345678', 2, 'XYZ987', '12345678'),      -- Otro chofer del mismo cliente
-- ('11223344', 'Jose', 'Martinez', 'Hernandez', '934567890', 3, 'JKL456', '87654321'), -- Chofer para cliente 87654321
-- ('44332211', 'Maria', 'Salazar', 'Torres', '987654321', 4, 'MNO789', '11223344');   -- Chofer para cliente 11223344


INSERT INTO Puesto (Puesto) VALUES
('Administrador'),
('Supervisor'),
('Cajero'),
('Recepcionista'),
('Mantenimiento');

INSERT INTO Empleado (DniEmpleado, Nombres, ApePaterno, ApeMaterno, Telefono, Direccion, PuestoID) VALUES
('12345678', 'Carlos', 'Ramirez', 'Lopez', '987654321', 'Av. Principal 123', 1), -- Administrador
('87654321', 'Lucia', 'Gomez', NULL, '912345678', 'Jr. Secundario 456', 2),      -- Supervisor
('11223344', 'Jose', 'Martinez', 'Hernandez', '934567890', 'Calle Falsa 789', 3),-- Cajero
('44332211', 'Maria', 'Salazar', 'Torres', '987654321', 'Av. Central 321', 4),   -- Recepcionista
('55667788', 'Luis', 'Fernandez', NULL, '945612378', 'Jr. Los Andes 654', 5);    -- Mantenimiento

INSERT INTO Verificacion (FechaVerificacion, Estado, Observaciones, Placa, DniEmpleado) VALUES
('2024-11-01', 'Aprobado', 'Verificación sin observaciones', 'OPQ852', '12345678'), -- Carlos verifica ABC123
('2024-11-02', 'Aprobado', 'Sistema eléctrico revisado', 'LMN456', '12345678'),    -- Carlos verifica XYZ987
('2024-11-03', 'Pendiente', 'Revisión de frenos necesaria', 'JKL321', '87654321'), -- Lucia verifica JKL456
('2024-11-04', 'Aprobado', 'Estado general óptimo', 'DEF987', '11223344'),         -- Jose verifica MNO789
('2024-11-05', 'Rechazado', 'Fugas de aceite detectadas', 'RST963', '11223344');   -- Jose verifica PQR321

('LMN456', 3, 'TP-003-2024', '11223344'), -- Cliente Jose, Camioneta
('JKL321', 4, 'TP-004-2024', '44332211'), -- Cliente Lucia, SUV
('DEF987', 5, 'TP-005-2024', '55667788'), -- Cliente Carlos, Bus
('GHI654', 1, 'TP-006-2024', '66778899'), -- Cliente Adriana, Automóvil
('OPQ852', 2, 'TP-007-2024', '77889900'), -- Cliente Fernando, Motocicleta
('RST963', 3, 'TP-008-2024', '88990011'); -- Cliente Elena, Camioneta

INSERT INTO CambioTarifa (FechaCambio, PrecioAnterior, NuevoPrecio, Nota, TarifaID) VALUES
('2024-10-01', 5.00, 6.00, 'Ajuste por inflación en tarifa por hora para vehículos compactos', 8), 
('2024-10-05', 50.00, 55.00, 'Incremento por aumento en la demanda diaria', 7), 
('2024-10-10', 7.50, 8.00, 'Pequeño ajuste en tarifa por hora para vehículos medianos', 6), 
('2024-10-15', 70.00, 75.00, 'Actualización debido al mantenimiento de instalaciones', 5), 
('2024-10-20', 350.00, 375.00, 'Cambio semanal para vehículos grandes', 4), 
('2024-10-25', 2.00, 2.50, 'Incremento en tarifa por hora para motocicletas', 3), 
('2024-11-01', 200.00, 220.00, 'Ajuste mensual por motocicletas', 2), 
('2024-11-10', 1800.00, 2000.00, 'Cambio anual en tarifa mensual para vehículos grandes', 1);


INSERT INTO Reserva (FechaInicio, FechaFin, ClaseClienteID, DniCliente, Placa, TarifaID, EspacioID) VALUES
('2024-11-10', '2024-11-25', 2, '87654321', 'JKL321', 2, 2); -- Reserva por año para un cliente VIP

INSERT INTO TipoReserva (TipoReserva) VALUES
('Por Hora'),
('Por Día'),
('Por Semana'),
('Por Mes'),
('Por Año');

INSERT INTO Reembolso (FechaReembolso, MontoReembolso, PagoID)
VALUES
('2024-11-05', 15.00, 1),  -- Reembolso para el Pago 1
('2024-11-06', 20.50, 3);  -- Reembolso para el Pago 2

INSERT INTO Devolucion (FechaDevolucion, MontoDevolucion, PagoID)
VALUES
('2024-11-07', 10.00, 1),  -- Devolución para el Pago 3
('2024-11-08', 5.00, 3);   -- Devolución para el Pago 4

INSERT INTO MetodoPago (MetodoPago) VALUES
('Efectivo'),
('Tarjeta de Crédito'),
('Tarjeta de Débito'),
('Transferencia Bancaria'),
('Pago Móvil');

SELECT r.ReservaID, c.Nombres, c.ApePaterno, v.Placa, e.TipoEspacio, r.FechaInicio, r.FechaFin, t.Precio 
               FROM Reserva r 
               JOIN Cliente c ON r.DniCliente = c.DniCliente 
               JOIN Vehiculo v ON r.Placa = v.Placa 
               JOIN EspacioEstacionamiento es ON r.EspacioID = es.EspacioID 
               JOIN TipoEspacio e ON es.TipoEspacioID = e.TipoEspacioID
               JOIN Tarifa t ON r.TarifaID = t.TarifaID;