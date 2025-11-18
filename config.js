// Configuración de rutas para el proyecto
// Cambia estas URLs según tu entorno de despliegue

const CONFIG = {
    // Para desarrollo local - usar server.py local
    development: {
        API_BASE_URL: "http://localhost:8001/api",
        SOCKET_URL: "ws://localhost:8001"
    },
    
    // Para producción - usar server.py local
    production: {
        API_BASE_URL: "http://localhost:8001/api",
        SOCKET_URL: "ws://localhost:8001"
    }
};

// Detectar entorno automáticamente
function getEnvironment() {
    if (window.location.hostname === 'localhost' || 
        window.location.hostname === '127.0.0.1' || 
        window.location.hostname === '') {
        return 'development';
    }
    return 'production';
}

// Obtener configuración actual
const CURRENT_ENV = getEnvironment();
const API_CONFIG = CONFIG[CURRENT_ENV];

// Exportar configuración para uso en otros archivos
window.API_CONFIG = API_CONFIG;
window.CURRENT_ENV = CURRENT_ENV;

console.log(`🌐 Entorno detectado: ${CURRENT_ENV}`);
console.log(`🔗 API Base URL: ${API_CONFIG.API_BASE_URL}`);