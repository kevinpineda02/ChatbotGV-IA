# Chat UFG - Sistema de Chat Inteligente para la Universidad Francisco Gavidia

Un sistema de chat completo que combina una interfaz web moderna con un backend inteligente basado en RAG (Retrieval-Augmented Generation) para responder preguntas sobre la Universidad Francisco Gavidia (UFG).

## 🌟 Características Principales

### Frontend
- **Interfaz moderna y responsive** - Diseño adaptativo que funciona en dispositivos móviles y desktop
- **Chat en tiempo real** - Sistema de mensajería fluido con respuestas instantáneas
- **Integración de voz** - Funcionalidad de texto a voz con ElevenLabs (opcional)
- **Animaciones y efectos visuales** - Experiencia de usuario rica con transiciones suaves
- **Sistema de sesiones** - Memoria de conversaciones para continuidad en el chat

### Backend
- **API REST con FastAPI** - Backend rápido y escalable
- **Sistema RAG inteligente** - Búsqueda y generación de respuestas basadas en contexto
- **Base de conocimiento completa** - Información actualizada sobre carreras, precios, pensum y más
- **Procesamiento de consultas** - Clasificación inteligente de preguntas para respuestas precisas
- **Integración con Gemini AI** - Generación de respuestas naturales y conversacionales

## 📁 Estructura del Proyecto

```
Chat/
├── Backend/
│   └── Python/
│       ├── server.py           # Servidor FastAPI principal
│       ├── rag_simple.py       # Sistema RAG para contexto
│       └── README.md           # Documentación del backend
├── FrontEnd/
│   ├── index.html              # Página principal
│   ├── script.js               # Lógica del frontend (1400+ líneas)
│   ├── style.css               # Estilos CSS
│   ├── call-system.js          # Sistema de llamadas de voz
│   ├── elevenlabs-integration.md # Documentación de integración de voz
│   ├── imagenes/               # Recursos gráficos y logos
│   └── txt/                    # Base de conocimiento
│       ├── InformacionGeneral.txt
│       ├── Instrucciones.txt
│       ├── Carreras/           # Información de 38+ carreras
│       └── Precios/            # Información de costos y aranceles
```

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.11 or superior
- Navegador web moderno
- Conexión a internet (para API de Gemini)

### 1. Configuración del Backend

```bash
# Navegar al directorio del backend
cd Chat/Backend/Python

# Instalar dependencias
pip install fastapi uvicorn requests

# Ejecutar el servidor
python server.py
```

El backend estará disponible en: **http://localhost:8001**

### 2. Configuración del Frontend

```bash
# Navegar al directorio del frontend
cd Chat/FrontEnd

# Abrir index.html en un servidor web local
# Opción 1: Con Python
python -m http.server 8080

# Opción 2: Con Node.js
npx http-server

# Opción 3: Abrir directamente index.html en el navegador
```

El frontend estará disponible en: **http://localhost:8080**

### 3. Configuración de Voz (Opcional)

Para habilitar la funcionalidad de texto a voz:

1. Crea una cuenta en [ElevenLabs](https://elevenlabs.io)
2. Obtén tu API key y Voice ID
3. Configura las credenciales en `call-system.js`
4. Consulta `elevenlabs-integration.md` para más detalles

## 🎯 Funcionalidades del Sistema

### Consultas Soportadas

El sistema puede responder preguntas sobre:

- **Carreras disponibles** - Ingenierías, Licenciaturas, Técnicos
- **Información específica de carreras** - Pensum, perfil, duración, modalidad
- **Precios y aranceles** - Costos de matrícula, mensualidades, descuentos
- **Requisitos de admisión** - Documentos, proceso de inscripción
- **Información de contacto** - Teléfonos, direcciones, horarios
- **Información general** - Historia, campus, servicios de la UFG

### Ejemplos de Preguntas

```
- "¿Cuánto cuesta la carrera de Psicología?"
- "¿Qué carreras de ingeniería tienen?"
- "Muéstrame el pensum de Desarrollo de Software"
- "¿Cuáles son los requisitos para estudiar Derecho?"
- "¿Dónde está ubicada la UFG?"
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web para Python
- **Uvicorn** - Servidor ASGI
- **Python 3.11** - Lenguaje de programación
- **Google Gemini AI** - Generación de respuestas
- **Sistema RAG** - Recuperación y generación aumentada

### Frontend
- **HTML5** - Estructura semántica
- **CSS3** - Estilos modernos y animaciones
- **JavaScript ES6+** - Interactividad y lógica del cliente
- **ElevenLabs API** - Texto a voz (opcional)

## 📚 Base de Conocimiento

El sistema incluye información completa sobre:

- **38+ Carreras universitarias** con detalles completos
- **Precios actualizados** de matrícula y mensualidades
- **Información institucional** de la UFG
- **Instrucciones del sistema** para el procesamiento de consultas

## 🔧 Endpoints de la API

### Backend (Puerto 8001)
- `POST /api/mistral` - Endpoint principal para consultas
- `GET /api/session-info/{session_id}` - Información de sesión
- `POST /api/clear-memory` - Limpiar memoria de sesión

## 📈 Estado del Proyecto

### ✅ Funcionalidades Completadas
- Sistema RAG completo y funcional
- Interfaz de usuario moderna
- Procesamiento inteligente de consultas
- Base de conocimiento completa
- Sistema de sesiones y memoria
- Integración con IA (Gemini)

### 🔄 En Desarrollo
- Mejoras en la precisión de respuestas
- Optimización de rendimiento
- Funcionalidades adicionales de voz


*Última actualización: Septiembre 2025*
