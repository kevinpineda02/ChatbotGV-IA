from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import json
import re
import time
import random
from rag_simple import RAGSystemSimple

app = FastAPI()

# SISTEMA DE VALIDACIÓN DE CONSULTAS INTELIGENTE
class QueryValidator:
    def __init__(self):
        # Patrones de preguntas técnicas válidas sobre la UFG
        self.technical_patterns = [
            # Carreras y programas
            r'\b(carrera|carreras|ingenier[ií]a|licenciatura|t[eé]cnico|programa|estudiar|estudios)\b',
            # Pensum y académico
            r'\b(pensum|plan\s+de\s+estudios|materias|asignaturas|ciclos|semestres|malla\s+curricular)\b',
            r'\b(qu[eé]\s+(estudia|ense[ñn]an|ve|lleva|tiene))\b',
            # Información universitaria
            r'\b(modalidad|presencial|semipresencial|duraci[oó]n|requisitos|admisi[oó]n)\b',
            r'\b(precio|costo|cuota|mensualidad|arancel|matricula|inscripci[oó]n)\b',
            r'\b(contacto|tel[eé]fono|direcci[oó]n|ubicaci[oó]n|horario|informaci[oó]n)\b',
            # UFG específico
            r'\b(ufg|universidad\s+francisco\s+gavidia|francisco\s+gavidia)\b',
            # Títulos y certificaciones
            r'\b(t[ií]tulo|certificado|grado|egreso|graduaci[oó]n)\b',
            # Búsquedas específicas
            r'\b(lista|listado|todas|todos|cu[aá]les|cu[aá]ntos|opciones|disponibles)\b'
        ]
        
        # Patrones de preguntas sin sentido o irrelevantes
        self.nonsense_patterns = [
            # Consultas muy vagas sin contexto educativo
            r'^\s*(que|quien|donde|cuando|como|por\s+que)\s*[.!?]*\s*$',
            # Spam o caracteres sin sentido
            r'^[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]*$|^(.)\1{4,}',
            # Preguntas sobre otras universidades
            r'\b(harvard|mit|stanford|otras?\s+universidades|otra\s+universidad)\b',
            # Temas completamente ajenos
            r'\b(clima|tiempo|deportes|pol[ií]tica|comida|m[uú]sica|pel[ií]culas)\b',
            # Preguntas filosóficas o existenciales
            r'\b(sentido\s+de\s+la\s+vida|felicidad|amor|existencia)\b'
        ]
        
        # ...se elimina la sección de patrones de saludo...
        
        # Palabras clave importantes de UFG
        self.ufg_keywords = [
            'ufg', 'francisco gavidia', 'universidad francisco gavidia',
            'carrera', 'carreras', 'ingenieria', 'licenciatura', 'tecnico',
            'pensum', 'materias', 'ciclos', 'estudios', 'modalidad',
            'precio', 'costo', 'admision', 'requisitos', 'contacto'
        ]
        
        # Patrones de agradecimiento
        self.thanks_patterns = [
            r'\b(gracias|muchas gracias|te agradezco|thank you|mil gracias)\b'
        ]
    
    # Se elimina la función is_greeting
    
    def is_thanks(self, query: str) -> bool:
        """Detecta si la consulta es un agradecimiento"""
        query_lower = query.lower().strip()
        for pattern in self.thanks_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True
        return False
    
    def is_technical_query(self, query: str) -> bool:
        """Determina si la consulta es técnica y relevante para la UFG"""
        query_lower = query.lower().strip()
        
        # Verificar si contiene patrones técnicos
        for pattern in self.technical_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True
        
        # Verificar palabras clave de UFG
        for keyword in self.ufg_keywords:
            if keyword.lower() in query_lower:
                return True
        
        return False
    
    def is_nonsense_query(self, query: str) -> bool:
        """Determina si la consulta es sin sentido o irrelevante"""
        query_lower = query.lower().strip()
        
        # Consultas muy cortas (menos de 3 caracteres)
        if len(query_lower) < 3:
            return True
        
        # Verificar patrones de sin sentido
        for pattern in self.nonsense_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True
        
        return False
    
    def get_query_relevance_score(self, query: str) -> float:
        """Calcula un puntaje de relevancia para la consulta (0.0 a 1.0)"""
        query_lower = query.lower().strip()
        score = 0.0
        
        # Puntuar por palabras clave técnicas
        technical_matches = 0
        for pattern in self.technical_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                technical_matches += 1
        
        # Puntuar por palabras clave UFG
        ufg_matches = 0
        for keyword in self.ufg_keywords:
            if keyword.lower() in query_lower:
                ufg_matches += 1
        
        # Calcular puntaje base
        score = min(1.0, (technical_matches * 0.2) + (ufg_matches * 0.15))
        
        # Penalizar si es muy corto
        if len(query_lower) < 10:
            score *= 0.7
        
        # Bonificar si tiene múltiples palabras relacionadas
        if technical_matches >= 2:
            score += 0.2
        
        # Penalizar si coincide con patrones sin sentido
        if self.is_nonsense_query(query):
            score *= 0.1
        
        return min(1.0, score)
    
    def classify_query_type(self, query: str) -> str:
        """Clasifica el tipo de consulta"""
        query_lower = query.lower().strip()
        
        if self.is_thanks(query):
            return "thanks"
        
        if self.is_nonsense_query(query):
            return "nonsense"
        
        if not self.is_technical_query(query):
            return "casual"
        
        # Clasificar tipo técnico específico
        if re.search(r'\b(pensum|plan\s+de\s+estudios|materias|asignaturas)\b', query_lower):
            return "pensum"
        elif re.search(r'\b(carrera|carreras|ingenier[ií]a|licenciatura)\b', query_lower):
            return "careers"
        elif re.search(r'\b(precio|costo|cuota|arancel)\b', query_lower):
            return "pricing"
        elif re.search(r'\b(contacto|tel[eé]fono|direcci[oó]n|ubicaci[oó]n)\b', query_lower):
            return "contact"
        elif re.search(r'\b(admisi[oó]n|requisitos|inscripci[oó]n)\b', query_lower):
            return "admission"
        else:
            return "technical"

def get_specific_instructions(query_type: str) -> str:
    """Genera instrucciones específicas según el tipo de consulta"""
    instructions = {
        "greeting": """
- PRIORIDAD MÁXIMA: Ser amigable, cálido y acogedor.
- Saluda de manera natural y entusiasta.
- Preséntate como GV-IA, el asistente virtual de la UFG.
- Pregunta específicamente en qué puedes ayudar.
- Menciona los principales servicios que ofreces (carreras, pensums, precios, admisión).
- Mantén un tono conversacional y cercano.
        """,
        "pensum": """
- PRIORIDAD MÁXIMA: Proporcionar información detallada sobre planes de estudio, materias y ciclos.
- Nunca digas que no tienes información sobre pensums.
- Si encuentras información sobre pensum, lista TODAS las materias por ciclo.
- Incluye información sobre Unidades Valorativas (UV) si está disponible.
- Especifica requisitos entre materias si están mencionados.
- Proporciona información completa sobre duración y estructura académica.
- FORMATO OBLIGATORIO: Organiza por ciclos con numeración clara y saltos de línea.
- EJEMPLO:
  CICLO I:
  1. Materia 1 (4 UV)
  2. Materia 2 (4 UV)
  
  CICLO II:
  1. Materia 3 (4 UV)
  2. Materia 4 (4 UV)
        """,
        "careers": """
- PRIORIDAD MÁXIMA: Listar carreras disponibles según lo solicitado.
- Cuando pregunten por "ingenierías", lista SOLO las que empiecen con "INGENIERÍA EN...".
- Cuando pregunten por "licenciaturas", lista SOLO las que empiecen con "LICENCIATURA EN...".
- Cuando pregunten por "técnicos", lista SOLO los que empiecen con "TÉCNICO EN...".
- NO mezcles tipos de carreras a menos que pregunten por "todas las carreras".
- Incluye modalidades (presencial/semipresencial) cuando estén disponibles.
- Cuando des el listado de carreras, no digas que falta información.
- FORMATO OBLIGATORIO: Cada carrera debe estar en una línea separada con numeración.
- EJEMPLO: 
  1. Ingeniería en Software (Presencial)
  2. Ingeniería en Sistemas (Presencial)
  3. Licenciatura en Psicología (Presencial)
        """,
        "pricing": """
- PRIORIDAD MÁXIMA: Proporcionar información sobre costos y aranceles.
- Si no hay información específica de precios, redirige a contacto oficial.
- Menciona opciones de financiamiento o becas si están disponibles.
        """,
        "contact": """
- PRIORIDAD MÁXIMA: Proporcionar información de contacto oficial.
- Incluye teléfonos, emails, direcciones y horarios disponibles.
- Proporciona información sobre ubicación y cómo llegar si está disponible.
        """,
        "admission": """
- PRIORIDAD MÁXIMA: Información sobre proceso de admisión y requisitos.
- Lista todos los requisitos de ingreso mencionados.
- Incluye información sobre documentos necesarios y procesos.
        """,
        "technical": """
- PRIORIDAD: Responder de manera técnica y precisa.
- Enfocar en aspectos académicos y universitarios específicos.
- Mantener un tono profesional pero amigable.
        """,
        "casual": """
- PRIORIDAD: Redirigir hacia temas específicos de la UFG de manera amigable.
- Ser cordial y acogedor en el tono.
- Sugerir temas específicos sobre los que puede ayudar.
        """
    }
    
    return instructions.get(query_type, instructions["technical"])

# Inicializar validador
query_validator = QueryValidator()

# Configuración de Google Gemini
GEMINI_API_KEY = "AIzaSyBFx7d3crRHe9iKw3gfaAveVZvdtAq-dGg"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

# Inicializar sistema RAG simple que funciona correctamente
txt_folder_path = r"C:\Users\kevin\OneDrive\Escritorio\Chat\FrontEnd\txt"
rag = RAGSystemSimple(txt_folder_path)

# Middleware CORS para permitir acceso desde tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Reemplázalo por tu dominio para más seguridad
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos recibido desde el frontend
class PromptRequest(BaseModel):
    prompt: str

# Memoria del chat en RAM
chat_memory = []
MAX_HISTORY = 10  # Número máximo de pares pregunta-respuesta a mantener

@app.post("/api/mistral")
async def generate_response(request: PromptRequest):
    try:
        # VALIDACIÓN INTELIGENTE DE LA CONSULTA
        query_type = query_validator.classify_query_type(request.prompt)
        relevance_score = query_validator.get_query_relevance_score(request.prompt)
        
        print(f"🔍 Consulta: {request.prompt}")
        print(f"📊 Tipo: {query_type}, Relevancia: {relevance_score:.2f}")
        
        # ...se elimina la sección de manejo de saludos...
        
        # Manejar consultas sin sentido
        if query_type == "nonsense":
            def nonsense_response():
                response = "Lo siento, no logro entender tu consulta. Por favor, hazme una pregunta específica sobre la Universidad Francisco Gavidia (UFG), como información sobre carreras, pensums, precios o admisiones."
                yield response
            return StreamingResponse(nonsense_response(), media_type="text/plain")
        
        # Manejar consultas casuales (redirigir hacia temas UFG de manera amigable)
        if query_type == "casual" and relevance_score < 0.3:
            def casual_response():
                casual_responses = [
                    "Hola! Soy GV-IA, el asistente virtual de la Universidad Francisco Gavidia. Estoy aquí para ayudarte con información sobre nuestras carreras, pensums, precios, modalidades de estudio y proceso de admisión. ¿En qué puedo ayudarte específicamente?",
                    
                    "¡Hola! Me alegra conocerte. Soy tu asistente virtual de la UFG y estoy para ayudarte. ¿Te interesa conocer sobre alguna carrera en particular? Tenemos ingenierías, licenciaturas y técnicos disponibles.",
                    
                    "¡Saludos! Soy GV-IA de la Universidad Francisco Gavidia. ¿Hay algo específico sobre la UFG que te gustaría saber? Puedo contarte sobre nuestras carreras, planes de estudio, modalidades y mucho más."
                ]
                
                response = random.choice(casual_responses)
                yield response
            return StreamingResponse(casual_response(), media_type="text/plain")
        
        # Manejar agradecimientos de manera especial
        if query_type == "thanks":
            def thanks_response():
                thanks_responses = [
                    "¡De nada! Si tienes más preguntas sobre la UFG, aquí estaré para ayudarte.",
                    "¡Con gusto! Si necesitas información adicional, no dudes en preguntar.",
                    "¡Para eso estoy! Si tienes otra consulta sobre carreras, pensums o servicios, dime.",
                    "¡Gracias a ti por contactarme! ¿Hay algo más que quieras saber sobre la UFG?"
                ]
                response = random.choice(thanks_responses)
                yield response
            return StreamingResponse(thanks_response(), media_type="text/plain")

        # Añadir el mensaje del usuario a la memoria
        chat_memory.append({"role": "user", "content": request.prompt})

        # Limpiar memoria si excede el límite
        if len(chat_memory) > MAX_HISTORY * 2:
            chat_memory.pop(0)

        # Si la consulta es sobre pensum pero no se menciona una carrera específica, pedir que sea más específico
        if query_type == "pensum":
            # Buscar si se menciona alguna carrera específica en la consulta
            carrera_keywords = [
                "administracion", "turistica", "animacion", "arquitectura", "infancia", "politicas", "comunicaciones", "contaduria", "control electrico", "criminologia", "moda", "publicitario", "web", "economia", "gestion", "industrial", "ingles", "leyes", "informatica", "sistemas", "mercadotecnia", "psicologia", "relaciones", "robotica", "social", "software", "tec animacion", "tec conta", "tec decoracion", "tec publicidad", "tec restaurante", "tec sistemas", "tec turismo", "tec ventas", "telecomunicaciones", "videojuegos"
            ]
            consulta = request.prompt.lower()
            menciona_carrera = any(kw in consulta for kw in carrera_keywords)
            if not menciona_carrera:
                def ask_career_response():
                    response = "¿Sobre qué carrera te gustaría conocer el pensum? Por favor, indícame el nombre de la carrera para mostrarte el plan de estudios correspondiente."
                    yield response
                return StreamingResponse(ask_career_response(), media_type="text/plain")

        # BUSCAR INFORMACIÓN RELEVANTE CON RAG SIMPLE (solo para consultas válidas)
        relevant_context = rag.get_context_for_query(request.prompt, max_context_length=60000)
        
        # Verificar si el RAG encontró información relevante
        if not relevant_context or len(relevant_context.strip()) < 50:
            def no_context_response():
                if query_type in ["careers", "pensum", "pricing", "admission", "contact"]:
                    response = f"No encontré información específica sobre tu consulta en nuestros registros. Para obtener información detallada sobre {query_type}, te recomiendo contactar directamente:\n\n- Teléfono: 2209-2834\n- Email: contactcenter@ufg.edu.sv\n- Web: https://www.ufg.edu.sv/"
                else:
                    response = "No tengo información específica sobre esa consulta. ¿Podrías ser más específico sobre qué aspecto de la UFG te interesa? Puedo ayudarte con información sobre carreras, pensums, precios o admisiones."
                yield response
            return StreamingResponse(no_context_response(), media_type="text/plain")

        # Construir el contexto del chat con información de la universidad
        base_context = f"""Eres GV-IA, el asistente virtual oficial de la Universidad Francisco Gavidia (UFG) en El Salvador.

Tu misión es ayudar a estudiantes, prospectivos estudiantes y visitantes con información.

TIPO DE CONSULTA DETECTADA: {query_type.upper()}
RELEVANCIA: {relevance_score:.2f}

INFORMACIÓN RELEVANTE DE LA UFG:
""" + relevant_context + "\n\nHISTORIAL DE CONVERSACIÓN:\n"

        for turno in chat_memory:
            rol = "Usuario" if turno["role"] == "user" else "GV-IA"
            base_context += f"{rol}: {turno['content']}\n"

        final_prompt = f"{base_context}GV-IA:"

        # Función generadora para enviar la respuesta en streaming con Gemini
        def stream_response():
            # Formatear el prompt para Gemini con contexto RAG mejorado
            system_instruction = f"""Eres GV-IA, el asistente virtual oficial de la Universidad Francisco Gavidia (UFG) en El Salvador.

Tu principal misión es brindar información precisa, clara y completa exclusivamente sobre la UFG a estudiantes, aspirantes y visitantes. Responde siempre en español.

ANÁLISIS DE LA CONSULTA DEL USUARIO:
- Tipo detectado: {query_type.upper()}
- Relevancia: {relevance_score:.2f}

INFORMACIÓN DE CONTEXTO DE LA UFG (solo utiliza ESTA información para responder):
{relevant_context}

---
**REGLAS Y FORMATO DE RESPUESTA CRÍTICOS (¡DEBES SEGUIRLOS SIEMPRE!):**

1.  **PROHIBIDO USAR ASTERISCOS (*) O NUMERALES (#):** Nunca uses estos símbolos para negritas, cursivas, títulos, listas o cualquier otro formato.
2.  **FORMATO DE LISTAS OBLIGATORIO:**
    -   Usa SOLO números seguidos de un punto (1., 2., 3., ...) o guiones seguidos de un espacio (-) para los elementos.
    -   Cada elemento de una lista debe ir en una línea separada.
    -   SIEMPRE usa saltos de línea (\\n) entre cada elemento para una mejor legibilidad.
    -   Ejemplo correcto de lista:
        1.  Primera opción
        2.  Segunda opción
        3.  Tercera opción
3.  **LENGUAJE Y TERMINOLOGÍA ESPECÍFICA:**
    -   Utiliza siempre "ciclo" o "ciclos" en lugar de "periodo" o "semestre".
    -   **NO hagas referencias, comparaciones, ni menciones otras universidades o instituciones educativas.** Esto es fundamental.
    -   Nunca digas que otras universidades ofrecen lo mismo.
    -   SIEMPRE prioriza "Ingeniería en Software" sobre "Ingeniería en Sistemas" si ambas opciones aparecen y solo una debe ser mencionada. Si solo una está en el contexto, menciona esa.
4.  **RESTRICCIONES DE CONTENIDO:**
    -   Responde basándote *ÚNICAMENTE* en la información proporcionada en la sección "INFORMACIÓN DE CONTEXTO DE LA UFG". No uses conocimiento general ni información externa.
    -   Si la información sobre una carrera específica (o cualquier otro dato) *no está* en el contexto proporcionado, simplemente afirma que "Esa carrera no está disponible en la UFG" o "No tengo información detallada sobre eso en este momento" y *no ofrezcas explicaciones adicionales ni sugerencias de contacto a menos que sea el tipo de consulta 'contact' o 'pricing' y la información esté ausente.*
    -   **NO uses frases como "bienvenido" en cada respuesta.**
    -   Sé concreto, directo y específico en tus respuestas, evitando ambigüedades o información irrelevante.

---

**INSTRUCCIONES ESPECÍFICAS SEGÚN EL TIPO DE CONSULTA DETECTADO ({query_type.upper()}):**

{get_specific_instructions(query_type)}

---

Consulta del usuario: {request.prompt}
"""

            # Preparar payload para Gemini
            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {
                                "text": f"{system_instruction}\n\nConsulta del usuario: {request.prompt}"
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                    "candidateCount": 1,
                    "stopSequences": []
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }

            headers = {
                "Content-Type": "application/json"
            }

            full_response = ""
            max_retries = 3
            retry_delay = 2  # segundos
            
            for attempt in range(max_retries):
                try:
                    print(f"🤖 Enviando consulta a Gemini 1.5... (Intento {attempt + 1}/{max_retries})")
                    
                    response = requests.post(
                        GEMINI_API_URL,
                        headers=headers,
                        json=payload,
                        timeout=30,
                        stream=True # Habilitar streaming para obtener chunks
                    )
                
                    if response.status_code == 200:
                        for chunk in response.iter_content(chunk_size=None): # Leer todo el chunk, o puedes iterar por líneas si la API lo soporta
                            if chunk:
                                try:
                                    # Intentar decodificar el chunk como JSON para manejar streaming de Gemini
                                    # Gemini suele enviar JSON Line (cada línea es un JSON) o un JSON completo.
                                    # Dependiendo de cómo la API Gemini envía los chunks, esto podría necesitar ajuste.
                                    # Para simplificar y dado que estamos construyendo full_response,
                                    # asumiremos que cada chunk puede contener parte de la respuesta.
                                    data = json.loads(chunk.decode('utf-8'))
                                    
                                    if "candidates" in data and len(data["candidates"]) > 0:
                                        candidate = data["candidates"][0]
                                        if "content" in candidate and "parts" in candidate["content"]:
                                            for part in candidate["content"]["parts"]:
                                                if "text" in part:
                                                    text_content = part["text"]
                                                    full_response += text_content
                                                    
                                                    # Emitir el texto directamente si deseas un streaming más rápido
                                                    yield text_content
                                                    time.sleep(0.01) # Pequeña pausa para simular el streaming
                                    
                                except json.JSONDecodeError:
                                    # Si no es un JSON completo, podría ser un chunk de texto plano o una parte del JSON.
                                    # Para una API que no envía JSON Lines, esto es más complejo.
                                    # Por ahora, simplemente intentaremos decodificar como texto y emitirlo.
                                    # Esto es una simplificación y puede no ser robusto para todas las APIs de streaming.
                                    text_content = chunk.decode('utf-8')
                                    full_response += text_content
                                    yield text_content
                                    time.sleep(0.01)

                        # Si llegamos aquí, la respuesta fue exitosa
                        break
                    
                    elif response.status_code == 503 or response.status_code == 429:
                        # Errores de sobrecarga o límite de tasa
                        error_detail = ""
                        try:
                            error_json = response.json()
                            error_detail = error_json.get('error', {}).get('message', 'Servidor sobrecargado')
                        except:
                            error_detail = f"Status {response.status_code} - Servidor sobrecargado"
                        
                        print(f"⚠️ Intento {attempt + 1}: {error_detail}")
                        
                        if attempt < max_retries - 1:
                            print(f"🔄 Reintentando en {retry_delay} segundos...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Backoff exponencial
                            continue
                        else:
                            error_msg = f"Error: La API de Gemini está sobrecargada. Intenta de nuevo en unos minutos. ({error_detail})"
                            print(f"❌ {error_msg}")
                            yield error_msg
                            return
                    
                    else:
                        error_detail = ""
                        try:
                            error_json = response.json()
                            error_detail = f" - {error_json.get('error', {}).get('message', 'Error desconocido')}"
                        except:
                            error_detail = f" - Status: {response.status_code}"
                        
                        error_msg = f"Error en la API de Gemini{error_detail}"
                        print(f"❌ {error_msg}")
                        
                        if attempt == max_retries - 1:
                            yield error_msg
                            return
                
                except requests.exceptions.Timeout:
                    error_msg = "Error: Timeout en la conexión con Gemini. Intenta de nuevo."
                    print(f"❌ {error_msg}")
                    if attempt == max_retries - 1:
                        chat_memory.append({"role": "assistant", "content": error_msg})
                        yield error_msg
                        return
                    else:
                        print(f"🔄 Reintentando en {retry_delay} segundos...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                        
                except Exception as e:
                    error_msg = f"Error inesperado con Gemini: {str(e)}"
                    print(f"❌ {error_msg}")
                    if attempt == max_retries - 1:
                        chat_memory.append({"role": "assistant", "content": error_msg})
                        yield error_msg
                        return
                    else:
                        print(f"🔄 Reintentando en {retry_delay} segundos...")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue

            # Agregar la respuesta completa a la memoria
            if full_response:
                chat_memory.append({"role": "assistant", "content": full_response})
                print(f"✅ Respuesta de Gemini generada: {len(full_response)} caracteres")

        # Retornar la respuesta como stream
        return StreamingResponse(stream_response(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear-memory")
async def clear_memory(request: dict):
    """Endpoint para limpiar la memoria del chat (opcional para compatibilidad)"""
    try:
        # En este servidor simple, no manejamos memoria persistente por sesión
        # Simplemente limpiamos la memoria global
        global chat_memory
        chat_memory = []
        return {"status": "success", "message": "Memoria limpiada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)