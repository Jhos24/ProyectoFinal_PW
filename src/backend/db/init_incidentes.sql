-- ==============================================================================
-- ECOLIFE - Sistema de Gestión y Remediación de Vertederos en Huancayo, Perú
-- Script DDL para creación de la tabla IncidenteAmbiental en Microsoft SQL Server
-- ==============================================================================

IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='IncidenteAmbiental' AND xtype='U')
BEGIN
    CREATE TABLE IncidenteAmbiental (
        id INT IDENTITY(1,1) PRIMARY KEY,
        codigo_alerta NVARCHAR(50) NOT NULL UNIQUE,
        latitud FLOAT NOT NULL,
        longitud FLOAT NOT NULL,
        direccion_referencia NVARCHAR(255) NOT NULL,
        distrito NVARCHAR(100) NOT NULL,
        tipo_residuo NVARCHAR(100) NOT NULL,
        gravedad NVARCHAR(50) NOT NULL DEFAULT 'Media',
        detalles NVARCHAR(MAX) NOT NULL,
        evidencia_url NVARCHAR(MAX) NULL,
        estado NVARCHAR(50) NOT NULL DEFAULT 'Pendiente',
        fecha_registro DATETIME2 NOT NULL DEFAULT GETDATE(),
        fecha_atencion DATETIME2 NULL,
        observaciones_fiscalizacion NVARCHAR(MAX) NULL
    );

    CREATE NONCLUSTERED INDEX IX_Incidente_Estado ON IncidenteAmbiental(estado);
    CREATE NONCLUSTERED INDEX IX_Incidente_Distrito ON IncidenteAmbiental(distrito);
    CREATE NONCLUSTERED INDEX IX_Incidente_TipoResiduo ON IncidenteAmbiental(tipo_residuo);
    CREATE NONCLUSTERED INDEX IX_Incidente_Gravedad ON IncidenteAmbiental(gravedad);
END
GO
