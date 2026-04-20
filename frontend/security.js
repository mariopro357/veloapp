/* ═══════════════════════════════════════════════════
   VELOAPP SECURITY SUITE
   - API Key Obfuscation
   - Anti-Debugging measures
   - Secure variable handling
   ═══════════════════════════════════════════════════ */

'use strict';

const VeloSecurity = (() => {
    // Llave consolidada para evitar errores de concatenación
    const _raw = 'QUl6YVN5QkxmZEtlLTQ3R2stTlNoTzlUY1lqRWRrMy1uamJzb2ZZ';
    const _key = () => atob(_raw).trim();

    // Anti-Debugging: Intenta dificultar el uso de DevTools detectando cambios de tamaño o debugger loops
    function _protect() {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') return;

        // Bucle de debugger que se activa si la consola está abierta (molesto para atacantes casuales)
        setInterval(() => {
            (function() {
                return false;
            })["constructor"]("debugger")["call"]();
        }, 1000);

        // Bloqueo de atajos comunes de "Inspeccionar" (F12, Ctrl+Shift+I, etc.)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J' || e.key === 'C'))) {
                e.preventDefault();
                console.warn('⚠️ Seguridad VeloApp: Acceso restringido.');
            }
        });

        // Prevenir menú contextual (Click derecho) para ver fuente
        document.addEventListener('contextmenu', e => e.preventDefault());
    }

    // Inicializar protección
    _protect();

    return {
        getGeminiKey: () => _key(),
        validateOrigin: () => true // Placeholder para futuras validaciones de dominio
    };
})();

window.VeloSecurity = VeloSecurity;
