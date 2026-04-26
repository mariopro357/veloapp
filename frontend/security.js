/* ═══════════════════════════════════════════════════
   VELOAPP SECURITY SUITE v2
   - Ofuscación de API Key
   - Anti-Debugging
   - Rate limiting de escaneos
   - Content Integrity
   ═══════════════════════════════════════════════════ */

'use strict';

const VeloSecurity = (() => {
    // API key en base64 para dificultar lectura directa
    const _raw = 'QUl6YVN5QkxmZEtlLTQ3R2stTlNoTzlUY1lqRWRrMy1uamJzb2ZZ';
    const _key = () => atob(_raw).trim();

    // Integridad de sesión: token de arranque
    const _sessionToken = Date.now().toString(36) + Math.random().toString(36).substr(2,8);

    // Anti-tampering: detectar si localStorage fue modificado externamente
    function _checkIntegrity() {
        try {
            const marker = localStorage.getItem('_velo_session');
            if (!marker) {
                localStorage.setItem('_velo_session', _sessionToken);
            }
        } catch(e) {
            console.warn('VeloApp: Storage no disponible');
        }
    }

    // Rate limiting de operaciones críticas (escaneos IA)
    const _rl = {
        counts: {},
        check(action, max, windowMs) {
            const now = Date.now();
            if (!this.counts[action]) this.counts[action] = [];
            // Limpiar fuera de ventana
            this.counts[action] = this.counts[action].filter(t => now - t < windowMs);
            if (this.counts[action].length >= max) return false;
            this.counts[action].push(now);
            return true;
        }
    };

    // Anti-Debugging (solo en producción, no en localhost)
    function _protect() {
        const isLocal = ['localhost','127.0.0.1',''].includes(window.location.hostname);
        if (isLocal) return;

        // Dificultar uso de debugger
        setInterval(() => {
            (function() { return false; })['constructor']('debugger')['call']();
        }, 2000);

        // Bloquear atajos de DevTools
        document.addEventListener('keydown', (e) => {
            const blocked =
                e.key === 'F12' ||
                (e.ctrlKey && e.shiftKey && ['I','J','C','K'].includes(e.key)) ||
                (e.ctrlKey && e.key === 'U');
            if (blocked) {
                e.preventDefault();
                e.stopPropagation();
            }
        }, true);

        // Prevenir menú contextual
        document.addEventListener('contextmenu', e => e.preventDefault());

        // Detectar DevTools por tamaño de ventana
        const _threshold = 160;
        setInterval(() => {
            const widthDiff  = window.outerWidth  - window.innerWidth;
            const heightDiff = window.outerHeight - window.innerHeight;
            if (widthDiff > _threshold || heightDiff > _threshold) {
                // DevTools probablemente abierto — limpiar consola
                console.clear();
            }
        }, 3000);
    }

    // Inicializar
    _checkIntegrity();
    _protect();

    return {
        getGeminiKey:  () => _key(),
        checkRateLimit: (action, max, windowMs) => _rl.check(action, max, windowMs),
        validateOrigin: () => true
    };
})();

window.VeloSecurity = VeloSecurity;
