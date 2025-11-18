# Integración con ElevenLabs

## Configuración Requerida

Para activar la funcionalidad completa de llamadas con ElevenLabs, necesitas:

1. **API Key de ElevenLabs**
   - Regístrate en [ElevenLabs](https://elevenlabs.io)
   - Obtén tu API key desde el dashboard
   - Copia tu Voice ID favorito

2. **Reemplazar el código en script.js**

En la función `callElevenLabs`, reemplaza el código comentado por:

```javascript
async function callElevenLabs(text) {
    try {
        const response = await fetch('https://api.elevenlabs.io/v1/text-to-speech/YOUR_VOICE_ID', {
            method: 'POST',
            headers: {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': 'YOUR_API_KEY'
            },
            body: JSON.stringify({
                text: text,
                model_id: "eleven_monolingual_v1",
                voice_settings: {
                    stability: 0.5,
                    similarity_boost: 0.5
                }
            })
        });
        
        if (response.ok) {
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayer = new Audio(audioUrl);
            audioPlayer.play();
            return audioPlayer;
        } else {
            throw new Error(`ElevenLabs API error: ${response.status}`);
        }
        
    } catch (error) {
        console.error('Error en la llamada a ElevenLabs:', error);
        throw error;
    }
}
```

3. **Variables a reemplazar:**
   - `YOUR_API_KEY`: Tu clave API de ElevenLabs
   - `YOUR_VOICE_ID`: El ID de la voz que quieres usar

## Funcionalidades Implementadas

✅ **Pantalla de llamada modal**
- Se muestra al presionar el botón de teléfono
- Animación de llamada en progreso
- Botón para cerrar la llamada

✅ **Control de estado de llamada**
- Previene múltiples llamadas simultáneas
- Manejo de errores
- Limpieza automática al finalizar

✅ **Interfaz responsive**
- Funciona en móvil y desktop
- Animaciones suaves
- Estilos cohesivos con el tema

## Cómo Probar

1. **Sin ElevenLabs (simulación):**
   - El código actual simula una llamada de 3 segundos
   - Puedes probar la interfaz inmediatamente

2. **Con ElevenLabs:**
   - Agrega tu API key y Voice ID
   - Descomenta el código real en `callElevenLabs()`
   - Comenta la simulación

## Mejoras Futuras Sugeridas

- [ ] Selector de voces en la interfaz
- [ ] Control de velocidad de reproducción
- [ ] Historial de llamadas
- [ ] Integración con micrófono para respuestas bidireccionales
