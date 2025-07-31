import os
import re
from typing import Dict, List

class RAGSystemSimple:
    def __init__(self, txt_folder_path: str):
        """
        Sistema RAG mejorado para búsqueda precisa de contexto.
        
        Args:
            txt_folder_path: Ruta a la carpeta con archivos .txt
        """
        self.txt_folder_path = txt_folder_path
        self.content_by_file: Dict[str, str] = {}
        self.all_content: str = ""
        self.career_file_mapping: Dict[str, str] = {}
        self.instruction_content: str = ""
        self.general_info_content: str = ""
        self._load_all_files()
        self._build_career_file_mapping()

    def _load_all_files(self):
        """Cargar todos los archivos de texto desde la ruta especificada de forma recursiva."""
        print("🔨 Cargando todos los archivos de texto...")
        
        archivos_cargados = 0
        textos = []

        if not os.path.exists(self.txt_folder_path):
            print(f"❌ ERROR: La ruta de documentos no existe: {self.txt_folder_path}")
            return

        for root, _, files in os.walk(self.txt_folder_path):
            for filename in files:
                if filename.endswith('.txt'):
                    file_path = os.path.join(root, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().strip()
                            if content:
                                # Clave: ruta relativa normalizada, ej: "carreras/psicologia"
                                relative_path = os.path.relpath(file_path, self.txt_folder_path)
                                key_for_dict = relative_path.replace(".txt", "").lower().replace("\\", "/")
                                
                                self.content_by_file[key_for_dict] = content
                                
                                # Identificar archivos especiales
                                filename_lower = filename.lower()
                                if any(keyword in filename_lower for keyword in ['instruccion', 'instruction', 'prompt']):
                                    self.instruction_content = content
                                    print(f"📋 Archivo de instrucciones detectado: {relative_path}")
                                elif any(keyword in filename_lower for keyword in ['informacion', 'general', 'info']):
                                    self.general_info_content = content
                                    print(f"ℹ️ Archivo de información general detectado: {relative_path}")
                                
                                textos.append(content)
                                archivos_cargados += 1
                                print(f"✅ Cargado: {relative_path} ({len(content)} caracteres)")
                            else:
                                print(f"⚠️  Archivo vacío: {file_path}")
                    except Exception as e:
                        print(f"❌ Error cargando {file_path}: {e}")
        
        self.all_content = "\n\n".join(textos)
        print(f"🎯 Sistema RAG Simple cargado: {archivos_cargados} archivos, {len(self.all_content)} caracteres totales")
        
        # Verificar archivos especiales
        if self.instruction_content:
            print(f"📋 Instrucciones cargadas: {len(self.instruction_content)} caracteres")
        else:
            print("⚠️ No se encontró archivo de instrucciones")
            
        if self.general_info_content:
            print(f"ℹ️ Información general cargada: {len(self.general_info_content)} caracteres")
        else:
            print("⚠️ No se encontró archivo de información general")

    def _build_career_file_mapping(self):
        """Construye el mapeo de palabras clave de carrera a claves de archivo."""
        self.career_file_mapping = {
            # Psicología
            "psicologia": "carreras/psicologia",
            "licenciatura en psicologia": "carreras/psicologia",
            
            # Derecho/Leyes
            "leyes": "carreras/leyes",
            "derecho": "carreras/leyes",
            "ciencias juridicas": "carreras/leyes",
            "licenciatura en ciencias juridicas": "carreras/leyes",
            
            # Ingenierías
            "ingenieria en software": "carreras/software",
            "ingenieria en diseño y desarrollo de software": "carreras/software",
            "diseño y desarrollo de software": "carreras/software",
            "desarrollo de software": "carreras/software",
            "software": "carreras/software",
            "ingenieria industrial": "carreras/industrial",
            "industrial": "carreras/industrial",
            "ingenieria en diseño y desarrollo": "carreras/diseñoydesarrollo",
            "diseño y desarrollo": "carreras/diseñoydesarrollo",
            "ingenieria en inteligencia": "carreras/inteligencia",
            "ingenieria en inteligencia artificial": "carreras/roboticaia",
            "ingenieria en inteligencia artificial y robotica": "carreras/roboticaia",
            "inteligencia artificial y robotica": "carreras/roboticaia",
            "inteligencia artificial": "carreras/roboticaia",
            "robotica": "carreras/roboticaia",
            "inteligencia": "carreras/inteligencia",
            "ingenieria en sistemas": "carreras/sistemas",
            "sistemas": "carreras/sistemas",
            "ingenieria en telecomunicaciones": "carreras/telecomunicaciones",
            "telecomunicaciones": "carreras/telecomunicaciones",
            "ingenieria en control electrico": "carreras/controlelectrico",
            "control electrico": "carreras/controlelectrico",
            "ingenieria en robotica": "carreras/roboticaia",
            "robotica y ia": "carreras/roboticaia",
            "ingenieria en videojuegos": "carreras/videojuegos",
            "ingeniería en videojuegos": "carreras/videojuegos",
            "desarrollo de videojuegos": "carreras/videojuegos",
            
            # Licenciaturas
            "administracion de empresas": "carreras/administracion",
            "administracion": "carreras/administracion",
            "licenciatura en administracion": "carreras/administracion",
            "administracion turistica": "carreras/administracionturistica",
            "animacion digital": "carreras/animaciondigital",
            "atencion a la primera infancia": "carreras/atencioninfancia",
            "ciencias politicas": "carreras/cienciaspoliticas",
            "comunicacion corporativa": "carreras/comunicacionescorporativa",
            "comunicaciones corporativas": "carreras/comunicacionescorporativa",
            "contaduria publica": "carreras/contaduria",
            "contaduria": "carreras/contaduria",
            "diseño de modas": "carreras/diseñomoda",
            "diseño publicitario": "carreras/diseñopublicitario",
            "diseño web": "carreras/diseñoweb",
            "economia internacional": "carreras/economiainternacional",
            "gestion estrategica de hoteles": "carreras/gestionestrategicahoteles",
            "mercadotecnia y publicidad": "carreras/mercadotecnia",
            "mercadotecnia": "carreras/mercadotecnia",
            "relaciones internacionales": "carreras/relacionesinter",
            "relaciones publicas": "carreras/relacionespublicas",
            "sistemas informaticos": "carreras/licinformatica",
            "licenciatura en informatica": "carreras/licinformatica",
            "sistemas de computacion administrativa": "carreras/licsistemas",
            "trabajo social": "carreras/social",
            "licenciatura en trabajo social": "carreras/social",
            "criminologia": "carreras/criminologia",
            "licenciatura en criminologia": "carreras/criminologia",
            "idioma ingles": "carreras/ingles",
            "ingles": "carreras/ingles",
            "licenciatura en idioma ingles": "carreras/ingles",
            "videojuegos": "carreras/videojuegos",
            "desarrollo de videojuegos": "carreras/videojuegos",
            
            # Técnicos
            "tecnico en contaduria": "carreras/tecconta",
            "tecnico en animacion": "carreras/tecanimacion",
            "tecnico en decoracion": "carreras/tecdecoracion",
            "tecnico en ventas": "carreras/tecventas",
            "tecnico en sistemas": "carreras/tecsistemas",
            "tecnico en restaurantes": "carreras/tecrestaurante",
            "tecnico en turismo": "carreras/tecturismo",
            "tecnico en publicidad": "carreras/tecpublicidad"
        }

    def _find_relevant_documents(self, query: str, top_n: int = 3) -> str:
        """Encuentra todos los documentos relevantes para una consulta general (sin límite de cantidad)."""
        query_words = set(re.findall(r'\w+', query.lower()))
        if not query_words:
            return ""

        scores = {}
        all_careers_content = []
        for file_key, content in self.content_by_file.items():
            if file_key.startswith("carreras/"):
                all_careers_content.append(content)
        # Esto devuelve todo el contenido de carreras, lo que podría ser muy grande.
        # Si la intención es un "top_n" real, se necesitaría un cálculo de score más sofisticado aquí.
        # Por ahora, se mantiene como está, que concatena todo el contenido de carreras.
        return "\n\n---\n\n".join(all_careers_content)

    def _detect_contact_query(self, query: str) -> bool:
        """Detecta si la consulta es sobre información de contacto."""
        contact_keywords = [
            'contacto', 'telefono', 'teléfono', 'email', 'correo', 'direccion', 'dirección',
            'ubicacion', 'ubicación', 'donde esta', 'dónde está', 'como llegar', 'cómo llegar',
            'horarios', 'atencion', 'atención', 'sede', 'campus', 'sucursal'
        ]
        return any(keyword in query.lower() for keyword in contact_keywords)

    def _detect_admission_query(self, query: str) -> bool:
        """Detecta si la consulta es sobre requisitos de admisión."""
        admission_keywords = [
            'requisitos', 'admision', 'admisión', 'inscripcion', 'inscripción', 
            'matricula', 'matrícula', 'costos', 'precio', 'cuota', 'mensualidad',
            'como ingresar', 'cómo ingresar', 'que necesito', 'qué necesito',
            'documentos', 'papeles', 'solicitud'
        ]
        return any(keyword in query.lower() for keyword in admission_keywords)

    def _get_all_careers_by_type(self, career_type: str = None) -> str:
        """
        Obtiene una lista formateada de carreras, opcionalmente filtrada por tipo.
        Solo muestra ingenierías reales cuando se pide ingenierías.
        """
        career_list = []
        for key, content in self.content_by_file.items():
            if key.startswith("carreras/"):
                career_name = None
                
                # Casos especiales para archivos conocidos primero
                if key == "carreras/software":
                    career_name = "Ingeniería en Diseño y Desarrollo de Software"
                elif key == "carreras/roboticaia":
                    career_name = "Ingeniería en Inteligencia Artificial y Robótica"
                elif key == "carreras/sistemas":
                    career_name = "Ingeniería en Sistemas y Computación"
                elif key == "carreras/telecomunicaciones":
                    career_name = "Ingeniería en Telecomunicaciones"
                elif key == "carreras/controlelectrico":
                    career_name = "Ingeniería en Control Eléctrico"
                elif key == "carreras/industrial":
                    career_name = "Ingeniería Industrial"
                elif key == "carreras/videojuegos":
                    career_name = "Ingeniería en Diseño y Desarrollo de Videojuegos"
                elif key == "carreras/psicologia": # Agregado para psicología si tiene un nombre específico
                    career_name = "Licenciatura en Psicología"
                elif key == "carreras/leyes": # Agregado para leyes
                    career_name = "Licenciatura en Ciencias Jurídicas"
                else:
                    # Usar regex para otros casos genéricos
                    # Busca el nombre completo de la carrera (ej. "LICENCIATURA EN X" o "INGENIERÍA EN Y")
                    patterns = [
                        r'^(INGENIER[IÍ]A EN\s+.*?)(?:\n|$)',
                        r'^(LICENCIATURA EN\s+.*?)(?:\n|$)',
                        r'^(T[EÉ]CNICO EN\s+.*?)(?:\n|$)',
                        r'^(?:NGENIERÍA EN)\s+(.+)', # Para casos como "NGENIERÍA" sin la I (posible error tipográfico)
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
                        if match:
                            # Asegúrate de capturar el nombre completo que coincide con el patrón
                            career_name = match.group(1).strip()
                            # Limpiar espacios extra y mayúsculas/minúsculas inconsistentes
                            career_name = re.sub(r'\s+', ' ', career_name).strip()
                            break
                
                if career_name:
                    # Normalizar el nombre para consistencia antes de la comparación
                    full_name_lower = career_name.lower()

                    # Filtrar por tipo si se especifica
                    if career_type:
                        if career_type.lower() == "ingenieria":
                            if not (full_name_lower.startswith("ingeniería en") or full_name_lower.startswith("ingeniería industrial")):
                                continue
                        elif career_type.lower() == "licenciatura":
                            if not full_name_lower.startswith("licenciatura en"):
                                continue
                        elif career_type.lower() == "tecnico":
                            if not (full_name_lower.startswith("técnico en") or full_name_lower.startswith("tecnico en")):
                                continue
                        # Si career_type es genérico (ej. "videojuegos"), se comprueba si está en el nombre
                        elif career_type.lower() not in full_name_lower:
                            continue
                    
                    # Extraer modalidad
                    modalidad_match = re.search(r'MODALIDAD\s+(PRESENCIAL|SEMIPRESENCIAL)', content, re.IGNORECASE)
                    modalidad = f"({modalidad_match.group(1).title()})" if modalidad_match else ""
                    career_list.append(f"{career_name} {modalidad}".strip())

        if not career_list:
            return f"No se encontraron carreras para el tipo '{career_type}'."

        # Eliminar duplicados y ordenar
        career_list = sorted(list(set(career_list)))
        
        # Título con mejor formato
        if career_type:
            if career_type.lower() == "ingenieria":
                title = "INGENIERÍAS DISPONIBLES EN LA UNIVERSIDAD FRANCISCO GAVIDIA (UFG)"
            elif career_type.lower() == "licenciatura":
                title = "LICENCIATURAS DISPONIBLES EN LA UNIVERSIDAD FRANCISCO GAVIDIA (UFG)"
            elif career_type.lower() == "tecnico":
                title = "TÉCNICOS DISPONIBLES EN LA UNIVERSIDAD FRANCISCO GAVIDIA (UFG)"
            else:
                # Caso para tipos genéricos como "videojuegos"
                title = f"CARRERAS DE {career_type.upper()} DISPONIBLES EN LA UNIVERSIDAD FRANCISCO GAVIDIA (UFG)"
        else:
            title = "TODAS LAS CARRERAS DISPONIBLES EN LA UNIVERSIDAD FRANCISCO GAVIDIA (UFG)"
        
        result = f"## {title}\n\n"
        
        # Agrupar por tipo para mejor organización
        ingenierias = []
        licenciaturas = []
        tecnicos = []
        others = [] # Para carreras que no encajan en las categorías principales

        for career in career_list:
            career_lower = career.lower()
            if career_lower.startswith("ingeniería en") or career_lower.startswith("ingeniería industrial"):
                ingenierias.append(career)
            elif career_lower.startswith("licenciatura en"):
                licenciaturas.append(career)
            elif career_lower.startswith("técnico en") or career_lower.startswith("tecnico en"):
                tecnicos.append(career)
            else:
                # Si no empieza con los prefijos comunes, agrégalo a "otros"
                others.append(career)
        
        # Si es una consulta específica por tipo, mostrar solo ese tipo
        if career_type:
            if career_type.lower() == "ingenieria" and ingenierias:
                for i, career in enumerate(ingenierias, 1):
                    result += f"{i}. {career}\n" # Se eliminó el doble salto de línea aquí
            elif career_type.lower() == "licenciatura" and licenciaturas:
                for i, career in enumerate(licenciaturas, 1):
                    result += f"{i}. {career}\n" # Se eliminó el doble salto de línea aquí
            elif career_type.lower() == "tecnico" and tecnicos:
                for i, career in enumerate(tecnicos, 1):
                    result += f"{i}. {career}\n" # Se eliminó el doble salto de línea aquí
            elif others: # Para tipos genéricos si hay coincidencias en 'others'
                 for i, career in enumerate(others, 1):
                    result += f"{i}. {career}\n"
        else:
            # Si es consulta general, mostrar por categorías
            if ingenierias:
                result += f"\n### INGENIERÍAS ({len(ingenierias)} disponibles):\n"
                for i, career in enumerate(ingenierias, 1):
                    result += f"{i}. {career}\n" # Se eliminó el doble salto de línea aquí
            
            if licenciaturas:
                result += f"\n### LICENCIATURAS ({len(licenciaturas)} disponibles):\n"
                for i, career in enumerate(licenciaturas, 1):
                    result += f"{i}. {career}\n" # Se eliminó el doble salto de línea aquí
            
            if tecnicos:
                result += f"\n### TÉCNICOS ({len(tecnicos)} disponibles):\n"
                for i, career in enumerate(tecnicos, 1):
                    result += f"{i}. {career}\n" # Se eliminó el doble salto de línea aquí

            if others: # Si hay otras carreras que no encajan en las categorías anteriores
                result += f"\n### OTRAS CARRERAS ({len(others)} disponibles):\n"
                for i, career in enumerate(others, 1):
                    result += f"{i}. {career}\n"
        
        # Ajuste final para eliminar el último salto de línea extra si lo hay
        result = result.strip()
        result += f"\n\n**Total de carreras: {len(career_list)}**"
        return result
    
    def get_context_for_query(self, query: str, max_context_length: int = 60000) -> str:
        """
        Obtiene contexto relevante para una consulta, optimizado para precisión.
        Devuelve un contexto estructurado en Markdown.
        """
        query_lower = query.lower()
        print(f"\n🔍 Analizando consulta: '{query}'")
        
        # 0. Detección de consulta de precios (general o por carrera)
        price_keywords = [
            'precio', 'precios', 'cuota', 'mensualidad', 'arancel', 'aranceles', 'costo', 'costos', 'matrícula', 'matricula', 'inscripción', 'inscripcion', 'pago', 'pagos', 'tarifa', 'tarifas'
        ]
        carrera_keywords = list(self.career_file_mapping.keys())
        if any(word in query_lower for word in price_keywords):
            # Buscar si la consulta menciona una carrera específica
            carrera_detectada = None
            for keyword, file_key in self.career_file_mapping.items():
                if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                    carrera_detectada = keyword
                    break

            precios_key = 'precios/precios'  # clave normalizada para Precios.txt
            if precios_key in self.content_by_file:
                precios_txt = self.content_by_file[precios_key]
                # Si se detectó una carrera, buscar sección específica
                if carrera_detectada:
                    # Buscar sección de la carrera en el texto de precios
                    pattern = re.compile(rf"{carrera_detectada}.*?(?=\n\w|$)", re.IGNORECASE | re.DOTALL)
                    match = pattern.search(precios_txt)
                    if match:
                        precios_carrera = match.group(0).strip()
                        if precios_carrera:
                            contacto = "\n\n---\n\nContacto UFG:\n- Teléfono: 2209-2834\n- Email: contactcenter@ufg.edu.sv\n- Web: https://www.ufg.edu.sv/"
                            print(f"💲 Consulta de precios detectada para carrera: {carrera_detectada}")
                            precios_section = f"## Precios y Aranceles para {carrera_detectada.title()}\n\n{precios_carrera}"
                            return f"{precios_section}{contacto}"[:max_context_length]
                    # Si no se encuentra sección específica, mostrar mensaje informativo
                    print(f"⚠️ No se encontró sección de precios para la carrera: {carrera_detectada}")
                    contacto = "\n\n---\n\nContacto UFG:\n- Teléfono: 2209-2834\n- Email: contactcenter@ufg.edu.sv\n- Web: https://www.ufg.edu.sv/"
                    return f"No se encontró información de precios específica para la carrera '{carrera_detectada.title()}'. {contacto}"
                else:
                    # Consulta general de precios
                    contacto = "\n\n---\n\nContacto UFG:\n- Teléfono: 2209-2834\n- Email: contactcenter@ufg.edu.sv\n- Web: https://www.ufg.edu.sv/"
                    print("💲 Consulta de precios general detectada. Devolviendo información de Precios.txt")
                    precios_section = f"## Precios y Aranceles UFG\n\n{precios_txt}"
                    return f"{precios_section}{contacto}"[:max_context_length]
            else:
                print("⚠️ No se encontró archivo de precios.")
                # Si no hay archivo de precios, sigue con el flujo normal

        # 1. Detección PRIORITARIA de carreras específicas (antes que listados)
        found_careers = set()
        for keyword, file_key in self.career_file_mapping.items():
            if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
                found_careers.add(file_key)

        # Si encontramos carreras específicas, devolver su información
        if found_careers:
            context_parts = []
            print(f"📋 Detectada consulta específica para carreras: {', '.join(found_careers)}")
            for key in found_careers:
                if key in self.content_by_file:
                    context_parts.append(self.content_by_file[key])
            if context_parts:
                contacto = "\n\n---\n\nContacto UFG:\n- Teléfono: 2209-2834\n- Email: contactcenter@ufg.edu.sv\n- Web: https://www.ufg.edu.sv/"
                context = f"## Información de Carrera Específica\n\n" + "\n\n---\n\n".join(context_parts) + contacto
                print(f"  - Devolviendo información específica de carrera ({len(context)} caracteres).")
                return context[:max_context_length]

        # 2. Detección de PENSUM o materias para carreras específicas
        specific_query_patterns = r'\b(pensum|perfil|materias|asignaturas|plan\s+de\s+estudio|ciclos|duraci(o|ó)n|malla\s+curricular)\b'
        is_specific_query = re.search(specific_query_patterns, query_lower)

        if is_specific_query and found_careers: # Usamos found_careers que ya detectamos arriba
            context_parts = []
            print(f"📋 Detectada consulta de PENSUM/PERFIL para: {', '.join(found_careers)}")
            for key in found_careers:
                if key in self.content_by_file:
                    context_parts.append(self.content_by_file[key])
            if context_parts:
                # Siempre agrega contactos al final
                contacto = "\n\n---\n\nContacto UFG:\n- Teléfono: 2209-2834\n- Email: contactcenter@ufg.edu.sv\n- Web: https://www.ufg.edu.sv/"
                context = f"## Contexto Específico de Carrera\n\n" + "\n\n---\n\n".join(context_parts) + contacto
                print(f"  - Devolviendo contexto específico de carrera ({len(context)} caracteres).")
                return context[:max_context_length]

        # 3. Detección de PENSUM para todas las carreras (si la consulta lo pide explícitamente)
        is_all_careers_query = re.search(r'\btodas\s+las\s+carreras\b', query_lower)
        if is_specific_query and is_all_careers_query:
            print("🎯 Detectada consulta de PENSUM/PERFIL para TODAS las carreras.")
            all_career_contexts = []
            for key, content in self.content_by_file.items():
                if key.startswith("carreras/"):
                    all_career_contexts.append(content)
            if all_career_contexts:
                contacto = "\n\n---\n\nContacto UFG:\n- Teléfono: 2209-2834\n- Email: contactcenter@ufg.edu.sv\n- Web: https://www.ufg.edu.sv/"
                context = f"## Contexto de Todas las Carreras\n\n" + "\n\n---\n\n".join(all_career_contexts) + contacto
                print(f"  - Devolviendo contexto de todas las carreras ({len(context)} caracteres).")
                return context[:max_context_length]

        # 4. Detección de listados generales (Ingenierías, Licenciaturas, Técnicos o Todas)
        list_patterns = {
            'ingenieria': r'\b(todas\s+las\s+)?ingenier(i|í)as?\b',
            'licenciatura': r'\b(todas\s+las\s+)?licenciaturas?\b',
            'tecnico': r'\b(todos\s+los\s+)?t(e|é)cnicos?\b',
            'carrera': r'\b(todas\s+las\s+)?carreras?\b|\bqu(e|é)\s+carreras\s+(hay|tiene|ofrece)\b'
        }
        for list_type_key, pattern in list_patterns.items():
            if re.search(pattern, query_lower):
                print(f"🎯 Detectada consulta de listado: {list_type_key}")
                
                # Pasar el tipo de carrera específico a _get_all_careers_by_type
                # Si es 'carrera', significa "todas"
                career_type_arg = list_type_key if list_type_key != 'carrera' else None
                
                listado = self._get_all_careers_by_type(career_type_arg)
                contacto = "\n\n---\n\nContacto UFG:\n- Teléfono: 2209-2834\n- Email: contactcenter@ufg.edu.sv\n- Web: https://www.ufg.edu.sv/"
                return listado + contacto

        # 5. Detección de consultas de contacto/admisión
        if self._detect_contact_query(query) or self._detect_admission_query(query):
            print("📞 Detectada consulta de contacto/admisión")
            contacto = "Contacto UFG:\n- Teléfono: 2209-2834\n- Email: contactcenter@ufg.edu.sv\n- Web: https://www.ufg.edu.sv/"
            if self.general_info_content:
                return f"## Información General de la UFG\n\n{self.general_info_content}\n\n---\n\n{contacto}"
            else:
                return contacto

        # 6. Para consultas generales que no encajan en las anteriores, usar búsqueda por relevancia
        print(f"🔍 Usando búsqueda por relevancia para consulta general.")
        relevant_context = self._find_relevant_documents(query, top_n=2)

        final_context_parts = []
        if relevant_context:
            final_context_parts.append(f"## Contexto Relevante\n\n{relevant_context}")

        if self.general_info_content:
            final_context_parts.append(f"## Información General de la UFG\n\n{self.general_info_content}")

        # Siempre agrega contactos al final
        contacto = "Contacto UFG:\n- Teléfono: 2209-2834\n- Email: contactcenter@ufg.edu.sv\n- Web: https://www.ufg.edu.sv/"
        final_context_parts.append(contacto)

        final_context = "\n\n".join(final_context_parts)

        # Si no hay contexto relevante y la consulta es específica de carrera pero sin pensum (ej. "ingeniería en software", pero el archivo no tiene pensum claro)
        if not relevant_context and is_specific_query and found_careers:
            carreras = ", ".join([k.split("/")[-1].replace("_", " ").title() for k in found_careers])
            return f"No hay información detallada sobre {carreras} en los documentos proporcionados.\n\n{contacto}"

        if not relevant_context and not found_careers and not self._detect_contact_query(query) and not self._detect_admission_query(query):
            print("  - No se encontraron documentos relevantes para la consulta general. Se devolverá solo contacto.")
            return contacto

        return final_context[:max_context_length]