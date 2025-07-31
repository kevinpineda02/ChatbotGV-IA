// Referencia a elementos HTML
const promptInput = document.querySelector("#prompt");
const chatContainer = document.querySelector(".chat-container");
const submitBtn = document.querySelector("#submit");
const closeBtn = document.querySelector("#close-chat");

// Pantalla de carga
const globalLoader = document.getElementById('global-loader');
const mainContent = document.querySelector('.main-content'); // Contenido principal de la página

// Función para ocultar la pantalla de carga
function hideLoader() {
    // Asegurarse de que el body no tenga scroll mientras el loader está activo
    document.body.style.overflow = 'hidden';

    // Inicia la animación de fade-out después de 3 segundos
    setTimeout(() => {
        globalLoader.classList.add('fade-out');
        mainContent.classList.add('loaded'); // Activa la animación del contenido principal

        // Una vez que la transición de opacidad del loader termina
        globalLoader.addEventListener('transitionend', function handler() {
            // Verifica si la clase 'fade-out' sigue presente para asegurar que la transición ha finalizado
            if (globalLoader.classList.contains('fade-out')) {
                globalLoader.style.display = 'none'; // Oculta completamente el loader
                document.body.style.overflow = ''; // Restaura el scroll en el body
                globalLoader.removeEventListener('transitionend', handler); // Limpia el listener para evitar duplicados
            }
        });
    }, 3000); // 3 segundos de pantalla de carga
}

// AbortController para cancelar la solicitud fetch
let abortController = new AbortController();

// Generar un ID de sesión único para este usuario
const sessionId = Date.now().toString() + Math.random().toString(36).substr(2, 9);

// Usuario (la estructura de 'user' podría ser más robusta si se manejan perfiles)
let user = {
    data: null
};

let isGenerating = false; // Bandera para controlar si la IA está generando una respuesta
let shouldStopWriting = false; // Nueva bandera global

// Función para generar respuesta desde el backend con animaciones de escritura
async function generateResponse(iaChatBox, userMessage) {
    abortController = new AbortController();
    const signal = abortController.signal;
    const aiChatArea = iaChatBox.querySelector(".ai-chat-area");
    aiChatArea.classList.add("typing", "fade-in");
    const cursor = document.createElement("span");
    cursor.classList.add("typing-cursor");

    shouldStopWriting = false; // Reinicia la bandera al empezar

    try {
        const response = await fetch("http://localhost:8001/api/mistral", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                prompt: userMessage,
                session_id: sessionId
            }),
            signal
        });

        if (!response.body || !response.ok) {
            throw new Error(`Error en la respuesta del servidor: ${response.status} ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let firstChunk = true;

        while (true) {
            if (shouldStopWriting) break; // Detiene la escritura inmediatamente
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });

            if (firstChunk && chunk.trim().length > 0) {
                const loadGif = aiChatArea.querySelector(".load");
                if (loadGif) loadGif.remove();
                aiChatArea.innerHTML = '';
                aiChatArea.appendChild(cursor);
                firstChunk = false;
            }

            if (cursor.parentNode) cursor.remove();

            for (let char of chunk) {
                if (shouldStopWriting) break; // Detiene la escritura de letras
                if (char === "\n") {
                    const br = document.createElement("br");
                    aiChatArea.appendChild(br);
                } else {
                    const span = document.createElement("span");
                    span.textContent = char;
                    span.classList.add("fade-letter");
                    aiChatArea.appendChild(span);
                }
                chatContainer.scrollTop = chatContainer.scrollHeight;
                await new Promise(resolve => setTimeout(resolve, 7));
            }
            aiChatArea.appendChild(cursor);
        }

        if (cursor.parentNode) cursor.remove();
        aiChatArea.classList.remove("typing");

        // Si se detuvo por el usuario, muestra mensaje opcional
        if (shouldStopWriting) {
            aiChatArea.innerHTML += "<p>Respuesta detenida por el usuario.</p>";
        }

    } catch (error) {
        const currentLoadGif = aiChatArea.querySelector(".load");
        if (currentLoadGif) currentLoadGif.remove();

        if (error.name === 'AbortError') {
            console.log("Solicitud cancelada por el usuario.");
            aiChatArea.innerHTML += "<p>Respuesta detenida por el usuario.</p>";
        } else {
            console.error("Error en la respuesta de la IA:", error);
            aiChatArea.innerHTML += "<p>Ocurrió un error al conectar con el servidor o al procesar la respuesta.</p>";
        }
        aiChatArea.classList.remove("typing");
    } finally {
        isGenerating = false;
        updateSubmitButton(false);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Función para limpiar la memoria del servidor (mantener conversaciones separadas)
async function clearServerMemory() {
    try {
        const response = await fetch("http://localhost:8001/api/clear-memory", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                session_id: sessionId // Usamos el session_id para limpiar la memoria asociada a esta sesión
            })
        });
        if (response.ok) {
            console.log("Memoria del servidor limpiada para la sesión:", sessionId);
        } else {
            console.error("Error al limpiar memoria del servidor:", response.status, response.statusText);
        }
    } catch (error) {
        console.error("Error de red al limpiar memoria del servidor:", error);
    }
}

// Limpiar memoria cuando se recarga la página o se cierra la pestaña
window.addEventListener('beforeunload', () => {
    // En beforeunload, fetch podría no completarse. Considera usar Navigator.sendBeacon() para asegurar el envío en algunos casos.
    // Sin embargo, para un desarrollo local y un simple cleanup, fetch está bien.
    clearServerMemory();
});

// Función para crear cajas de chat con contenido HTML y clases CSS
function createChatBox(html, classes) {
    const div = document.createElement("div");
    div.innerHTML = html;
    div.classList.add(classes);
    return div;
}

// Función para manejar el envío del mensaje del usuario y la respuesta de la IA
function handleChatResponse(message) {
    // 1. Validación de mensaje vacío
    if (!message || message.trim() === "") {
        console.log("Mensaje vacío, no se envía.");
        return;
    }

    // 2. Control de generación en curso
    if (isGenerating) {
        // Si ya se está generando, el botón de enviar ahora actúa como "cancelar"
        abortController.abort(); // Cancela la solicitud fetch actual
        console.log("Cancelando generación actual por acción del usuario.");
        return; // Sale de la función
    }

    // 3. Iniciar el proceso de generación
    isGenerating = true; // Establece la bandera
    updateSubmitButton(true); // Cambia el botón a "Parar"

    user.data = message; // Guarda el mensaje del usuario
    
    // 4. Mostrar el mensaje del usuario
    const userHtml = `
        <img src="imagenes/user.png" alt="Usuario" id="UserImagen" width="50">
        <div class="user-chat-area">${user.data}</div>`;

    promptInput.value = ""; // Limpia el input
    const userBox = createChatBox(userHtml, "user-chat-box");
    userBox.style.display = "block"; // Asegura que la caja de usuario sea visible
    chatContainer.appendChild(userBox);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll al último mensaje

    // 5. Mostrar la caja de la IA con el GIF de carga
    setTimeout(() => { // Pequeño retardo para que el mensaje del usuario se asiente
        const aiHtml = `
            <img src="imagenes/ia.png" alt="IA" id="AiImagen" width="50">
            <div class="ai-chat-area">
                <img src="imagenes/load.gif" alt="Cargando" class="load" width="40">
            </div>`;

        const iaBox = createChatBox(aiHtml, "ai-chat-box");
        chatContainer.appendChild(iaBox);
        chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll al GIF de carga

        // Inicia la generación de la respuesta de la IA
        generateResponse(iaBox, message);
    }, 800); // Retardo de 800ms antes de mostrar el spinner de la IA
}

// Función para actualizar el estado visual del botón de enviar (Enviar/Parar)
function updateSubmitButton(isGeneratingResponse) {
    const img = submitBtn.querySelector("img");
    promptInput.disabled = isGeneratingResponse;
    submitBtn.disabled = false;

    if (isGeneratingResponse) {
        img.src = "imagenes/cancelar.png";
        img.alt = "Parar";
        submitBtn.title = "Parar generación de respuesta";
        submitBtn.classList.add("stop-button");
    } else {
        img.src = "imagenes/enviar(1).png"; // Cambia al icono correcto
        img.alt = "Enviar";
        submitBtn.title = "Enviar mensaje";
        submitBtn.classList.remove("stop-button");
        promptInput.focus();
    }
}

// EVENT LISTENERS

// Cuando la página se carga completamente:
// 1. Limpia la memoria del servidor.
// 2. Oculta la pantalla de carga.
window.addEventListener('load', () => {
    clearServerMemory();
    hideLoader(); 
});

// Cuando el DOM está completamente cargado, añadir listeners a los elementos
document.addEventListener('DOMContentLoaded', () => {
    // Evento para el input de texto (tecla Enter)
    promptInput.addEventListener("keydown", e => {
        // Solo envía si la tecla es Enter, no se está generando, y el input no está vacío
        if (e.key === "Enter" && !isGenerating && promptInput.value.trim()) {
            handleChatResponse(promptInput.value.trim());
        }
    });

    // Evento para el botón de enviar/parar
    submitBtn.addEventListener("click", () => {
        if (isGenerating) {
            // Detiene tanto la petición como la escritura
            abortController.abort();
            shouldStopWriting = true;
            updateSubmitButton(false); // <-- Añade esta línea para restaurar el icono de enviar
            console.log("Generación de mensaje detenida por el usuario vía botón.");
        } else if (promptInput.value.trim()) {
            handleChatResponse(promptInput.value.trim());
        }
    });

    // Evento para el botón de cerrar chat (limpia cookie y redirige)
    closeBtn.addEventListener("click", () => {
        // Borrar la cookie JWT (si la usas para autenticación/sesión)
        document.cookie = "jwt=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        // Redirigir a la raíz del sitio
        window.location.replace("/");
    });

    // Funcionalidad del botón 'Clear' (asumiendo que #clear es para detener la generación)
    // Si tu botón 'Clear' es para limpiar el *chat* visualmente, necesitaría otra lógica.
    const clearBtn = document.querySelector("#clear");
    if (clearBtn) { // Asegúrate de que el botón #clear exista en tu HTML
        clearBtn.addEventListener("click", async () => {
            if (isGenerating) {
                // Si hay una generación en curso, la detiene
                abortController.abort();
                console.log("Generación de mensaje detenida por el usuario desde el botón 'Clear'.");
                // Pequeño retardo para que la cancelación se procese antes de cualquier otra acción
                await new Promise(resolve => setTimeout(resolve, 100)); 
            } else {
                console.log("No hay generación activa para detener.");
                // Si este botón es para LIMPIAR el chat, aquí iría la lógica para borrar mensajes del DOM
                // Por ejemplo: chatContainer.innerHTML = '';
            }
        });
    }
});

// --- Funcionalidad del Modal de Información ---
document.addEventListener('DOMContentLoaded', function() {
    const infoButton = document.getElementById('info-button');
    const infoModal = document.getElementById('info-modal');
    const closeModal = document.getElementById('close-modal');

    // Abrir modal
    if (infoButton) {
        infoButton.addEventListener('click', function() {
            infoModal.style.display = 'block';
            document.body.style.overflow = 'hidden'; // Prevenir scroll del fondo
        });
    }

    // Cerrar modal al hacer clic en la X
    if (closeModal) {
        closeModal.addEventListener('click', function() {
            infoModal.style.display = 'none';
            document.body.style.overflow = ''; // Restaurar scroll
        });
    }

    // Cerrar modal al hacer clic fuera del contenido
    if (infoModal) {
        infoModal.addEventListener('click', function(e) {
            if (e.target === infoModal) {
                infoModal.style.display = 'none';
                document.body.style.overflow = ''; // Restaurar scroll
            }
        });
    }

    // Cerrar modal con la tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && infoModal.style.display === 'block') {
            infoModal.style.display = 'none';
            document.body.style.overflow = ''; // Restaurar scroll
        }
    });
});
