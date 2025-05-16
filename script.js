// Variables usadas del script
let prompt = document.querySelector("#prompt");
let chatcontainer = document.querySelector(".chat-container");




// Usuario
let user = {
    data: null
};

async function generateResponse(iaChatBox, userMessage) {
    try {
        // Contactenando los Archivos txt
        const archivos = [
            //Instrucciones para la IA
            "txt/Instrucciones.txt",
            //Informacion Sobre la Universidad
            "txt/InformacionGeneral.txt",
            //Carreras
            "txt/Carreras/VideoJuegos.txt",
            "txt/Carreras/Software.txt",
            "txt/Carreras/Industrial.txt",
            "txt/Carreras/Arquitectura.txt",
            "txt/Carreras/ControlElectrico",
            "txt/Carreras/RoboticaIA",
            "txt/Carreras/Sistemas.txt",
            "txt/Carreras/Telecomunicaciones.txt",
            "txt/Carreras/Psicologia.txt",
            "txt/Carreras/Administracion.txt",
            "txt/Carreras/AdministracionTuristica.txt",
            "txt/Carreras/AnimacionDigital.txt",
            "txt/Carreras/AtencionInfancia.txt",
            "txt/Carreras/Leyes.txt",
            "txt/Carreras/CienciasPoliticas.txt",
            "txt/Carreras/ComunicacionesCorporativa.txt",
            "txt/Carreras/Contaduria.txt",
            "txt/Carreras/DiseñoModa.txt",
            "txt/Carreras/DiseñoPublicitario.txt",
            "txt/Carreras/DiseñoWeb.txt",
            "txt/Carreras/EconomiaInternacional.txt",
            "txt/Carreras/GestionEstrategicaHoteles.txt",
            "txt/Carreras/Mercadotecnia.txt",
            "txt/Carreras/RelacionesInter.txt",
            "txt/Carreras/RelacionesPublicas.txt",
            "txt/Carreras/LicInformatica.txt",
            "txt/Carreras/LicSistemas.txt",
            "txt/Carreras/Social.txt",
            "txt/Carreras/TecConta.txt",
            "txt/Carreras/TecAnimacion.txt",
            "txt/Carreras/TecDecoracion.txt",
            "txt/Carreras/TecVentas.txt",
            "txt/Carreras/TecSistemas.txt",
            "txt/Carreras/TecRestaurante.txt",
            "txt/Carreras/TecTurismo.txt",
            "txt/Carreras/TecPublicidad.txt"
            // añade más archivos aquí si quieres
        ];

        //Iniciando busqueda de informacion en paralelo
        const textos = await Promise.all(
            archivos.map(ruta => fetch(ruta).then(res => {
                if (!res.ok) throw new Error(`No se pudo cargar ${ruta}`);
                return res.text();
            }))
        );

        const textoCompleto = textos.join("\n\n");

        // Armar el prompt completo
        const prompt = `${textoCompleto}
Pregunta del usuario: ${userMessage}
IMPORTANTE: No uses el símbolo # en ningún título, lista o texto. Si haces listas, usa solo números (1., 2., 3., ...) o guiones (-). No uses otros símbolos para las listas ni para los títulos. Mantén el formato claro y ordenado. 
DA LAS LISTAS COMPLETAS PORFAVOR. 
DA RESPUESTAS CONCRETAS, DIRECTAS Y ESPECÍFICAS, evitando información general o irrelevante.
NO digas bienvenido en cada repuesta.`;

        // Llamar al Backend Gemini con el prompt concatenado
        const response = await fetch("https://backendchat-r5bf.onrender.com/api/gemini", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    contents: [
      {
        parts: [
          {
            text: prompt
          }
        ]
      }
    ]
  })
});


        const data = await response.json();
        const aiText = data.candidates?.[0]?.content?.parts?.[0]?.text || "Error al procesar la respuesta de Gemini.";
        const formattedText = aiText.replace(/\n/g, "<br>");
        iaChatBox.querySelector(".ai-chat-area").innerHTML = formattedText;

    } catch (error) {
        console.log(error);
        iaChatBox.querySelector(".ai-chat-area").textContent = "Ocurrió un error al conectar con Gemini.";
    }
}



// Cajas de texto a crear cuando se mandan mensajes
function createChatBox(html, classes) {
    let div = document.createElement("div");
    div.innerHTML = html;
    div.classList.add(classes);
    return div;
}

// Función de manejo de mensajes
function handlechatResponse(message) {
    user.data = message;

    let html = `
    <img src="imagenes/user.png" alt="" id="UserImagen" width="50">
    <div class="user-chat-area">
        ${user.data}
    </div>`;

    prompt.value = "";
    let userChatBox = createChatBox(html, "user-chat-box");
    userChatBox.style.display = "block";
    chatcontainer.appendChild(userChatBox);
    chatcontainer.scrollTop = chatcontainer.scrollHeight;

    setTimeout(() => {
        let html = `
        <img src="imagenes/ia.png" alt="" id="AiImagen" width="50">
        <div class="ai-chat-area">
            <img src="imagenes/load.gif" alt="" class="load" width="40">
        </div>`;

        let iaChatBox = createChatBox(html, "ai-chat-box");
        chatcontainer.appendChild(iaChatBox);
        chatcontainer.scrollTop = chatcontainer.scrollHeight;

        generateResponse(iaChatBox, message);
    }, 800);
}

// Eventos
prompt.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        if (prompt.value.trim() === "") return;
        handlechatResponse(prompt.value);
        prompt.value = "";
    }
});

document.querySelector("#submit").addEventListener("click", () => {
    if (prompt.value.trim() === "") return;
    handlechatResponse(prompt.value);
    prompt.value = "";
});

