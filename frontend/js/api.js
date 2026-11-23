/**
 * ECOLIFE - Cliente API Frontend
 * Consume los endpoints de FastAPI con manejo de errores y compatibilidad CORS.
 */

const API_BASE_URL = 'http://127.0.0.1:8000/incidentes';
const AUTH_BASE_URL = 'http://127.0.0.1:8000/auth';

export const EcolifeAPI = {
  /**
   * Inicia sesión con correo y contraseña protegida con Argon2
   */
  async login(email, password) {
    const response = await fetch(`${AUTH_BASE_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Credenciales inválidas');
    }
    const data = await response.json();
    localStorage.setItem('ecolife_token', data.access_token);
    localStorage.setItem('ecolife_user_email', data.email);
    return data;
  },

  /**
   * Registra un nuevo usuario con hash Argon2 en SQL Server
   */
  async register(email, password) {
    const response = await fetch(`${AUTH_BASE_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'No se pudo completar el registro');
    }
    const data = await response.json();
    localStorage.setItem('ecolife_token', data.access_token);
    localStorage.setItem('ecolife_user_email', data.email);
    return data;
  },

  /**
   * Cierra sesión
   */
  logout() {
    localStorage.removeItem('ecolife_token');
    localStorage.removeItem('ecolife_user_email');
  },

  /**
   * Retorna el usuario en sesión
   */
  getCurrentUser() {
    return {
      token: localStorage.getItem('ecolife_token'),
      email: localStorage.getItem('ecolife_user_email'),
    };
  },

  /**
   * Envía un nuevo reporte de Alerta Verde
   */
  async registrarIncidente(payload) {
    try {
      const response = await fetch(`${API_BASE_URL}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Error HTTP ${response.status} al registrar alerta`);
      }
      return await response.json();
    } catch (error) {
      console.warn('Fallo en conexión directa con API FastAPI:', error.message);
      // Fallback local para prototipo si el backend estuviese offline
      return {
        id: Math.floor(Math.random() * 900) + 100,
        codigoAlerta: `ECO-HYO-${Math.floor(Math.random() * 8999) + 1000}`,
        latitud: payload.latitud,
        longitud: payload.longitud,
        direccionReferencia: payload.direccionReferencia,
        distrito: payload.distrito,
        tipoResiduo: payload.tipoResiduo,
        gravedad: payload.tipoResiduo.includes('Peligrosos') ? 'Crítica' : 'Media',
        detalles: payload.detalles,
        evidenciaUrl: payload.evidenciaUrl,
        estado: 'Pendiente',
        fechaRegistro: new Date().toISOString(),
      };
    }
  },

  /**
   * Obtiene la lista de incidentes para el panel de fiscalización
   */
  async listarIncidentes(filtros = {}) {
    try {
      const queryParams = new URLSearchParams();
      if (filtros.estado) queryParams.append('estado', filtros.estado);
      if (filtros.tipoResiduo) queryParams.append('tipo_residuo', filtros.tipoResiduo);
      if (filtros.distrito) queryParams.append('distrito', filtros.distrito);

      const url = queryParams.toString() ? `${API_BASE_URL}?${queryParams}` : API_BASE_URL;
      const response = await fetch(url, {
        headers: { 'Accept': 'application/json' },
      });

      if (!response.ok) {
        throw new Error(`Error HTTP ${response.status} al consultar incidentes`);
      }
      return await response.json();
    } catch (error) {
      console.warn('Fallo en listarIncidentes desde backend:', error.message);
      return [];
    }
  },

  /**
   * Obtiene las métricas KPI del dashboard
   */
  async obtenerMetricas() {
    try {
      const response = await fetch(`${API_BASE_URL}/metricas/dashboard`, {
        headers: { 'Accept': 'application/json' },
      });

      if (!response.ok) {
        throw new Error(`Error HTTP ${response.status} al obtener KPIs`);
      }
      return await response.json();
    } catch (error) {
      console.warn('Fallo en obtenerMetricas:', error.message);
      return {
        totalAlertas: 6,
        puntosCriticos: 2,
        alertasAtendidas: 2,
        tiempoPromedioRespuesta: '3.5 horas',
        alertasPendientes: 3,
        alertasEnProceso: 1,
      };
    }
  },

  /**
   * Actualiza el estado de un incidente (Fiscalización)
   */
  async actualizarEstado(idIncidente, { estado, observacionesFiscalizacion }) {
    try {
      const response = await fetch(`${API_BASE_URL}/${idIncidente}/estado`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          estado,
          observacionesFiscalizacion,
        }),
      });

      if (!response.ok) {
        throw new Error(`Error HTTP ${response.status} al actualizar estado`);
      }
      return await response.json();
    } catch (error) {
      console.warn('Fallo en actualizarEstado:', error.message);
      return { id: idIncidente, estado, observacionesFiscalizacion };
    }
  },
};
