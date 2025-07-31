// Referencia a elementos HTML
const promptInput = document.querySelector("#prompt");
const chatContainer = document.querySelector(".chat-container");
const submitBtn = document.querySelector("#submit");
const closeBtn = document.querySelector("#close-chat");

// Pantalla de carga
const globalLoader = document.getElementById('global-loader');
const mainContent = document.querySelector('.main-content');

// Función para ocultar la pantalla de carga
function hideLoader() {
    document.body.style.overflow = 'hidden';

    setTimeout(() => {
        globalLoader.classList.add('fade-out');
        mainContent.classList.add('loaded');

        globalLoader.addEventListener('transitionend', function handler() {
            if (globalLoader.classList.contains('fade-out')) {
                globalLoader.style.display = 'none';
                document.body.style.overflow = '';
                globalLoader.removeEventListener('transitionend', handler);
            }
        });
    }, 3000);
}

let abortController = new AbortController();

// ID de sesión único
const sessionId = Date.now().toString() + Math.random().toString(36).substring(2, 11);

let user = {
    data: null
};

let isGenerating = false;
let shouldStopWriting = false;

// Función para generar respuesta
async function generateResponse(iaChatBox, userMessage) {
    abortController = new AbortController();
    const signal = abortController.signal;
    const aiChatArea = iaChatBox.querySelector(".ai-chat-area");
    aiChatArea.classList.add("typing", "fade-in");

    const cursor = document.createElement("span");
    cursor.classList.add("typing-cursor");

    shouldStopWriting = false;

    try {
        const response = await fetch("http://localhost:8001/api/mistral", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: userMessage, session_id: sessionId }),
            signal
        });

        if (!response.body || !response.ok) {
            throw new Error(`Error del servidor: ${response.status} ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let firstChunk = true;

        while (true) {
            if (shouldStopWriting) break;

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
                if (shouldStopWriting) break;

                const element = char === "\n"
                    ? document.createElement("br")
                    : Object.assign(document.createElement("span"), {
                        textContent: char,
                        className: "fade-letter"
                    });

                aiChatArea.appendChild(element);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                await new Promise(resolve => setTimeout(resolve, 7));
            }
            aiChatArea.appendChild(cursor);
        }

        if (cursor.parentNode) cursor.remove();
        aiChatArea.classList.remove("typing");

        if (shouldStopWriting) {
            aiChatArea.innerHTML += "<p>Respuesta detenida por el usuario.</p>";
        }

    } catch (error) {
        const currentLoadGif = aiChatArea.querySelector(".load");
        if (currentLoadGif) currentLoadGif.remove();

        if (error.name === 'AbortError') {
            console.log("Cancelado por el usuario.");
            aiChatArea.innerHTML += "<p>Respuesta detenida por el usuario.</p>";
        } else {
            console.error("Error:", error);
            aiChatArea.innerHTML += "<p>Error al conectar con el servidor.</p>";
        }

        aiChatArea.classList.remove("typing");

    } finally {
        isGenerating = false;
        updateSubmitButton(false);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Limpiar memoria del servidor
async function clearServerMemory() {
    try {
        const response = await fetch("http://localhost:8001/api/clear-memory", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ session_id: sessionId })
        });

        if (response.ok) {
            console.log("Memoria del servidor limpiada:", sessionId);
        } else {
            console.error("Error al limpiar memoria:", response.status);
        }
    } catch (error) {
        console.error("Error de red:", error);
    }
}

// Antes de salir de la página
window.addEventListener('beforeunload', () => {
    clearServerMemory();
});

// Crear caja de chat
function createChatBox(html, classes) {
    const div = document.createElement("div");
    div.innerHTML = html;
    div.classList.add(classes);
    return div;
}

// Manejar respuesta del usuario
function handleChatResponse(message) {
    if (!message || message.trim() === "") return;

    if (isGenerating) {
        abortController.abort();
        console.log("Cancelando generación por usuario.");
        return;
    }

    isGenerating = true;
    updateSubmitButton(true);
    user.data = message;

    const userHtml = `
        <img src="imagenes/user.png" alt="Usuario" id="UserImagen" width="50">
        <div class="user-chat-area">${user.data}</div>`;
    promptInput.value = "";

    const userBox = createChatBox(userHtml, "user-chat-box");
    userBox.style.display = "block";
    chatContainer.appendChild(userBox);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    setTimeout(() => {
        const aiHtml = `
            <img src="imagenes/ia.png" alt="IA" id="AiImagen" width="50">
            <div class="ai-chat-area">
                <img src="imagenes/load.gif" alt="Cargando" class="load" width="40">
            </div>`;

        const iaBox = createChatBox(aiHtml, "ai-chat-box");
        chatContainer.appendChild(iaBox);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        generateResponse(iaBox, message);
    }, 800);
}

// Actualizar botón Enviar/Parar
function updateSubmitButton(isGeneratingResponse) {
    const img = submitBtn.querySelector("img");
    promptInput.disabled = isGeneratingResponse;
    submitBtn.disabled = false;

    if (isGeneratingResponse) {
        img.src = "imagenes/cancelar.png";
        img.alt = "Parar";
        submitBtn.title = "Parar generación";
        submitBtn.classList.add("stop-button");
    } else {
        img.src = "imagenes/enviar(1).png";
        img.alt = "Enviar";
        submitBtn.title = "Enviar mensaje";
        submitBtn.classList.remove("stop-button");
        promptInput.focus();
    }
}

// Cuando se carga la página
window.addEventListener('load', () => {
    clearServerMemory();
    hideLoader();
});

// DOM cargado
document.addEventListener('DOMContentLoaded', () => {
    promptInput.addEventListener("keydown", e => {
        if (e.key === "Enter" && !isGenerating && promptInput.value.trim()) {
            handleChatResponse(promptInput.value.trim());
        }
    });

    submitBtn.addEventListener("click", () => {
        if (isGenerating) {
            abortController.abort();
            shouldStopWriting = true;
            updateSubmitButton(false);
        } else if (promptInput.value.trim()) {
            handleChatResponse(promptInput.value.trim());
        }
    });

    closeBtn.addEventListener("click", () => {
        document.cookie = "jwt=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        window.location.replace("/");
    });

    const clearBtn = document.querySelector("#clear");
    if (clearBtn) {
        clearBtn.addEventListener("click", async () => {
            if (isGenerating) {
                abortController.abort();
                await new Promise(resolve => setTimeout(resolve, 100));
            } else {
                console.log("No hay generación activa.");
                // chatContainer.innerHTML = ''; // Descomenta si deseas limpiar mensajes
            }
        });
    }

    // Modal de información
    const infoButton = document.getElementById('info-button');
    const infoModal = document.getElementById('info-modal');
    const closeModal = document.getElementById('close-modal');

    if (infoButton) {
        infoButton.addEventListener('click', () => {
            infoModal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        });
    }

    if (closeModal) {
        closeModal.addEventListener('click', () => {
            infoModal.style.display = 'none';
            document.body.style.overflow = '';
        });
    }

    if (infoModal) {
        infoModal.addEventListener('click', (e) => {
            if (e.target === infoModal) {
                infoModal.style.display = 'none';
                document.body.style.overflow = '';
            }
        });
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && infoModal.style.display === 'block') {
            infoModal.style.display = 'none';
            document.body.style.overflow = '';
        }
    });
});
