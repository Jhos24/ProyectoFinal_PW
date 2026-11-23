import unittest
from backend.schemas.incidentes import (
    IncidenteCreate,
    TipoResiduo,
    EstadoIncidente,
    GravedadIncidente,
    IncidenteUpdate,
)
from backend.services.incidentes import IncidenteService
from backend.repositories.incidentes import IncidenteRepository


class TestIncidentesModule(unittest.TestCase):
    def setUp(self):
        self.repo = IncidenteRepository()
        self.service = IncidenteService(self.repo)

    def test_registro_reporte_ciudadano(self):
        payload = IncidenteCreate(
            latitud=-12.0653,
            longitud=-75.2049,
            direccion_referencia="Av. Ferrocarril 123",
            distrito="Huancayo Centro",
            tipo_residuo=TipoResiduo.PLASTICOS,
            detalles="Acumulación de residuos plásticos en la vía peatonal.",
            evidencia_url="https://ejemplo.com/foto.jpg",
        )
        reporte = self.service.registrar_reporte(payload)

        self.assertIsNotNone(reporte.id)
        self.assertTrue(reporte.codigo_alerta.startswith("ECO-HYO-"))
        self.assertEqual(reporte.estado, EstadoIncidente.PENDIENTE)
        self.assertEqual(reporte.gravedad, GravedadIncidente.MEDIA)
        self.assertEqual(reporte.distrito, "Huancayo Centro")

    def test_gravedad_peligrosa(self):
        payload = IncidenteCreate(
            latitud=-12.0540,
            longitud=-75.2160,
            direccion_referencia="Orillas Río Shullcas",
            distrito="El Tambo",
            tipo_residuo=TipoResiduo.PELIGROSOS,
            detalles="Residuos punzocortantes y frascos de laboratorio abandonados.",
        )
        reporte = self.service.registrar_reporte(payload)
        self.assertEqual(reporte.gravedad, GravedadIncidente.CRITICA)

    def test_actualizacion_estado_fiscalizacion(self):
        todos = self.service.listar_incidentes()
        self.assertTrue(len(todos) > 0)
        primer_id = todos[0].id

        update_data = IncidenteUpdate(
            estado=EstadoIncidente.RESUELTO,
            observaciones_fiscalizacion="Limpieza ejecutada por brigada ambiental.",
        )
        actualizado = self.service.actualizar_estado(primer_id, update_data)

        self.assertIsNotNone(actualizado)
        self.assertEqual(actualizado.estado, EstadoIncidente.RESUELTO)
        self.assertIsNotNone(actualizado.fecha_atencion)
        self.assertIn("Limpieza ejecutada", actualizado.observaciones_fiscalizacion)

    def test_kpis_dashboard(self):
        metricas = self.service.obtener_metricas_dashboard()
        self.assertGreater(metricas.total_alertas, 0)
        self.assertIsInstance(metricas.tiempo_promedio_respuesta, str)
        self.assertIn("horas", metricas.tiempo_promedio_respuesta)


if __name__ == "__main__":
    unittest.main()
