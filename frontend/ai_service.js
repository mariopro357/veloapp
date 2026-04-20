/* ═══════════════════════════════════════════════════
   VELOAPP AI SERVICE (GEMINI 1.5 FLASH)
   - OCR Correction
   - Data Structuring
   - Rate limiting (5s Cooldown)
   ═══════════════════════════════════════════════════ */

'use strict';

const GeminiAPI = (() => {
    const COOLDOWN_MS = 10000; // Proteccion de cuota gratuita (10s)
    let _lastRequestTime = 0;

    const _endpoint = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent';

    async function processOCRText(inputData, context = {}) {
        const now = Date.now();
        const diff = now - _lastRequestTime;
        const targetCurrency = context.currency || 'Bs';

        if (diff < COOLDOWN_MS) {
            const waitSec = Math.ceil((COOLDOWN_MS - diff) / 1000);
            throw new Error(`⚠️ Espera ${waitSec}s.`);
        }

        const isImage = inputData.startsWith('data:image/');
        const key = VeloSecurity.getGeminiKey();
        
        // Simplified Prompt (Strict Verbatim)
        const prompt = `Extrae los datos de esta factura en JSON puro:
{
  "emisor": { "razonSocial": "", "rif": "" },
  "cliente": { "nombre": "", "cedula": "" },
  "transaccion": { "nroFactura": "", "fecha": "" },
  "items": [{ "concepto": "", "monto": 0.00 }],
  "total": 0.0,
  "currency": {"simbolo": "${targetCurrency == 'Bs' ? 'Bs.' : '$'}"}
}
No calcules nada, transcribe exactamente lo que ves.`;

        const parts = [];
        
        // 1. Text FIRST (Instructions)
        parts.push({ text: prompt });

        // 2. Image SECOND (Visual Data)
        if (isImage) {
            const [mimePart, rawBase64] = inputData.split(';base64,');
            const mimeType = mimePart.split(':')[1];
            parts.push({
                inline_data: {
                    mime_type: mimeType,
                    data: rawBase64.replace(/\s/g, '')
                }
            });
        }

        try {
            // Reverting to URL-based auth as it's the most compatible with file:// protocol and browser fetch
            const response = await fetch(`${_endpoint}?key=${key}`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contents: [{ parts: parts }]
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Gemini Raw Error:', errorData);
                const msg = errorData.error?.message || 'Bad Request';
                // Capturar el detalle técnico de Google (INVALID_ARGUMENT, etc)
                const detail = errorData.error?.details?.[0]?.fieldViolations?.[0]?.description || 
                               errorData.error?.details?.[0]?.description || '';
                
                throw new Error(`${msg} ${detail ? '('+detail+')' : ''}`);
            }

            const data = await response.json();
            _lastRequestTime = Date.now();
            
            let resultText = data.candidates?.[0]?.content?.parts?.[0]?.text;
            if (!resultText) throw new Error('Respuesta vacía de la IA.');
            
            resultText = resultText.replace(/```json/g, '').replace(/```/g, '').trim();
            return JSON.parse(resultText);

        } catch (err) {
            console.error('Request failed:', err);
            throw err;
        }
    }

    async function testConnection() {
        const key = VeloSecurity.getGeminiKey();
        try {
            // Usar v1beta con el modelo más reciente Gemini 2.5 Lite
            const apiBeta = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent';
            const response = await fetch(`${apiBeta}?key=${key}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    contents: [{ parts: [{ text: "Hola VeloApp, responde solo 'CONECTADO'" }] }]
                })
            });
            const data = await response.json();
            if (response.ok) return { ok: true, msg: data.candidates[0].content.parts[0].text };
            return { ok: false, msg: data.error?.message || 'Error Desconocido', raw: data };
        } catch (e) {
            return { ok: false, msg: e.message };
        }
    }

    return {
        processOCR: processOCRText,
        testConnection: testConnection,
        getRemainingCooldown: () => {
            const diff = Date.now() - _lastRequestTime;
            return Math.max(0, COOLDOWN_MS - diff);
        }
    };
})();

window.GeminiAPI = GeminiAPI;
