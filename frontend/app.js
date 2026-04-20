/* ═══════════════════════════════════════════════════
   VELOAPP — COMPLETE APP ENGINE
   7 Módulos | localStorage | Sin servidor
   ═══════════════════════════════════════════════════ */

'use strict';

// ══════════════════────────────────────────────
// UTILIDADES DE ALMACENAMIENTO
// ──────────────────────────────────────────────
const Store = {
    get(key, def = null) {
        try { const v = localStorage.getItem('velo_' + key); return v ? JSON.parse(v) : def; }
        catch { return def; }
    },
    set(key, val) {
        try { localStorage.setItem('velo_' + key, JSON.stringify(val)); }
        catch { console.error('Storage error'); }
    },
    del(key) { localStorage.removeItem('velo_' + key); }
};

// ══════════════════────────────────────────────
// UTILIDADES GENERALES
// ──────────────────────────────────────────────
const Utils = {
    fmt(n) { return parseFloat(n || 0).toFixed(2); },
    fmtCurrency(n) { return '$' + this.fmt(n); },
    today() { return new Date().toISOString().split('T')[0]; },
    monthKey() { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`; },
    dateLabel(iso) {
        if (!iso) return '';
        const [y,m,d] = iso.split('-');
        const months = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
        return `${parseInt(d)} ${months[parseInt(m)-1]} ${y}`;
    },
    timeLabel() {
        return new Date().toLocaleTimeString('es-VE', {hour:'2-digit', minute:'2-digit'});
    },
    uid() { return Date.now().toString(36) + Math.random().toString(36).substr(2,5); },
    el(id) { return document.getElementById(id); },
    esc(str) { const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }
};

// ══════════════════────────────────────────────
// TOAST
// ──────────────────────────────────────────────
function toast(msg, icon = '') {
    const t = Utils.el('toast');
    t.innerHTML = icon ? `<span class="material-icons-outlined" style="font-size:16px;vertical-align:middle;margin-right:6px">${icon}</span>${msg}` : msg;
    t.classList.remove('hidden');
    t.classList.add('show');
    clearTimeout(t._timer);
    t._timer = setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.classList.add('hidden'), 300); }, 2500);
}

// ══════════════════────────────────────────────
// MODAL ENGINE
// ──────────────────────────────────────────────
const Modal = {
    show(html) {
        Utils.el('modal-content').innerHTML = `<div class="modal-handle"></div>` + html;
        Utils.el('modal-overlay').classList.remove('hidden');
    },
    close() { Utils.el('modal-overlay').classList.add('hidden'); },
    confirm(msg, cb) {
        this.show(`
            <div class="modal-title">Confirmar</div>
            <p style="color:var(--text-secondary);font-size:14px;margin-bottom:20px">${msg}</p>
            <div style="display:flex;gap:10px">
              <button class="btn btn-danger" onclick="Modal.close()">Cancelar</button>
              <button class="btn btn-primary" id="modal-confirm-ok">Confirmar</button>
            </div>`);
        Utils.el('modal-confirm-ok').onclick = () => { Modal.close(); cb(); };
    }
};

// ══════════════════────────────────────────────
// NOTIFICACIONES (Notification API + ticker)
// ──────────────────────────────────────────────
const Notif = {
    init() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
        this.scheduleDaily();
        this.checkCreditReminder();
    },
    scheduleDaily() {
        // Chequear cada minuto si son las 8:00 AM hora Venezuela (UTC-4)
        setInterval(() => this.checkCreditReminder(), 60000);
    },
    checkCreditReminder() {
        const now = new Date();
        // Venezuela UTC-4
        const vzHour = (now.getUTCHours() - 4 + 24) % 24;
        const vzMin  = now.getUTCMinutes();
        if (vzHour === 8 && vzMin === 0) {
            const creditos = Store.get('creditos', []).filter(c => !c.pagado);
            if (creditos.length > 0) {
                const fechaHoy = Utils.dateLabel(Utils.today());
                this.push(`¡Recuerde pagar su crédito el ${fechaHoy}! Lindo día 🌞`);
                Utils.el('notif-badge').style.display = 'block';
            }
        }
    },
    push(msg) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('VeloApp 💙', { body: msg, icon: '' });
        }
    }
};

// ══════════════════════════════════════════════
// ╔═══════════════════════════════════════════╗
// ║            VISTAS / MÓDULOS               ║
// ╚═══════════════════════════════════════════╝
// ══════════════════════════════════════════════

// ─────────────────────────────────────────────
// HOME DASHBOARD
// ─────────────────────────────────────────────
const ViewHome = {
    render() {
        const gastos  = Store.get('gastos_' + Utils.monthKey(), []);
        const ingresos = Store.get('ingresos_' + Utils.monthKey(), []);
        const ahorros = Store.get('ahorros', { total: 0, meta: 0 });
        const creditos = Store.get('creditos', []).filter(c => !c.pagado);
        const clientes = Store.get('clientes', []);

        const totalGasto   = gastos.reduce((a, g) => a + parseFloat(g.monto || 0), 0);
        const totalIngreso  = ingresos.reduce((a, i) => a + parseFloat(i.monto || 0), 0);
        const balance      = totalIngreso - totalGasto;
        const now          = new Date();
        const hour         = now.getHours();
        let greeting = hour < 12 ? '¡Buenos días!' : hour < 18 ? '¡Buenas tardes!' : '¡Buenas noches!';
        const meses = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];

        return `
        <div class="anim-1">
            <div class="home-greeting">${greeting} 👋</div>
            <div class="home-sub">${meses[now.getMonth()]} ${now.getFullYear()} · Tu resumen personal</div>
        </div>

        <div class="stats-grid anim-2">
            <div class="stat-card card-success-top" onclick="App.navigate('ingresos')">
                <span class="label">Ingresos Mes</span>
                <span class="value success">${Utils.fmtCurrency(totalIngreso)}</span>
                <span class="material-icons-outlined bg-icon">trending_up</span>
            </div>
            <div class="stat-card card-danger-top" onclick="App.navigate('gastos')">
                <span class="label">Gastos Mes</span>
                <span class="value danger">${Utils.fmtCurrency(totalGasto)}</span>
                <span class="material-icons-outlined bg-icon">trending_down</span>
            </div>
            <div class="stat-card ${balance >= 0 ? 'card-success-top' : 'card-danger-top'}" onclick="App.navigate('gastos')">
                <span class="label">Balance</span>
                <span class="value ${balance >= 0 ? 'success' : 'danger'}">${Utils.fmtCurrency(balance)}</span>
                <span class="material-icons-outlined bg-icon">account_balance_wallet</span>
            </div>
            <div class="stat-card card-gold-top" onclick="App.navigate('ahorros')">
                <span class="label">Ahorros</span>
                <span class="value gold">${Utils.fmtCurrency(ahorros.total)}</span>
                <span class="material-icons-outlined bg-icon">savings</span>
            </div>
        </div>

        <div class="card anim-3">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                <span style="font-weight:600;font-size:14px">Estado Rápido</span>
                <span class="chip chip-accent">${meses[now.getMonth()]}</span>
            </div>
            <div class="list-item" onclick="App.navigate('creditos')">
                <div class="list-item-icon"><span class="material-icons-outlined">credit_card</span></div>
                <div class="list-item-content">
                    <div class="list-item-title">Créditos Activos</div>
                    <div class="list-item-sub">Cuotas pendientes</div>
                </div>
                <div class="list-item-right">
                    <span class="chip ${creditos.length > 0 ? 'chip-warning' : 'chip-success'}">${creditos.length}</span>
                </div>
            </div>
            <div class="list-item" onclick="App.navigate('clientes')">
                <div class="list-item-icon"><span class="material-icons-outlined">people</span></div>
                <div class="list-item-content">
                    <div class="list-item-title">Clientes Registrados</div>
                    <div class="list-item-sub">Cartelera de trabajo</div>
                </div>
                <div class="list-item-right">
                    <span class="chip chip-accent">${clientes.length}</span>
                </div>
            </div>
        </div>

        <div class="card anim-4">
            <div class="section-title" style="font-size:14px;margin-bottom:10px">
                <span class="material-icons-outlined" style="font-size:18px">grid_view</span>
                Acceso Rápido
            </div>
            <div class="shortcuts-grid">
                <button class="shortcut-btn" onclick="App.navigate('scanner')">
                    <span class="material-icons-outlined">document_scanner</span>
                    <span>Factura</span>
                </button>
                <button class="shortcut-btn" onclick="App.navigate('gastos')">
                    <span class="material-icons-outlined">receipt_long</span>
                    <span>Gastos</span>
                </button>
                <button class="shortcut-btn" onclick="App.navigate('horarios')">
                    <span class="material-icons-outlined">schedule</span>
                    <span>Horario</span>
                </button>
                <button class="shortcut-btn" onclick="App.navigate('ingresos')">
                    <span class="material-icons-outlined">attach_money</span>
                    <span>Ingreso</span>
                </button>
            </div>
        </div>`;
    }
};


// ─────────────────────────────────────────────
// MÓDULO 1: SCANNER DE FACTURAS (OCR MEJORADO)
// ─────────────────────────────────────────────
const ViewScanner = {
    currentResult: null,
    config: {
        currency: 'Bs',
        rate: null
    },

    async init() {
        // Cargar tasa BCV automáticamente cada vez que entramos
        try {
            const rate = await App.getBcvRate();
            this.config.rate = rate;
        } catch (e) {
            this.config.rate = Store.get('bcv_rate', 48.00); 
        }
    },

    render() {
        const month    = Utils.monthKey();
        const facturas = Store.get('facturas_' + month, []);
        const total    = facturas.reduce((a,f) => a + (f.total || 0), 0);
        const meses    = ['Enero','Feb','Marzo','Abril','Mayo','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
        const now      = new Date();
        return `
        <div class="section-title anim-1">
            <span class="material-icons-outlined">document_scanner</span>
            Escáner de Facturas
        </div>

        <div class="scanner-zone anim-2" id="scanner-dropzone"
             onclick="Utils.el('scanner-input').click()"
             ondragover="event.preventDefault();this.classList.add('drag-over')"
             ondragleave="this.classList.remove('drag-over')"
             ondrop="ViewScanner.onDrop(event)">
            <span class="material-icons-outlined">photo_camera</span>
            <span class="big">Toca para tomar o subir foto</span>
            <p>Funciona con facturas rotadas, arrugadas o en cualquier condición</p>
            <input type="file" id="scanner-input" accept="image/*" capture="environment"
                   style="display:none" onchange="ViewScanner.processImage(event)">
        </div>

        <div id="ocr-status"  style="margin-bottom:14px"></div>
        
        <div style="margin: 15px 0; text-align:center">
            <button class="btn btn-ghost" style="padding:10px 20px; font-size:12px; opacity:0.8" onclick="ViewScanner.runDiagnostic()">
                <span class="material-icons-outlined" style="font-size:16px; vertical-align:middle; margin-right:5px">vps_line</span> 
                Testar Conexión IA
            </button>
            <div id="diag-res" style="font-size:10px; margin-top:10px; color:var(--text-muted); font-family:monospace; background:rgba(0,0,0,0.2); padding:5px; border-radius:5px; min-height:20px"></div>
        </div>

        <div id="ocr-result"  style="margin-bottom:14px"></div>

        <div class="card card-accent-top anim-3">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                <span style="font-weight:700;font-size:16px">
                    📋 Bloc de Notas — ${meses[now.getMonth()]} ${now.getFullYear()}
                </span>
                <span class="chip chip-accent">${Utils.fmtCurrency(total)}</span>
            </div>
            ${facturas.length === 0 ? `
              <div class="empty-state" style="padding:20px">
                <span class="material-icons-outlined" style="font-size:36px">receipt</span>
                <span class="empty-sub">No hay facturas guardadas este mes</span>
              </div>`
            : facturas.map((f,i) => {
                const remains = f.expiresAt ? Math.ceil((f.expiresAt - now.getTime()) / (24 * 60 * 60 * 1000)) : null;
                const isUrgent = remains !== null && remains <= 3;
                return `
                <div class="notepad-entry" onclick="ViewScanner.verFactura(${i})" style="cursor:pointer; border-left: 4px solid ${f.categoria === 'universidad' ? '#4a9eff' : '#fbbf24'}">
                    <div>
                        <div class="date">${Utils.dateLabel(f.fecha)} · ${f.time || ''}</div>
                        <div class="desc" style="font-weight:700; color:#fff">${Utils.esc(f.titulo || 'Factura')}</div>
                        <div style="display:flex; align-items:center; gap:6px; margin-top:4px">
                            <span style="font-size:10px; padding:2px 6px; border-radius:4px; background:${f.categoria === 'universidad' ? 'rgba(74,158,255,0.1)' : 'rgba(251,191,36,0.1)'}; color:${f.categoria === 'universidad' ? '#4a9eff' : '#fbbf24'}; font-weight:800; text-transform:uppercase">
                                ${f.categoria || 'mercado'}
                            </span>
                            ${remains !== null ? `
                            <span style="font-size:10px; color:${isUrgent ? 'var(--danger)' : 'var(--text-muted)'}; font-weight:600">
                                <span class="material-icons-outlined" style="font-size:10px; vertical-align:middle">timer</span>
                                ${isUrgent ? 'Expira pronto: ' : 'Expira en: '}${remains} días
                            </span>` : ''}
                        </div>
                    </div>
                    <div style="display:flex;align-items:center;gap:12px">
                        <span class="amount" style="font-size:16px; font-weight:900; color:#fbbf24">${f.monedaSimbolo || 'Bs.'}${Utils.fmt(f.total)}</span>
                        <button class="btn-icon btn-sm"
                                onclick="event.stopPropagation();ViewScanner.delFactura(${i})"
                                style="width:32px;height:32px;border-radius:8px;background:rgba(239,68,68,0.1);color:var(--danger);border:1px solid rgba(239,68,68,0.2)">
                            <span class="material-icons-outlined" style="font-size:18px">delete</span>
                        </button>
                    </div>
                </div>`;
            }).join('')}
        </div>`;
    },

    // ══ HANDLERS ══════════════════════════════════
    onDrop(e) {
        e.preventDefault();
        document.getElementById('scanner-dropzone').classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        if (file && file.type.startsWith('image/')) this.showPreScanModal(file);
    },

    processImage(e) {
        const file = e.target.files[0];
        if (file) {
            this.showPreScanModal(file);
            e.target.value = ''; // Reset input
        }
    },

    async showPreScanModal(file) {
        // Fetch current rate to make sure it's fresh
        const currentRate = await App.getBcvRate();
        this.config.rate = currentRate;

        Modal.show(`
            <div class="modal-title" style="margin-bottom:15px">
                <span class="material-icons-outlined" style="vertical-align:middle;color:var(--accent-glow)">settings_suggest</span>
                Confirmar Configuración
            </div>
            
            <p style="font-size:13px;color:var(--text-secondary);margin-bottom:20px">
                Confirma la moneda y tasa de la factura para asegurar una extracción 100% exacta. <b>Ahora con Visión por IA directa.</b>
            </p>

            <div class="form-group">
                <label class="form-label">Moneda de la Factura</label>
                <div class="toggle-group" style="display:flex; background:rgba(0,0,0,0.2); border-radius:10px; padding:4px; margin-bottom:15px">
                    <button id="modal-curr-bs" onclick="document.getElementById('modal-curr-bs').classList.add('active');document.getElementById('modal-curr-usd').classList.remove('active');ViewScanner.config.currency='Bs'"
                            class="btn-toggle active"
                            style="flex:1; padding:10px; font-size:13px; border:none; border-radius:7px; cursor:pointer">Bolívares (Bs)</button>
                    <button id="modal-curr-usd" onclick="document.getElementById('modal-curr-usd').classList.add('active');document.getElementById('modal-curr-bs').classList.remove('active');ViewScanner.config.currency='USD'"
                            class="btn-toggle"
                            style="flex:1; padding:10px; font-size:13px; border:none; border-radius:7px; cursor:pointer">Dólares ($)</button>
                </div>
            </div>

            <div class="form-group">
                <label class="form-label">Tasa BCV Oficial (Bs/$)</label>
                <input type="number" id="modal-rate-input" step="0.01" value="${currentRate}" 
                       style="width:100%; border:1px solid var(--glass-border); border-radius:12px; padding:12px; font-size:16px; font-weight:700; color:var(--accent-glow); text-align:center">
            </div>

            <div style="margin-top:25px; display:flex; gap:10px">
                <button class="btn btn-primary" style="flex:2" onclick="ViewScanner.confirmPreScan()">
                    <span class="material-icons-outlined">rocket_launch</span> Iniciar Escaneo
                </button>
                <button class="btn btn-danger" style="flex:1" onclick="Modal.close()">Cancelar</button>
            </div>
        `); 
        this._pendingFile = file;
    },

    confirmPreScan() {
        const rateInput = document.getElementById('modal-rate-input');
        if (rateInput) this.config.rate = rateInput.value;
        const file = this._pendingFile;
        Modal.close();
        this.runDirectVision(file);
    },

    async runDiagnostic() {
        const resEl = document.getElementById('diag-res');
        resEl.innerHTML = '<span class="loading-ring" style="width:12px;height:12px"></span> Probando llave...';
        try {
            const res = await GeminiAPI.testConnection();
            resEl.innerText = res;
        } catch (e) {
            resEl.innerText = "Error crítico: " + e.message;
        }
    },

    setConfig(key, val) {
        this.config[key] = val;
        this.renderCurrentView(); // Refresh UI to show active toggle/rate
    },

    renderCurrentView() {
        if (App.currentView === 'scanner') App.renderCurrentView();
    },

    // ══ MOTOR OCR AVANZADO + GEMINI AI ══════════════
    // ══ NUEVO MOTOR: VISIÓN DIRECTA POR IA ════════
    async runDirectVision(file) {
        if (!file) file = this._pendingFile;
        if (!file) return;

        const statusEl = Utils.el('ocr-status');
        const resultEl = Utils.el('ocr-result');
        resultEl.innerHTML = '';

        // ── 0. Límite Diario de Seguridad (Quota) ──────
        const dayKey = 'daily_ai_scans_' + Utils.today();
        const dailyCount = Store.get(dayKey, 0);
        if (dailyCount >= 50) {
            statusEl.innerHTML = `
                <div class="alert-box alert-danger anim-1">
                    <span class="material-icons-outlined">block</span>
                    Límite diario de IA alcanzado (50/50). Intenta mañana.
                </div>`;
            return;
        }

        // ── 1. Verificar Cooldown ─────────────────────
        const cooldown = GeminiAPI.getRemainingCooldown();
        if (cooldown > 0) {
            const sec = Math.ceil(cooldown / 1000);
            statusEl.innerHTML = `
                <div class="alert-box alert-warning anim-1">
                    <span class="material-icons-outlined">timer</span>
                    Espera <b>${sec} segundos</b> antes del próximo escaneo por IA.
                </div>`;
            return;
        }

        statusEl.innerHTML = `
            <div class="card anim-1" style="border: 2px solid var(--accent-glow); text-align:center; padding:30px">
                <div class="loading-ring" style="width:40px;height:40px;margin:0 auto 15px; border-width:3px"></div>
                <div style="font-weight:800; font-size:16px; color:var(--accent-glow); text-transform:uppercase; letter-spacing:1px">
                    🧠 IA Visualizando Factura...
                </div>
                <div style="font-size:12px; color:var(--text-muted); margin-top:8px">
                    Optimizando imagen y extrayendo datos con visión artificial
                </div>
            </div>`;

        try {
            // 1. Comprimir imagen para subida rápida y confiable (Max 1200px)
            const compressedBlob = await this.compressImage(file, 1200);
            
            // 2. Convertir a Base64
            const base64Data = await this.fileToBase64(compressedBlob);
            
            // 3. Procesar con Gemini Vision API
            const bcvRate = parseFloat(this.config.rate) || Store.get('bcv_rate', 1.0);
            
            const result = await GeminiAPI.processOCR(base64Data, {
                currency: this.config.currency,
                rate: bcvRate
            });

            if (!result || !result.items) throw new Error('La IA no pudo estructurar los datos. Intenta con una foto más clara.');

            this.currentResult = {
                ...result,
                bcvRate: bcvRate
            };

            // Incrementar contador diario
            const dayKey = 'daily_ai_scans_' + Utils.today();
            Store.set(dayKey, (Store.get(dayKey, 0)) + 1);

            setTimeout(() => {
                statusEl.innerHTML = '';
                this.renderDigitalInvoice(file);
                toast('Escaneo inteligente completado', 'auto_awesome');
            }, 600);

        } catch (err) {
            statusEl.innerHTML = `
                <div class="alert-box alert-danger anim-1">
                    <span class="material-icons-outlined">error</span>
                    <div style="text-align:left">
                        <strong>Error de Escaneo</strong><br>
                        <span style="font-size:11px">${Utils.esc(err.message)}</span>
                    </div>
                </div>`;
            console.error('AI Vision Error:', err);
        }
    },

    // ══ COMPRESIÓN DE IMAGEN PARA IA ══════════════
    compressImage(file, maxSide) {
        return new Promise(resolve => {
            const img = new Image();
            const url = URL.createObjectURL(file);
            img.onload = () => {
                URL.revokeObjectURL(url);
                let w = img.width, h = img.height;
                if (w > h) { if (w > maxSide) { h *= maxSide/w; w = maxSide; } }
                else { if (h > maxSide) { w *= maxSide/h; h = maxSide; } }
                
                const canvas  = document.createElement('canvas');
                canvas.width  = w;
                canvas.height = h;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, w, h);
                canvas.toBlob(blob => resolve(blob), 'image/jpeg', 0.9);
            };
            img.onerror = () => resolve(file); 
            img.src = url;
        });
    },

    async runDiagnostic() {
        const diagEl = document.getElementById('diag-res');
        if (!diagEl) return;
        diagEl.innerHTML = '<span class="loading-ring" style="width:10px;height:10px"></span> Conectando con Google Gemini...';
        
        try {
            const res = await GeminiAPI.testConnection();
            if (res.ok) {
                diagEl.style.color = '#10b981';
                diagEl.innerHTML = `✅ ${res.msg} (Conexión Exitosa)`;
            } else {
                diagEl.style.color = '#ef4444';
                diagEl.innerHTML = `❌ Error: ${res.msg}<br>Detalle: ${JSON.stringify(res.raw || 'Sin datos')}`;
            }
        } catch (e) {
            diagEl.style.color = '#ef4444';
            diagEl.innerHTML = `❌ Fallo Crítico: ${e.message}`;
        }
    },

    fileToBase64(fileOrBlob) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(fileOrBlob);
            reader.onload = () => resolve(reader.result);
            reader.onerror = e => reject(e);
        });
    },

    // (Obsoleto) El OCR de Tesseract ya no se usa, pero lo mantengo por compatibilidad si algo falla
    async runOCR(file) {
        return this.runDirectVision(file);
    },

    // ── FUSIONAR DOS LECTURAS OCR ─────────────────
    // Combina las líneas de ambas pasadas, priorizando las que
    // tienen más números (más probable que sean precios reales).
    mergeOcrResults(text1, text2) {
        const scoreLines = (txt) => txt.split('\n')
            .map(l => l.trim())
            .filter(l => l.length > 1);

        const lines1 = scoreLines(text1);
        const lines2 = scoreLines(text2);

        // Contar cuántos dígitos tiene cada texto
        const digits1 = (text1.match(/\d/g) || []).length;
        const digits2 = (text2.match(/\d/g) || []).length;

        // Usar el que tiene más dígitos como base
        const [base, extra] = digits1 >= digits2 ? [lines1, lines2] : [lines2, lines1];

        // Agregar líneas del otro resultado que tengan precios y no estén ya
        const baseSet = new Set(base.map(l => l.toLowerCase().replace(/\s+/g, ' ')));
        const merged  = [...base];
        for (const line of extra) {
            const key = line.toLowerCase().replace(/\s+/g, ' ');
            if (!baseSet.has(key) && /\d[.,]\d/.test(line)) {
                merged.push(line);
            }
        }
        return merged.join('\n');
    },

    // ══════════════════════════════════════════════
    // PRE-PROCESAMIENTO AVANZADO DE IMAGEN
    // ══════════════════════════════════════════════

    // Helper: Cargar imagen en canvas con escala óptima
    _loadToCanvas(file) {
        return new Promise(resolve => {
            const img = new Image();
            const url = URL.createObjectURL(file);
            img.onload = () => {
                // Escalar: mínimo 1400px ancho, máximo 2400px para rapidez
                const targetW = Math.min(Math.max(img.width, 1400), 2400);
                const scale   = targetW / img.width;
                const canvas  = document.createElement('canvas');
                canvas.width  = Math.round(img.width  * scale);
                canvas.height = Math.round(img.height * scale);
                const ctx = canvas.getContext('2d');
                // Antialiasing de calidad
                ctx.imageSmoothingEnabled  = true;
                ctx.imageSmoothingQuality  = 'high';
                ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                URL.revokeObjectURL(url);
                resolve({ canvas, ctx, W: canvas.width, H: canvas.height });
            };
            img.onerror = () => { URL.revokeObjectURL(url); resolve(null); };
            img.src = url;
        });
    },

    // Helper: Extraer canal gris de ImageData
    _toGray(data, W, H) {
        const gray = new Float32Array(W * H);
        for (let i = 0; i < W * H; i++) {
            gray[i] = 0.299 * data[i*4] + 0.587 * data[i*4+1] + 0.114 * data[i*4+2];
        }
        return gray;
    },

    // Helper: Blur Gaussiano separable (σ configurable)
    _gaussianBlur(gray, W, H, sigma) {
        const radius = Math.ceil(sigma * 2);
        const size   = radius * 2 + 1;
        // Construir kernel 1D
        const kernel = new Float32Array(size);
        let sum = 0;
        for (let k = 0; k < size; k++) {
            const x    = k - radius;
            kernel[k]  = Math.exp(-(x*x) / (2*sigma*sigma));
            sum       += kernel[k];
        }
        for (let k = 0; k < size; k++) kernel[k] /= sum;

        const tmp  = new Float32Array(W * H);
        const out  = new Float32Array(W * H);

        // Horizontal
        for (let y = 0; y < H; y++) {
            for (let x = 0; x < W; x++) {
                let v = 0;
                for (let k = 0; k < size; k++) {
                    const sx = Math.min(W-1, Math.max(0, x + k - radius));
                    v += gray[y*W + sx] * kernel[k];
                }
                tmp[y*W + x] = v;
            }
        }
        // Vertical
        for (let y = 0; y < H; y++) {
            for (let x = 0; x < W; x++) {
                let v = 0;
                for (let k = 0; k < size; k++) {
                    const sy = Math.min(H-1, Math.max(0, y + k - radius));
                    v += tmp[sy*W + x] * kernel[k];
                }
                out[y*W + x] = v;
            }
        }
        return out;
    },

    // Helper: Tabla de integrales para umbral adaptativo rápido O(1)/pixel
    _integralImage(gray, W, H) {
        const integral = new Float64Array((W+1) * (H+1));
        for (let y = 0; y < H; y++) {
            for (let x = 0; x < W; x++) {
                integral[(y+1)*(W+1) + (x+1)] =
                    gray[y*W + x]
                    + integral[y*(W+1) + (x+1)]
                    + integral[(y+1)*(W+1) + x]
                    - integral[y*(W+1) + x];
            }
        }
        return integral;
    },

    // Helper: Umbral adaptativo de Sauvola (excelente para fondos desiguales)
    // Ideal para facturas arrugadas, con luz no uniforme o manchas
    _adaptiveThreshold(gray, W, H, blockR, C) {
        const integral = this._integralImage(gray, W, H);
        const out      = new Uint8Array(W * H);
        const area     = (2*blockR+1) ** 2;

        for (let y = 0; y < H; y++) {
            for (let x = 0; x < W; x++) {
                const x1 = Math.max(0, x - blockR);
                const y1 = Math.max(0, y - blockR);
                const x2 = Math.min(W-1, x + blockR);
                const y2 = Math.min(H-1, y + blockR);
                const n  = (x2-x1+1) * (y2-y1+1);
                const s  = integral[(y2+1)*(W+1) + (x2+1)]
                           - integral[y1*(W+1) + (x2+1)]
                           - integral[(y2+1)*(W+1) + x1]
                           + integral[y1*(W+1) + x1];
                const mean = s / n;
                // Pixel es texto (negro) si está suficientemente por debajo del promedio local
                out[y*W + x] = gray[y*W + x] < (mean - C) ? 0 : 255;
            }
        }
        return out;
    },

    // ── ESTRATEGIA 1: UMBRAL ADAPTATIVO ──────────
    // Mejor para: facturas arrugadas, luz irregular, fondos manchados.
    // Usa Gaussian blur + unsharp mask + binarización adaptativa local.
    async preprocessAdaptive(file) {
        const loaded = await this._loadToCanvas(file);
        if (!loaded) return null;
        const { canvas, ctx, W, H } = loaded;

        const raw     = ctx.getImageData(0, 0, W, H);
        const gray    = this._toGray(raw.data, W, H);

        // 1. Blur suave para eliminar ruido de arrugas
        const blurred = this._gaussianBlur(gray, W, H, 1.2);

        // 2. Unsharp mask: realza bordes del texto
        //    sharpened = gray + (gray - blurred) * amount
        const sharp = new Float32Array(W * H);
        for (let i = 0; i < W*H; i++) {
            sharp[i] = Math.min(255, Math.max(0, gray[i] + (gray[i] - blurred[i]) * 1.8));
        }

        // 3. Umbral adaptativo (bloque 25px, C=10)
        //    Maneja zonas de luz distinta dentro de la misma imagen
        const binar = this._adaptiveThreshold(sharp, W, H, 25, 10);

        // 4. Escribir en canvas y exportar
        const imgOut = ctx.createImageData(W, H);
        for (let i = 0; i < W*H; i++) {
            imgOut.data[i*4]   = binar[i];
            imgOut.data[i*4+1] = binar[i];
            imgOut.data[i*4+2] = binar[i];
            imgOut.data[i*4+3] = 255;
        }
        ctx.putImageData(imgOut, 0, 0);
        return new Promise(r => canvas.toBlob(r, 'image/png'));
    },

    // ── ESTRATEGIA 2: CONTRASTE GLOBAL FUERTE ────
    // Mejor para: facturas descoloridas, oscuras, papel amarillento.
    // Usa normalización de histograma + contraste agresivo.
    async preprocessContrast(file) {
        const loaded = await this._loadToCanvas(file);
        if (!loaded) return null;
        const { canvas, ctx, W, H } = loaded;

        const raw  = ctx.getImageData(0, 0, W, H);
        const d    = raw.data;
        const gray = this._toGray(d, W, H);

        // 1. Encontrar rango real del histograma (1%-99% percentile)
        const hist    = new Array(256).fill(0);
        for (const v of gray) hist[Math.round(v)]++;
        const total   = W * H;
        const pLow    = 0.01 * total;
        const pHigh   = 0.99 * total;
        let cumul = 0, minV = 0, maxV = 255;
        for (let i = 0; i < 256; i++)  { cumul += hist[i]; if (cumul >= pLow  && minV === 0) minV = i; }
        cumul = 0;
        for (let i = 255; i >= 0; i--) { cumul += hist[i]; if (cumul >= (total-pHigh) && maxV === 255) maxV = i; }
        const range = Math.max(1, maxV - minV);

        // 2. Aplicar normalización de contraste + gamma
        const blur2  = this._gaussianBlur(gray, W, H, 0.8);
        const imgOut = ctx.createImageData(W, H);
        for (let i = 0; i < W * H; i++) {
            // Normalizar al rango completo
            let v    = Math.min(255, Math.max(0, ((blur2[i] - minV) / range) * 255));
            // Gamma correction 0.75 (oscurece texto, aclara fondo)
            v        = 255 * Math.pow(v / 255, 0.75);
            // Contraste final x1.5
            v        = Math.min(255, Math.max(0, (v - 128) * 1.5 + 128));
            const vi = Math.round(v);
            imgOut.data[i*4]   = vi;
            imgOut.data[i*4+1] = vi;
            imgOut.data[i*4+2] = vi;
            imgOut.data[i*4+3] = 255;
        }
        ctx.putImageData(imgOut, 0, 0);
        return new Promise(r => canvas.toBlob(r, 'image/png'));
    },

    statusMsg(s) {
        const m = {
            'loading tesseract core':       '⚙️  Cargando motor OCR...',
            'initializing tesseract':       '🔧  Iniciando Tesseract...',
            'initialized tesseract':        '✅  Motor listo',
            'loading language traineddata': '📚  Cargando español + inglés...',
            'loaded language traineddata':  '✅  Idioma cargado',
            'initializing api':             '🔍  Preparando reconocimiento...',
            'recognizing text':             '🧠  Leyendo factura...'
        };
        return m[s] || s;
    },

    // ══ CORRECCIÓN DE ERRORES OCR COMUNES ════════
    // El OCR confunde: O↔0  l/I↔1  S↔5  B/G↔8  Z↔2
    fixOcrDigits(str) {
        return str
            .replace(/O/g, '0').replace(/o/g, '0')   // O → 0 (en contexto numérico)
            .replace(/[lI\|]/g, '1')                   // l, I, | → 1
            .replace(/[Z]/g,   '2')                    // Z → 2
            .replace(/[G]/g,   '6')                    // G → 6
            .replace(/[B]/g,   '8')                    // B → 8
            .replace(/,/g,     '.');                   // coma → punto decimal
    },

    // ══ DETECTOR DE MONEDA ════════════════════════
    detectCurrency(text) {
        if (/Bs\.?\s*[Ff]/i.test(text))           return { simbolo: 'Bs.F', nombre: 'Bolívares Fuertes', key: 'BsF' };
        if (/Bs\.?\s*[Dd]/i.test(text))           return { simbolo: 'Bs.D', nombre: 'Bolívares Digitales', key: 'BsD' };
        if (/\bBs\.?\b/i.test(text))              return { simbolo: 'Bs.',  nombre: 'Bolívares', key: 'BsF' };
        if (/bolívar|bolivar/i.test(text))         return { simbolo: 'Bs.',  nombre: 'Bolívares', key: 'BsF' };
        if (/\bCOP\b|\bpeso[s]?\b/i.test(text))   return { simbolo: '$',   nombre: 'Pesos Colombianos', key: 'COP' };
        if (/\bEUR\b|€/i.test(text))              return { simbolo: '€',   nombre: 'Euros', key: 'EUR' };
        if (/\bUSD\b|\$\s*USD/i.test(text))       return { simbolo: '$',   nombre: 'Dólares USD', key: 'USD' };
        if (/\$/.test(text))                       return { simbolo: '$',   nombre: 'Dólares', key: 'USD' };
        return                                            { simbolo: '$',   nombre: 'Dólares', key: 'USD' };
    },

    // ══ PARSEO PRINCIPAL ══════════════════════════
    parseAndShow(rawText, file) {
        Utils.el('ocr-status').innerHTML = `
            <div class="alert-box alert-success">
                <span class="material-icons-outlined" style="font-size:18px">check_circle</span>
                ¡Imagen analizada! Generando factura digital...
            </div>`;

        const currency = this.detectCurrency(rawText);

        // Dividir en líneas limpias
        const rawLines = rawText
            .split('\n')
            .map(l => l.trim())
            .filter(l => l.length > 1);

        // ── Detectar cabecera (primeras líneas sin dígitos = nombre de tienda)
        let shopLines = [];
        for (let i = 0; i < Math.min(5, rawLines.length); i++) {
            const hasDigit = /\d/.test(rawLines[i]);
            if (!hasDigit && rawLines[i].length > 2) shopLines.push(rawLines[i]);
            else if (hasDigit) break;
        }
        const shopName = shopLines.slice(0, 2).join(' — ').trim();

        const SKIP_WORDS = /^(fecha|date|hora|time|rif|nit|cif|nro|n\.|recibo|gracias|vuelto|cambio|banco|ref|cajero|caja|operacion|autorización|telefono|tlf|atendido|servido|bienvenido|subtotal|descuento|propina)$/i;

        const items  = [];
        let billIva   = null;
        let billTotal = null;       // total detectado en la factura

        for (const line of rawLines) {
            // Saltar separadores visuales
            if (/^[-=_*#|.]{3,}$/.test(line)) continue;

            const lowerLine = line.toLowerCase().trim();

            // ── Detectar líneas de TOTAL/IVA ────────────────
            const isTotalLine    = /\btotal\b/i.test(lowerLine) && !/subtotal/i.test(lowerLine);
            const isSubtotalLine = /subtotal/i.test(lowerLine);
            const isIvaLine      = /\biva\b|\bimpuesto\b|\btax\b/i.test(lowerLine);
            const isSkip         = SKIP_WORDS.test(lowerLine) && !isTotalLine && !isIvaLine;
            if (isSkip) continue;

            // ── Extraer precio de la línea ───────────────────
            const extracted = this.extractPrice(line, currency.key);
            if (!extracted) continue;

            const { price, rawPrice, nameStr } = extracted;
            if (price <= 0 || price > 9999999) continue;

            if (isTotalLine) {
                billTotal = price;
                continue;
            }
            if (isIvaLine) {
                billIva = price;
                continue;
            }
            if (isSubtotalLine) continue;  // ya lo calculamos nosotros

            // ── Limpiar nombre del producto ──────────────────
            let { name, qty, unitPrice } = this.parseProductLine(nameStr, price);

            items.push({ name, qty, unitPrice, price });
        }

        // Totales finales
        const subtotal   = items.reduce((a,i) => a + i.price, 0);
        const totalFinal = billTotal || (subtotal + (billIva || 0));

        this.currentResult = { items, iva: billIva, subtotal, total: totalFinal, shopName, currency, rawText };

        this.renderDigitalInvoice(file);
    },

    // ── EXTRAER PRECIO DE UNA LÍNEA ───────────────
    // Retorna { price, rawPrice, nameStr } o null
    extractPrice(line, currencyKey) {
        const isBs = currencyKey === 'BsF' || currencyKey === 'BsD';

        // Patrón 1: símbolo de moneda DELANTE  →  $12.50  Bs 45,00  $ 1.234,50
        const p1 = line.match(/(?:\$|Bs\.?\s*[FfDd]?\s*|€|USD\s+)(\d[\d.,]*)/i);
        if (p1) return { price: this.parsePrice(p1[1]), rawPrice: p1[1], nameStr: line.replace(p1[0], '').trim() };

        // Patrón 2: símbolo DETRÁS  →  45Bs  12.50$
        const p2 = line.match(/(\d[\d.,]*)(?:\s*(?:\$|Bs\.?|€|USD))/i);
        if (p2) return { price: this.parsePrice(p2[1]), rawPrice: p2[1], nameStr: line.replace(p2[0], '').trim() };

        // Patrón 3: número decimal al final (XX,XX || X.XXX,XX || X,XXX.XX)
        const p3 = line.match(/^(.+?)\s{2,}(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})\s*$/);
        if (p3) return { price: this.parsePrice(p3[2]), rawPrice: p3[2], nameStr: p3[1].trim() };

        // Patrón 4: número decimal simple al final con 1 espacio
        const p4 = line.match(/^(.+?)\s+(\d{1,4}[.,]\d{2})\s*$/);
        if (p4) return { price: this.parsePrice(p4[2]), rawPrice: p4[2], nameStr: p4[1].trim() };

        // Patrón 5: entero de 2-6 dígitos al final (precio entero)
        // Solo si la parte de texto tiene al menos 3 caracteres de letras
        const p5 = line.match(/^(.+?)\s+(\d{2,6})\s*$/);
        if (p5 && /[a-zA-ZáéíóúÁÉÍÓÚñÑ]{3,}/.test(p5[1])) {
            return { price: this.parsePrice(p5[2]), rawPrice: p5[2], nameStr: p5[1].trim() };
        }

        return null;
    },

    // ── PARSEO ROBUSTO DE NÚMERO ──────────────────
    parsePrice(str) {
        if (!str) return 0;
        let s = str.toString().trim();

        // Formato europeo con miles en punto: 1.234,50
        if (/^\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?$/.test(s)) {
            s = s.replace(/\./g, '').replace(',', '.');
        }
        // Formato americano con miles en coma: 1,234.50
        else if (/^\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?$/.test(s)) {
            s = s.replace(/,/g, '');
        }
        // Coma simple como decimal: 45,50
        else {
            s = s.replace(',', '.');
        }

        // Aplicar correcciones de caracteres OCR en contexto numérico
        s = this.fixOcrDigits(s);

        const v = parseFloat(s);
        return isNaN(v) ? 0 : v;
    },

    // ── PARSEAR LÍNEA DE PRODUCTO ─────────────────
    // Detecta cantidad: "2 x Arroz"  "3×Leche"  "2 @ 5.00"
    parseProductLine(nameStr, totalPrice) {
        let qty = 1, unitPrice = totalPrice, name = '';

        const qtyMatch = nameStr.match(/^(\d{1,3})\s*[xX×@]\s*(.+?)(?:\s+[\d.,]+)?$/i);
        if (qtyMatch) {
            qty       = parseInt(qtyMatch[1]) || 1;
            name      = this.cleanName(qtyMatch[2]);
            unitPrice = qty > 0 ? totalPrice / qty : totalPrice;
        } else {
            name = this.cleanName(nameStr);
        }

        if (!name || name.length < 2) name = 'Producto';
        return { name, qty, unitPrice };
    },

    // ── LIMPIAR NOMBRE ────────────────────────────
    cleanName(raw) {
        if (!raw) return '';
        return raw
            .replace(/[^\w\sáéíóúÁÉÍÓÚñÑüÜ()\-.,/%]/g, ' ')  // eliminar ruido
            .replace(/\b\d{6,}\b/g, '')                         // eliminar códigos de barras
            .replace(/^\d+\s*/,     '')                         // eliminar número inicial suelto
            .replace(/\s{2,}/g,     ' ')                        // espacios múltiples
            .trim()
            .substring(0, 60);
    },

    // ══ FACTURA DIGITAL VISUAL ════════════════════
    renderDigitalInvoice(file) {
        const r      = this.currentResult;
        const sym    = r.currency.simbolo;
        const items  = r.items;
        const imgUrl = URL.createObjectURL(file);
        const now    = new Date();
        const dateStr = Utils.dateLabel(Utils.today());
        const timeStr = now.toLocaleTimeString('es-VE', {hour:'2-digit', minute:'2-digit'});

        // Indicador de confianza
        const conf = items.length >= 3 ? { label: '🟢 Alta', color: 'var(--success)' }
                   : items.length >= 1 ? { label: '🟡 Media', color: 'var(--warning)' }
                                       : { label: '🔴 Baja',  color: 'var(--danger)' };

        // Inyectar estilos de factura digital (una sola vez)
        if (!document.getElementById('invoice-styles')) {
            const style = document.createElement('style');
            style.id = 'invoice-styles';
            style.textContent = `
            details > summary { list-style: none; }
            details > summary::-webkit-details-marker { display:none; }

            .digital-invoice { background: #0c1425; border:1px solid rgba(45,125,210,0.3); border-radius:16px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,0.5); font-family:'Outfit',sans-serif; margin-bottom:20px; color:#e2e8f0; }
            .inv-section { padding:15px 20px; border-bottom:1px solid rgba(45,125,210,0.1); }
            .inv-section-title { display:flex; align-items:center; gap:8px; font-weight:800; font-size:14px; color:#4a9eff; text-transform:uppercase; letter-spacing:1px; margin-bottom:10px; }
            
            .inv-emisor-name { font-size:17px; font-weight:900; color:#fff; line-height:1.2; margin-bottom:4px; }
            .inv-emisor-inst { font-size:12px; color:#94a3b8; margin-bottom:8px; font-weight:500; font-style:italic; }
            
            .inv-grid { display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:11px; }
            .inv-label { color:#64748b; font-weight:600; }
            .inv-val { color:#cbd5e1; }
            
            .inv-info-box { background: rgba(0,0,0,0.2); border-radius:10px; padding:12px; margin-top:5px; border:1px solid rgba(45,125,210,0.1); }
            
            .inv-table { width:100%; border-collapse:collapse; margin-top:10px; }
            .inv-table th { text-align:left; font-size:10px; color:#64748b; padding:8px; border-bottom:2px solid rgba(45,125,210,0.2); text-transform:uppercase; }
            .inv-table td { padding:10px 8px; font-size:12px; border-bottom:1px solid rgba(45,125,210,0.05); }
            .inv-amount-cell { text-align:right; font-weight:700; color:#fbbf24; }
            
            .inv-resumen-box { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding:20px; text-align:right; border-top:2px dashed rgba(45,125,210,0.3); }
            .inv-total-label { font-size:14px; font-weight:800; color:#4a9eff; margin-bottom:4px; letter-spacing:1px; }
            .inv-total-val { font-size:28px; font-weight:900; color:#fbbf24; text-shadow:0 0 15px rgba(251,191,36,0.3); }
            
            .inv-footer-notes { padding:15px 20px; font-size:11px; color:#94a3b8; background:rgba(0,0,0,0.1); }
            .inv-note-row { display:flex; justify-content:space-between; margin-bottom:6px; border-bottom:1px solid rgba(255,255,255,0.03); padding-bottom:4px; }
            .inv-note-row:last-child { border:none; }
            `;
            document.head.appendChild(style);
        }

        Utils.el('ocr-result').innerHTML = `

        <!-- ① Imagen original (colapsable para ahorrar espacio) -->
        <div class="card anim-1" style="padding:10px;margin-bottom:14px">
            <details>
                <summary style="cursor:pointer;font-size:13px;color:var(--text-secondary);padding:4px 0;user-select:none">
                    📷 Mostrar imagen original de la factura ▾
                </summary>
                <img src="${imgUrl}" alt="Factura original"
                     style="width:100%;border-radius:12px;margin-top:10px;
                            filter:brightness(1.05) contrast(1.1);display:block">
            </details>
        </div>

        <div class="digital-invoice anim-2">
            <div style="background:#1a3060; color:#fff; padding:12px; font-weight:900; text-align:center; font-size:14px; letter-spacing:2px">
                📄 FACTURA DIGITAL (VeloApp)
            </div>

            <!-- ① EMISOR -->
            <div class="inv-section">
                <div class="inv-section-title">🏢 Datos del Emisor</div>
                <div class="inv-emisor-name">${Utils.esc(r.emisor?.razonSocial || 'Emisor no detectado')}</div>
                <div class="inv-emisor-inst">${Utils.esc(r.emisor?.institucion || '')}</div>
                <div class="inv-grid">
                    <div><span class="inv-label">RIF:</span> <span class="inv-val">${Utils.esc(r.emisor?.rif || '—')}</span></div>
                    <div><span class="inv-label">NIT:</span> <span class="inv-val">${Utils.esc(r.emisor?.nit || '—')}</span></div>
                </div>
                <div style="font-size:11px; margin-top:6px; line-height:1.4">
                    <span class="inv-label">Dirección:</span> <span class="inv-val">${Utils.esc(r.emisor?.direccion || '—')}</span>
                </div>
                <div class="inv-grid" style="margin-top:6px">
                    <div><span class="inv-label">Teléfonos:</span> <span class="inv-val">${Utils.esc(r.emisor?.telefonos || '—')}</span></div>
                    <div><span class="inv-label">Sitio Web:</span> <span class="inv-val">${Utils.esc(r.emisor?.web || '—')}</span></div>
                </div>
            </div>

            <!-- ② CLIENTE -->
            <div class="inv-section" style="background:rgba(45,125,210,0.03)">
                <div class="inv-section-title">🆔 Datos del Cliente / Estudiante</div>
                <div class="inv-info-box">
                    <div style="font-size:14px; font-weight:800; color:#fff; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:5px; margin-bottom:5px">
                        Nombre: ${Utils.esc(r.cliente?.nombre || '—')}
                    </div>
                    <div class="inv-grid">
                        <div><span class="inv-label">Cédula:</span> <span class="inv-val">${Utils.esc(r.cliente?.cedula || '—')}</span></div>
                        <div><span class="inv-label">Carrera:</span> <span class="inv-val">${Utils.esc(r.cliente?.carrera || '—')}</span></div>
                    </div>
                </div>
            </div>

            <!-- ③ TRANSACCION -->
            <div class="inv-section">
                <div class="inv-section-title">🗓️ Detalles de la Transacción</div>
                <div class="inv-grid">
                    <div><span class="inv-label">Nro. Factura:</span> <span class="inv-val">${Utils.esc(r.transaccion?.nroFactura || '—')}</span></div>
                    <div><span class="inv-label">Nro. Control:</span> <span class="inv-val">${Utils.esc(r.transaccion?.nroControl || '—')}</span></div>
                    <div><span class="inv-label">Fecha Emisión:</span> <span class="inv-val">${Utils.esc(r.transaccion?.fecha || dateStr)}</span></div>
                    <div><span class="inv-label">Hora:</span> <span class="inv-val">${Utils.esc(r.transaccion?.hora || timeStr)}</span></div>
                </div>
            </div>

            <!-- ④ DETALLE PAGO -->
            <div class="inv-section">
                <div class="inv-section-title">🛍️ Detalle de Pago</div>
                <table class="inv-table">
                    <thead>
                        <tr>
                            <th>Fecha</th>
                            <th>Concepto</th>
                            <th style="text-align:right">Monto</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${r.items.map(it => `
                        <tr>
                            <td><span class="inv-val">${Utils.esc(it.fecha || r.transaccion?.fecha || '')}</span></td>
                            <td>
                                <div style="font-weight:700">${Utils.esc(it.concepto || it.name || 'Sin concepto')}</div>
                                <div style="font-size:9px; color:#64748b">${it.documento ? 'Doc: '+it.documento : ''}</div>
                            </td>
                            <td class="inv-amount-cell">${sym}${Utils.fmt(it.monto || it.price)}</td>
                        </tr>`).join('')}
                    </tbody>
                </table>
            </div>

            <!-- ⑤ RESUMEN -->
            <div class="inv-resumen-box">
                <div class="inv-section-title" style="color:#94a3b8; font-size:11px; margin-bottom:5px; justify-content:flex-end">💰 Resumen Financiero</div>
                <div style="display:flex; justify-content:space-between; align-items:center">
                    <span class="inv-label" style="font-size:12px">Total Pago</span>
                    <div class="inv-total-val">${sym}${Utils.fmt(r.total)}</div>
                </div>
            </div>

            <!-- ⑥ NOTAS -->
            <div class="inv-footer-notes">
                <div class="inv-section-title" style="color:#94a3b8; font-size:11px">📝 Notas Adicionales</div>
                <div class="inv-note-row">
                    <span class="inv-label">Próximo Pago:</span>
                    <span class="inv-val" style="color:#fbbf24; font-weight:800">${Utils.esc(r.notas?.proximoPago || '—')}</span>
                </div>
                <div class="inv-note-row">
                    <span class="inv-label">Cajero:</span>
                    <span class="inv-val">${Utils.esc(r.notas?.cajero || '—')}</span>
                </div>
                <div class="inv-note-row">
                    <span class="inv-label">Forma de Forma:</span>
                    <span class="inv-val">${Utils.esc(r.notas?.formaForma || 'FORMA LIBRE')}</span>
                </div>
            </div>

            <div style="background:#000; padding:8px; text-align:center; font-size:10px; color:#4a5f80">
                VELOAPP DIGITAL TRANSCRIPTION ENGINE
            </div>
        </div>

        <!-- ③ CORRECCIÓN MANUAL -->
        <div class="card anim-3" style="margin-bottom:14px">
            <div style="font-weight:700;font-size:14px;margin-bottom:12px">
                ✏️ Agregar / Corregir Productoss
            </div>
            <div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:10px">
                <input type="text"   id="man-nombre" placeholder="Nombre del producto" style="flex:2">
                <input type="number" id="man-precio" placeholder="Precio" step="0.01" min="0" style="flex:1;min-width:80px">
                <button onclick="ViewScanner.addManualItem()"
                        style="width:42px;height:44px;border-radius:10px;background:var(--accent-soft);border:1px solid var(--glass-border);color:var(--accent-glow);cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0">
                    <span class="material-icons-outlined" style="font-size:22px">add</span>
                </button>
            </div>
            <div id="manual-items-list"></div>
        </div>

        <!-- ④ GUARDAR -->
        <div class="card anim-4" style="margin-bottom:14px">
            <div class="form-group">
                <label class="form-label">Nombre de la tienda / nota</label>
                <input type="text" id="factura-titulo"
                       placeholder="Ej: Mercado Central, Farmatodo..."
                       value="${r.shopName ? Utils.esc(r.shopName) : ''}">
            </div>
            <div class="form-group anim-3">
                <label class="form-label">Tipo de Factura (Periodo de guardado)</label>
                <select id="factura-categoria" style="border:1px solid var(--accent-soft); background:rgba(45,125,210,0.05)">
                    <option value="mercado">🛒 Mercado (Guardar por 1 Mes)</option>
                    <option value="universidad">🎓 Universidad (Guardar por 4 Meses)</option>
                </select>
                <p style="font-size:10px; color:var(--text-muted); margin-top:5px; margin-left:5px">
                    * Las de mercado se borran solas en 30 días, las de universidad en 120 días.
                </p>
            </div>
            
            <div class="form-group anim-4">
                <label class="form-label">Confirmar Moneda</label>
                <select id="factura-moneda">
                    <option value="Bs" ${r.currency.key==='Bs'?'selected':''}>🇻🇪 Bolívares (Bs.)</option>
                    <option value="USD" ${r.currency.key==='USD'?'selected':''}>💵 Dólares (USD)</option>
                </select>
            </div>

            <button class="btn btn-primary anim-5" onclick="ViewScanner.saveFactura()" style="width:100%; height:54px; margin-top:10px">
                <span class="material-icons-outlined">save</span>
                Guardar como Factura Digital (Transcripción)
            </button>
        </div>`;
    },

    // ══ AGREGAR ÍTEM MANUAL ═══════════════════════
    _manualList: [],

    addManualItem() {
        const nombreEl = Utils.el('man-nombre');
        const precioEl = Utils.el('man-precio');
        const nombre   = nombreEl?.value?.trim();
        const precio   = parseFloat(precioEl?.value || 0);

        if (!nombre || precio <= 0) { toast('Ingresa nombre y precio válidos', 'warning'); return; }
        if (!this.currentResult)    return;

        const sym = this.currentResult.currency.simbolo;

        // Añadir al modelo
        this.currentResult.items.push({ name: nombre, qty: 1, unitPrice: precio, price: precio });
        this.currentResult.subtotal += precio;
        this.currentResult.total    += precio;
        this._manualList.push({ nombre, precio });

        // UI: agregar tag en la lista manual
        const listEl = Utils.el('manual-items-list');
        if (listEl) {
            const idx = this._manualList.length - 1;
            const tag = document.createElement('div');
            tag.className = 'manual-tag';
            tag.id = `man-tag-${idx}`;
            tag.innerHTML = `
                <span class="manual-tag-name">🛒 ${Utils.esc(nombre)}</span>
                <span class="manual-tag-price">${sym}${Utils.fmt(precio)}</span>
                <button class="manual-tag-del" onclick="ViewScanner.removeManualItem(${idx})" title="Eliminar">
                    <span class="material-icons-outlined" style="font-size:14px">close</span>
                </button>`;
            listEl.appendChild(tag);
        }

        nombreEl.value = '';
        precioEl.value = '';
        nombreEl.focus();
        toast(`"${nombre}" agregado`, 'add_shopping_cart');
    },

    removeManualItem(idx) {
        const item = this._manualList[idx];
        if (!item || !this.currentResult) return;
        // Buscar y eliminar del array de items
        const pos = this.currentResult.items.findLastIndex(i => i.name === item.nombre && i.price === item.precio);
        if (pos >= 0) {
            this.currentResult.items.splice(pos, 1);
            this.currentResult.subtotal -= item.precio;
            this.currentResult.total    -= item.precio;
        }
        const tag = Utils.el(`man-tag-${idx}`);
        if (tag) tag.remove();
        toast('Producto eliminado', 'remove');
    },

    // ══ GUARDAR FACTURA ═══════════════════════════
    saveFactura() {
        if (!this.currentResult) return;
        const r = this.currentResult;
        const categoria = Utils.el('factura-categoria')?.value || 'mercado';
        const monedaKey = Utils.el('factura-moneda')?.value || 'Bs';
        
        // Retention Policy Logic
        const now = Date.now();
        const oneDay = 24 * 60 * 60 * 1000;
        const retentionDays = categoria === 'universidad' ? 120 : 30;
        const expiresAt = now + (retentionDays * oneDay);

        const symMap    = { USD:'$', Bs:'Bs.', COP:'$', EUR:'€' };
        const sym       = symMap[monedaKey] || 'Bs.';
        
        const month     = Utils.monthKey();
        const facturas  = Store.get('facturas_' + month, []);

        facturas.push({
            titulo:        r.emisor?.razonSocial || 'Factura Digital',
            categoria,
            expiresAt,
            createdAt:     now,
            fecha:         Utils.today(),
            time:          Utils.timeLabel(),
            itemCount:     r.items.length,
            total:         r.total,
            moneda:        monedaKey,
            monedaSimbolo: sym,
            // Full Detailed Snapshot
            snapshot: {
                emisor: r.emisor,
                cliente: r.cliente,
                transaccion: r.transaccion,
                items: r.items,
                notas: r.notas
            }
        });

        Store.set('facturas_' + month, facturas);
        this.currentResult = null;
        this._manualList   = [];
        toast(`✅ Guardada como ${categoria}. Expiración: ${retentionDays} días.`, 'save');
        App.navigate('scanner');
    },

    // ══ VER FACTURA GUARDADA ══════════════════════
    verFactura(idx) {
        const month    = Utils.monthKey();
        const facturas = Store.get('facturas_' + month, []);
        const f        = facturas[idx];
        if (!f) return;
        const sym = f.monedaSimbolo || 'Bs.';

        // If high-fidelity snapshot exists, use the same template as scanner
        if (f.snapshot) {
            const r = f.snapshot;
            Modal.show(`
                <div class="digital-invoice" style="margin-bottom:0">
                    <div style="background:#1a3060; color:#fff; padding:12px; font-weight:900; text-align:center; font-size:14px; letter-spacing:2px">
                        📄 FACTURA DIGITAL GUARDADA (VeloApp)
                    </div>

                    <!-- EMISOR -->
                    <div class="inv-section">
                        <div class="inv-section-title">🏢 Datos del Emisor</div>
                        <div class="inv-emisor-name">${Utils.esc(r.emisor?.razonSocial || '—')}</div>
                        <div class="inv-emisor-inst">${Utils.esc(r.emisor?.institucion || '')}</div>
                        <div class="inv-grid">
                            <div><span class="inv-label">RIF:</span> <span class="inv-val">${Utils.esc(r.emisor?.rif || '—')}</span></div>
                            <div><span class="inv-label">NIT:</span> <span class="inv-val">${Utils.esc(r.emisor?.nit || '—')}</span></div>
                        </div>
                    </div>

                    <!-- CLIENTE -->
                    <div class="inv-section" style="background:rgba(45,125,210,0.03)">
                        <div class="inv-section-title">🆔 Datos del Cliente / Estudiante</div>
                        <div class="inv-info-box">
                            <div style="font-size:14px; font-weight:800; color:#fff">Nombre: ${Utils.esc(r.cliente?.nombre || '—')}</div>
                            <div class="inv-grid">
                                <div><span class="inv-label">Cédula:</span> <span class="inv-val">${Utils.esc(r.cliente?.cedula || '—')}</span></div>
                                <div><span class="inv-label">Carrera:</span> <span class="inv-val">${Utils.esc(r.cliente?.carrera || '—')}</span></div>
                            </div>
                        </div>
                    </div>

                    <!-- TRANSACCION -->
                    <div class="inv-section">
                        <div class="inv-section-title">🗓️ Detalles de la Transacción</div>
                        <div class="inv-grid">
                            <div><span class="inv-label">Nro. Factura:</span> <span class="inv-val">${Utils.esc(r.transaccion?.nroFactura || '—')}</span></div>
                            <div><span class="inv-label">Fecha:</span> <span class="inv-val">${Utils.esc(r.transaccion?.fecha || f.fecha)}</span></div>
                        </div>
                    </div>

                    <!-- DETALLE PAGO -->
                    <div class="inv-section">
                        <div class="inv-section-title">🛍️ Detalle de Pago</div>
                        <table class="inv-table">
                            <thead><tr><th>Concepto</th><th style="text-align:right">Monto</th></tr></thead>
                            <tbody>
                                ${r.items.map(it => `
                                <tr>
                                    <td>
                                        <div style="font-weight:700">${Utils.esc(it.concepto || it.name || 'Sin concepto')}</div>
                                        <div style="font-size:9px; color:#64748b">${it.fecha || ''}</div>
                                    </td>
                                    <td class="inv-amount-cell">${sym}${Utils.fmt(it.monto || it.price)}</td>
                                </tr>`).join('')}
                            </tbody>
                        </table>
                    </div>

                    <!-- RESUMEN -->
                    <div class="inv-resumen-box">
                        <span class="inv-label" style="font-size:12px">Total Pago</span>
                        <div class="inv-total-val">${sym}${Utils.fmt(f.total)}</div>
                    </div>

                    <div style="background:#000; padding:10px; text-align:center; font-size:10px; color:#4a5f80">
                        ${f.categoria === 'universidad' ? '🎓 UNIVERSIDAD - Expira en 120 días' : '🛒 MERCADO - Expira en 30 días'}
                    </div>
                </div>
                <button class="btn btn-primary" style="margin-top:15px; width:100%" onclick="Modal.close()">Cerrar</button>
            `);
            return;
        }

        // Fallback for legacy items
        Modal.show(`
            <div class="modal-title">🧾 ${Utils.esc(f.titulo)}</div>
            <div style="color:var(--text-secondary);font-size:15px; margin-bottom:15px">
                Total: <strong style="color:var(--gold)">${sym}${Utils.fmt(f.total)}</strong>
            </div>
            <button class="btn btn-primary" onclick="Modal.close()">Cerrar</button>`);
    },

    delFactura(idx) {
        Modal.confirm('¿Eliminar esta factura?', () => {
            const month    = Utils.monthKey();
            const facturas = Store.get('facturas_' + month, []);
            facturas.splice(idx, 1);
            Store.set('facturas_' + month, facturas);
            toast('Factura eliminada', 'delete');
            App.navigate('scanner');
        });
    }
};

// ─────────────────────────────────────────────
// MÓDULO 2: GASTOS
// ─────────────────────────────────────────────
const ViewGastos = {
    render() {
        const month = Utils.monthKey();
        const gastos = Store.get('gastos_' + month, []);
        const total  = gastos.reduce((a,g) => a + parseFloat(g.monto || 0), 0);
        const cats   = {};
        gastos.forEach(g => { cats[g.categoria] = (cats[g.categoria] || 0) + parseFloat(g.monto || 0); });
        const meses  = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Sep','Oct','Nov','Dic'];
        const now    = new Date();

        return `
        <div class="section-title anim-1">
            <span class="material-icons-outlined">receipt_long</span>
            Gastos del Mes
        </div>

        <div class="card card-danger-top anim-2" style="text-align:center;padding:20px">
            <div class="label">Total gastado — ${meses[now.getMonth()]} ${now.getFullYear()}</div>
            <div style="font-family:var(--font-title);font-size:44px;font-weight:700;color:var(--danger);margin:4px 0">${Utils.fmtCurrency(total)}</div>
            <div style="font-size:12px;color:var(--text-muted)">${gastos.length} registro(s) este mes</div>
        </div>

        ${Object.keys(cats).length > 0 ? `
        <div class="card anim-3">
            <div style="font-weight:600;margin-bottom:10px;font-size:14px">Por Categoría</div>
            ${Object.entries(cats).map(([cat,v]) => `
            <div style="margin-bottom:8px">
                <div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:3px">
                    <span>${this.catIcon(cat)} ${cat}</span>
                    <span style="color:var(--danger);font-weight:600">${Utils.fmtCurrency(v)}</span>
                </div>
                <div class="progress-bar-wrap" style="height:4px">
                    <div class="progress-bar" style="width:${Math.min(100,(v/total)*100)}%;background:var(--danger)"></div>
                </div>
            </div>`).join('')}
        </div>` : ''}

        <div class="card anim-4">
            <div style="font-weight:700;font-size:15px;margin-bottom:12px">Registros</div>
            ${gastos.length === 0 ? `
            <div class="empty-state" style="padding:20px">
                <span class="material-icons-outlined" style="font-size:36px">receipt</span>
                <span class="empty-sub">Sin gastos registrados este mes</span>
            </div>` : gastos.slice().reverse().map((g, ri) => {
                const i = gastos.length - 1 - ri;
                return `
            <div class="list-item">
                <div class="list-item-icon" style="background:rgba(239,68,68,0.1);color:var(--danger)">${this.catIcon(g.categoria)}</div>
                <div class="list-item-content">
                    <div class="list-item-title">${Utils.esc(g.desc)}</div>
                    <div class="list-item-sub">${g.categoria} · ${Utils.dateLabel(g.fecha)}</div>
                </div>
                <div style="display:flex;align-items:center;gap:8px">
                    <span style="font-weight:700;color:var(--danger)">${Utils.fmtCurrency(g.monto)}</span>
                    <button onclick="ViewGastos.del(${i})" style="width:28px;height:28px;border-radius:8px;background:rgba(239,68,68,0.1);color:var(--danger);border:1px solid rgba(239,68,68,0.2);cursor:pointer;display:flex;align-items:center;justify-content:center">
                        <span class="material-icons-outlined" style="font-size:14px">delete</span>
                    </button>
                </div>
            </div>`;}).join('')}
        </div>

        <button class="btn btn-primary anim-5" onclick="ViewGastos.showAdd()">
            <span class="material-icons-outlined">add</span> Agregar Gasto
        </button>`;
    },

    catIcon(c) {
        const icons = { Mercado:'🛒', Repuestos:'🔧', Bodega:'🏪', Comida:'🍽️', Transporte:'🚗', Salud:'💊', Entretenimiento:'🎬', Otro:'📦' };
        return icons[c] || '📦';
    },

    showAdd() {
        Modal.show(`
            <div class="modal-title">➕ Nuevo Gasto</div>
            <div class="form-group">
                <label class="form-label">Descripción</label>
                <input type="text" id="g-desc" placeholder="¿Qué compraste?">
            </div>
            <div class="form-group">
                <label class="form-label">Monto ($)</label>
                <input type="number" id="g-monto" placeholder="0.00" step="0.01" min="0">
            </div>
            <div class="form-group">
                <label class="form-label">Categoría</label>
                <select id="g-cat">
                    <option>Mercado</option><option>Repuestos</option><option>Bodega</option>
                    <option>Comida</option><option>Transporte</option><option>Salud</option>
                    <option>Entretenimiento</option><option>Otro</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="ViewGastos.save()">
                <span class="material-icons-outlined">save</span> Guardar Gasto
            </button>`);
    },

    save() {
        const desc  = (Utils.el('g-desc') || {}).value?.trim();
        const monto = parseFloat((Utils.el('g-monto') || {}).value || 0);
        const cat   = (Utils.el('g-cat') || {}).value;
        if (!desc || monto <= 0) { toast('Completa descripción y monto', 'warning'); return; }
        const month = Utils.monthKey();
        const gastos = Store.get('gastos_' + month, []);
        gastos.push({ desc, monto, categoria: cat, fecha: Utils.today() });
        Store.set('gastos_' + month, gastos);
        Modal.close();
        toast('Gasto registrado', 'check');
        App.navigate('gastos');
    },

    del(idx) {
        Modal.confirm('¿Eliminar este gasto?', () => {
            const month = Utils.monthKey();
            const gastos = Store.get('gastos_' + month, []);
            gastos.splice(idx, 1);
            Store.set('gastos_' + month, gastos);
            toast('Gasto eliminado', 'delete');
            App.navigate('gastos');
        });
    }
};

// ─────────────────────────────────────────────
// MÓDULO 3: CLIENTES
// ─────────────────────────────────────────────
const ViewClientes = {
    selectedClient: null,

    render() {
        if (this.selectedClient !== null) return this.renderClient();
        const clientes = Store.get('clientes', []);
        return `
        <div class="section-title anim-1">
            <span class="material-icons-outlined">people</span>
            Cartelera de Clientes
        </div>

        ${clientes.length === 0 ? `
        <div class="empty-state anim-2">
            <span class="material-icons-outlined">person_add</span>
            <span class="empty-title">Sin clientes aún</span>
            <span class="empty-sub">Agrega tu primer cliente para llevar control de tus trabajos</span>
        </div>` : clientes.map((c,i) => {
            const jobs = Store.get('client_jobs_' + c.id, []);
            const pendiente = jobs.filter(j => j.estado === 'pendiente').reduce((a,j) => a + parseFloat(j.monto||0), 0);
            const pagado    = jobs.filter(j => j.estado === 'pagado').reduce((a,j) => a + parseFloat(j.monto||0), 0);
            return `
            <div class="card anim-${Math.min(i+2,5)}" onclick="ViewClientes.openClient(${i})" style="cursor:pointer">
                <div style="display:flex;align-items:center;gap:12px">
                    <div class="client-avatar">${Utils.esc(c.nombre[0].toUpperCase())}</div>
                    <div style="flex:1;min-width:0">
                        <div style="font-weight:700;font-size:16px">${Utils.esc(c.nombre)}</div>
                        <div style="font-size:12px;color:var(--text-secondary)">${Utils.esc(c.oficio || 'Trabajador independiente')} · ${jobs.length} trabajo(s)</div>
                    </div>
                    <span class="material-icons-outlined" style="color:var(--text-muted)">chevron_right</span>
                </div>
                <div style="display:flex;gap:10px;margin-top:12px;padding-top:10px;border-top:1px solid var(--glass-border)">
                    <div style="flex:1;text-align:center">
                        <div style="font-size:11px;color:var(--text-muted)">Por cobrar</div>
                        <div style="font-weight:700;color:var(--warning)">${Utils.fmtCurrency(pendiente)}</div>
                    </div>
                    <div style="width:1px;background:var(--glass-border)"></div>
                    <div style="flex:1;text-align:center">
                        <div style="font-size:11px;color:var(--text-muted)">Cobrado</div>
                        <div style="font-weight:700;color:var(--success)">${Utils.fmtCurrency(pagado)}</div>
                    </div>
                </div>
                <button onclick="event.stopPropagation();ViewClientes.delClient(${i})" style="position:absolute;top:12px;right:36px;width:28px;height:28px;border-radius:8px;background:rgba(239,68,68,0.1);color:var(--danger);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center">
                    <span class="material-icons-outlined" style="font-size:14px">close</span>
                </button>
            </div>`;
        }).join('')}

        <button class="btn btn-primary anim-5" onclick="ViewClientes.showAddClient()">
            <span class="material-icons-outlined">person_add</span> Nuevo Cliente
        </button>`;
    },

    renderClient() {
        const clientes = Store.get('clientes', []);
        const c = clientes[this.selectedClient];
        if (!c) { this.selectedClient = null; return this.render(); }
        const jobs = Store.get('client_jobs_' + c.id, []);
        const pendienteTotal = jobs.filter(j => j.estado === 'pendiente').reduce((a,j) => a + parseFloat(j.monto||0), 0);
        const pagadoTotal    = jobs.filter(j => j.estado === 'pagado').reduce((a,j) => a + parseFloat(j.monto||0), 0);

        return `
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px" class="anim-1">
            <button onclick="ViewClientes.back()" style="width:36px;height:36px;border-radius:10px;background:var(--accent-soft);border:1px solid var(--glass-border);color:var(--accent-glow);cursor:pointer;display:flex;align-items:center;justify-content:center">
                <span class="material-icons-outlined">arrow_back</span>
            </button>
            <div class="client-avatar" style="width:48px;height:48px;font-size:22px">${Utils.esc(c.nombre[0].toUpperCase())}</div>
            <div>
                <div style="font-family:var(--font-title);font-size:20px;font-weight:700">${Utils.esc(c.nombre)}</div>
                <div style="font-size:12px;color:var(--text-secondary)">${Utils.esc(c.oficio || '')}</div>
            </div>
        </div>

        <div style="display:flex;gap:10px;margin-bottom:14px" class="anim-2">
            <div class="card" style="flex:1;text-align:center;padding:12px;margin-bottom:0">
                <div class="label">Por Cobrar</div>
                <div class="value warning" style="font-size:18px">${Utils.fmtCurrency(pendienteTotal)}</div>
            </div>
            <div class="card" style="flex:1;text-align:center;padding:12px;margin-bottom:0">
                <div class="label">Cobrado</div>
                <div class="value success" style="font-size:18px">${Utils.fmtCurrency(pagadoTotal)}</div>
            </div>
        </div>

        <div class="card anim-3">
            <div style="font-weight:700;font-size:15px;margin-bottom:12px">Planilla de Trabajos</div>
            ${jobs.length === 0 ? `<div class="empty-state" style="padding:16px"><span class="empty-sub">Sin trabajos registrados</span></div>` 
            : jobs.slice().reverse().map((j, ri) => {
                const idx = jobs.length - 1 - ri;
                return `
                <div class="job-entry">
                    <div class="job-left">
                        <div class="job-date">${Utils.dateLabel(j.fecha)}</div>
                        <div class="job-desc">${Utils.esc(j.descripcion)}</div>
                    </div>
                    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:6px">
                        <span class="job-amount">${Utils.fmtCurrency(j.monto)}</span>
                        <div style="display:flex;gap:4px">
                            ${j.estado === 'pendiente' ? `
                            <button onclick="ViewClientes.markPaid(${idx})" style="padding:4px 8px;border-radius:6px;background:rgba(34,197,94,0.1);color:var(--success);border:1px solid rgba(34,197,94,0.2);cursor:pointer;font-size:11px;font-family:var(--font-body)">✓ Pagado</button>` 
                            : `<span class="chip chip-success">✓ Cobrado</span>`}
                            <button onclick="ViewClientes.delJob(${idx})" style="width:26px;height:26px;border-radius:6px;background:rgba(239,68,68,0.1);color:var(--danger);border:1px solid rgba(239,68,68,0.2);cursor:pointer;display:flex;align-items:center;justify-content:center">
                                <span class="material-icons-outlined" style="font-size:13px">delete</span>
                            </button>
                        </div>
                    </div>
                </div>`; }).join('')}
        </div>

        <button class="btn btn-primary anim-4" onclick="ViewClientes.showAddJob()">
            <span class="material-icons-outlined">add</span> Registrar Trabajo
        </button>`;
    },

    back() { this.selectedClient = null; App.navigate('clientes'); },
    openClient(i) { this.selectedClient = i; App.renderCurrentView(); },

    showAddClient() {
        Modal.show(`
            <div class="modal-title">👤 Nuevo Cliente</div>
            <div class="form-group">
                <label class="form-label">Nombre del Cliente</label>
                <input type="text" id="c-nombre" placeholder="Ej: Mario González">
            </div>
            <div class="form-group">
                <label class="form-label">Oficio / Especialidad</label>
                <input type="text" id="c-oficio" placeholder="Ej: Refrigeración, Construcción...">
            </div>
            <button class="btn btn-primary" onclick="ViewClientes.saveClient()">
                <span class="material-icons-outlined">save</span> Guardar Cliente
            </button>`);
    },

    saveClient() {
        const nombre = (Utils.el('c-nombre') || {}).value?.trim();
        const oficio = (Utils.el('c-oficio') || {}).value?.trim();
        if (!nombre) { toast('Ingresa el nombre del cliente', 'warning'); return; }
        const clientes = Store.get('clientes', []);
        clientes.push({ id: Utils.uid(), nombre, oficio });
        Store.set('clientes', clientes);
        Modal.close();
        toast('Cliente agregado', 'person_add');
        App.navigate('clientes');
    },

    delClient(i) {
        Modal.confirm('¿Eliminar este cliente y todos sus trabajos?', () => {
            const clientes = Store.get('clientes', []);
            Store.del('client_jobs_' + clientes[i].id);
            clientes.splice(i, 1);
            Store.set('clientes', clientes);
            toast('Cliente eliminado', 'delete');
            this.selectedClient = null;
            App.navigate('clientes');
        });
    },

    showAddJob() {
        Modal.show(`
            <div class="modal-title">📋 Registrar Trabajo</div>
            <div class="form-group">
                <label class="form-label">Fecha</label>
                <input type="date" id="j-fecha" value="${Utils.today()}">
            </div>
            <div class="form-group">
                <label class="form-label">Descripción del Trabajo</label>
                <textarea id="j-desc" rows="3" placeholder="Ej: Instalación de aire acondicionado..."></textarea>
            </div>
            <div class="form-group">
                <label class="form-label">Cobrado ($)</label>
                <input type="number" id="j-monto" placeholder="0.00" step="0.01" min="0">
            </div>
            <div class="form-group">
                <label class="form-label">Estado de Pago</label>
                <select id="j-estado">
                    <option value="pendiente">⏳ En Espera</option>
                    <option value="pagado">✅ Ya Pagó</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="ViewClientes.saveJob()">
                <span class="material-icons-outlined">save</span> Guardar Trabajo
            </button>`);
    },

    saveJob() {
        const desc   = (Utils.el('j-desc') || {}).value?.trim();
        const monto  = parseFloat((Utils.el('j-monto') || {}).value || 0);
        const fecha  = (Utils.el('j-fecha') || {}).value;
        const estado = (Utils.el('j-estado') || {}).value;
        if (!desc || monto <= 0) { toast('Completa la descripción y el monto', 'warning'); return; }
        const clientes = Store.get('clientes', []);
        const c = clientes[this.selectedClient];
        const jobs = Store.get('client_jobs_' + c.id, []);
        jobs.push({ id: Utils.uid(), descripcion: desc, monto, fecha, estado });
        Store.set('client_jobs_' + c.id, jobs);
        Modal.close();
        toast('Trabajo registrado', 'check');
        App.renderCurrentView();
    },

    markPaid(idx) {
        const clientes = Store.get('clientes', []);
        const c = clientes[this.selectedClient];
        const jobs = Store.get('client_jobs_' + c.id, []);
        jobs[idx].estado = 'pagado';
        Store.set('client_jobs_' + c.id, jobs);
        toast('¡Marcado como cobrado! 💰', 'check_circle');
        App.renderCurrentView();
    },

    delJob(idx) {
        Modal.confirm('¿Eliminar este trabajo?', () => {
            const clientes = Store.get('clientes', []);
            const c = clientes[this.selectedClient];
            const jobs = Store.get('client_jobs_' + c.id, []);
            jobs.splice(idx, 1);
            Store.set('client_jobs_' + c.id, jobs);
            toast('Trabajo eliminado', 'delete');
            App.renderCurrentView();
        });
    }
};

// ─────────────────────────────────────────────
// MÓDULO 4: CRÉDITOS
// ─────────────────────────────────────────────
const ViewCreditos = {
    render() {
        const creditos = Store.get('creditos', []);
        const activos  = creditos.map((c, i) => ({ ...c, originalIndex: i })).filter(c => !c.pagado);
        const terminados = creditos.map((c, i) => ({ ...c, originalIndex: i })).filter(c => c.pagado);
        const totalMes  = activos.reduce((a,c) => a + parseFloat(c.cuotaMensual||0), 0);

        return `
        <div class="section-title anim-1">
            <span class="material-icons-outlined">credit_card</span>
            Mis Créditos
        </div>

        ${activos.length > 0 ? `
        <div class="card card-gold-top anim-2" style="text-align:center;padding:18px">
            <div class="label">Total a Pagar Este Mes</div>
            <div style="font-family:var(--font-title);font-size:40px;font-weight:700;color:var(--gold)">${Utils.fmtCurrency(totalMes)}</div>
            <div style="font-size:12px;color:var(--text-muted)">${activos.length} crédito(s) activo(s)</div>
        </div>

        <div class="alert-box alert-info anim-3">
            <span class="material-icons-outlined" style="font-size:20px">alarm</span>
            <span>Recordatorio diario programado a las <strong>8:00 AM</strong>. Gestiona tus pagos a tiempo.</span>
        </div>` : ''}

        ${activos.length === 0 && terminados.length === 0 ? `
        <div class="empty-state anim-2">
            <span class="material-icons-outlined">credit_score</span>
            <span class="empty-title">Sin créditos registrados</span>
            <span class="empty-sub">Anota tus compras a crédito para no perder el control</span>
        </div>` : ''}

        ${activos.map((c,i) => {
            const pagado = parseFloat(c.pagado2 || 0);
            const total  = parseFloat(c.costoTotal || 0);
            const pct    = total > 0 ? Math.min(100, (pagado/total*100)) : 0;
            return `
            <div class="card card-warning-top anim-${Math.min(i+3,5)}">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div style="flex:1; min-width:0">
                        <div style="font-weight:700;font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">${Utils.esc(c.nombre)}</div>
                        <div style="font-size:12px;color:var(--text-secondary);margin-top:2px">Cuota: <strong style="color:var(--gold)">${Utils.fmtCurrency(c.cuotaMensual)}</strong></div>
                    </div>
                    <div style="display:flex;gap:6px">
                        <button onclick="ViewCreditos.abonar(${c.originalIndex})" class="btn-icon-text">
                            <span class="material-icons-outlined" style="font-size:16px">payments</span>
                        </button>
                        <button onclick="ViewCreditos.markComplete(${c.originalIndex})" class="btn-icon-text" style="color:var(--success)">
                            <span class="material-icons-outlined" style="font-size:16px">done_all</span>
                        </button>
                        <button onclick="ViewCreditos.del(${c.originalIndex})" class="btn-icon-text" style="color:var(--danger)">
                            <span class="material-icons-outlined" style="font-size:16px">delete</span>
                        </button>
                    </div>
                </div>
                <div style="margin-top:12px">
                    <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px">
                        <span style="color:var(--text-muted)">Progreso de pago</span>
                        <span style="color:var(--gold)">${Utils.fmtCurrency(pagado)} / ${Utils.fmtCurrency(total)}</span>
                    </div>
                    <div class="progress-bar-wrap" style="height:8px">
                        <div class="progress-bar" style="width:${pct}%;background:var(--gold)"></div>
                    </div>
                    <div style="font-size:11px;color:var(--text-muted);margin-top:3px">${pct.toFixed(0)}% pagado</div>
                </div>
            </div>`; }).join('')}

        ${terminados.length > 0 ? `
        <div class="card anim-5" style="opacity:0.9">
            <div style="font-weight:600;font-size:13px;color:var(--text-secondary);margin-bottom:10px">✅ Créditos Completados</div>
            ${terminados.map(c => `
            <div class="list-item">
                <div class="list-item-icon" style="background:rgba(34,197,94,0.1);color:var(--success)">
                    <span class="material-icons-outlined">check_circle</span>
                </div>
                <div class="list-item-content">
                    <div class="list-item-title">${Utils.esc(c.nombre)}</div>
                    <div class="list-item-sub">Total pagado: ${Utils.fmtCurrency(c.costoTotal)}</div>
                </div>
                <div style="display:flex;gap:4px;align-items:center">
                    <span class="chip chip-success">Listo</span>
                    <button onclick="ViewCreditos.del(${c.originalIndex})" style="width:30px;height:30px;border-radius:8px;background:rgba(239,68,68,0.1);color:var(--danger);border:none;cursor:pointer;display:flex;align-items:center;justify-content:center">
                        <span class="material-icons-outlined" style="font-size:16px">delete</span>
                    </button>
                </div>
            </div>`).join('')}
        </div>` : ''}

        <button class="btn btn-primary anim-5" onclick="ViewCreditos.showAdd()">
            <span class="material-icons-outlined">add_card</span> Agregar Crédito
        </button>`;
    },

    showAdd() {
        Modal.show(`
            <div class="modal-title">💳 Nuevo Crédito</div>
            <div class="form-group">
                <label class="form-label">Nombre del artículo / servicio</label>
                <input type="text" id="cr-nombre" placeholder="Ej: Televisor Samsung">
            </div>
            <div class="form-group">
                <label class="form-label">Costo Total ($)</label>
                <input type="number" id="cr-total" placeholder="300.00" step="0.01" min="0">
            </div>
            <div class="form-group">
                <label class="form-label">Cuota Mensual ($)</label>
                <input type="number" id="cr-cuota" placeholder="50.00" step="0.01" min="0">
            </div>
            <div class="form-group">
                <label class="form-label">Fecha de Inicio</label>
                <input type="date" id="cr-fecha" value="${Utils.today()}">
            </div>
            <button class="btn btn-primary" onclick="ViewCreditos.save()">
                <span class="material-icons-outlined">save</span> Guardar Crédito
            </button>`);
    },

    save() {
        const nombre     = (Utils.el('cr-nombre') || {}).value?.trim();
        const costoTotal = parseFloat((Utils.el('cr-total') || {}).value || 0);
        const cuotaMensual = parseFloat((Utils.el('cr-cuota') || {}).value || 0);
        const fecha      = (Utils.el('cr-fecha') || {}).value;
        if (!nombre || costoTotal <= 0 || cuotaMensual <= 0) { toast('Completa los campos correctamente', 'warning'); return; }
        const creditos = Store.get('creditos', []);
        creditos.push({ id: Utils.uid(), nombre, costoTotal, cuotaMensual, fecha, pagado: false, pagado2: 0 });
        Store.set('creditos', creditos);
        Modal.close();
        toast('Crédito registrado', 'credit_card');
        App.navigate('creditos');
    },

    abonar(idx) {
        const creditos = Store.get('creditos', []);
        const c = creditos[idx];
        if (!c) return;
        const pendiente = c.costoTotal - (c.pagado2 || 0);

        Modal.show(`
            <div class="modal-title">💰 Abonar Pago</div>
            <p style="font-size:12px; color:var(--text-secondary); margin-bottom:15px">Crédito: <strong>${Utils.esc(c.nombre)}</strong><br>Pendiente: ${Utils.fmtCurrency(pendiente)}</p>
            <div class="form-group">
                <label class="form-label">Monto a Abonar ($)</label>
                <input type="number" id="ab-monto" placeholder="${Utils.fmt(c.cuotaMensual)}" value="${Utils.fmt(c.cuotaMensual)}" step="0.01" min="0">
            </div>
            <button class="btn btn-primary" onclick="ViewCreditos.doAbonar(${idx})">
                <span class="material-icons-outlined">payments</span> Registrar Abono
            </button>`);
    },

    doAbonar(idx) {
        const monto = parseFloat((Utils.el('ab-monto') || {}).value || 0);
        if (monto <= 0) { toast('Ingresa un monto válido', 'warning'); return; }
        const creditos = Store.get('creditos', []);
        if (!creditos[idx]) return;

        creditos[idx].pagado2 = (parseFloat(creditos[idx].pagado2 || 0)) + monto;
        
        // Auto-completar si el pago cubre el total
        if (creditos[idx].pagado2 >= creditos[idx].costoTotal - 0.01) {
            creditos[idx].pagado2 = creditos[idx].costoTotal;
            creditos[idx].pagado = true;
            toast('🎉 ¡Crédito completamente pagado!', 'celebration');
        } else {
            toast(`Abono de ${Utils.fmtCurrency(monto)} registrado`, 'payments');
        }
        
        Store.set('creditos', creditos);
        Modal.close();
        App.navigate('creditos');
    },

    markComplete(idx) {
        Modal.confirm('¿Marcar este crédito como pagado al 100%?', () => {
            const creditos = Store.get('creditos', []);
            if (!creditos[idx]) return;
            creditos[idx].pagado = true;
            creditos[idx].pagado2 = creditos[idx].costoTotal;
            Store.set('creditos', creditos);
            toast('🎉 ¡Felicidades! Crédito cerrado.', 'celebration');
            App.navigate('creditos');
        });
    },

    del(idx) {
        Modal.confirm('¿Estás seguro de eliminar este crédito? Esta acción no se puede deshacer.', () => {
            const creditos = Store.get('creditos', []);
            creditos.splice(idx, 1);
            Store.set('creditos', creditos);
            toast('Crédito eliminado', 'delete');
            App.navigate('creditos');
        });
    }
};

// ─────────────────────────────────────────────
// MÓDULO 5: AHORROS
// ─────────────────────────────────────────────
const ViewAhorros = {
    render() {
        const ahorros = Store.get('ahorros', { total: 0, meta: 0, historial: [] });
        const pct = ahorros.meta > 0 ? Math.min(100, (ahorros.total / ahorros.meta) * 100) : 0;

        return `
        <div class="section-title anim-1">
            <span class="material-icons-outlined">savings</span>
            Mis Ahorros
        </div>

        <div class="card card-gold-top anim-2">
            <div class="savings-circle">
                <div class="savings-amount">${Utils.fmtCurrency(ahorros.total)}</div>
                <div class="savings-label">Total Ahorrado</div>
                ${ahorros.meta > 0 ? `
                <div class="savings-meta">
                    <div class="meta-item">
                        <div class="meta-val" style="color:var(--gold)">${pct.toFixed(0)}%</div>
                        <div class="meta-key">de la meta</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-val" style="color:var(--success)">${Utils.fmtCurrency(ahorros.meta)}</div>
                        <div class="meta-key">Meta</div>
                    </div>
                    <div class="meta-item">
                        <div class="meta-val" style="color:var(--accent-glow)">${Utils.fmtCurrency(Math.max(0,ahorros.meta - ahorros.total))}</div>
                        <div class="meta-key">Restante</div>
                    </div>
                </div>` : ''}
            </div>
            ${ahorros.meta > 0 ? `
            <div>
                <div class="progress-bar-wrap" style="height:10px">
                    <div class="progress-bar" style="width:${pct}%;background:linear-gradient(90deg,var(--gold),#f59e0b)"></div>
                </div>
                <div style="font-size:12px;color:var(--text-muted);margin-top:6px;text-align:center">${pct.toFixed(1)}% hacia tu meta 🏠</div>
            </div>` : ''}
        </div>

        <div style="display:flex;gap:10px;margin-bottom:14px" class="anim-3">
            <button class="btn btn-success" onclick="ViewAhorros.showDeposit()" style="flex:1">
                <span class="material-icons-outlined">add</span> Ahorré
            </button>
            <button class="btn btn-danger" onclick="ViewAhorros.showWithdraw()" style="flex:1">
                <span class="material-icons-outlined">remove</span> Gasté
            </button>
            <button class="btn" onclick="ViewAhorros.showMeta()" style="flex:0.6;background:var(--accent-soft);border:1px solid var(--glass-border);color:var(--accent-glow)">
                <span class="material-icons-outlined">flag</span>
            </button>
        </div>

        <div class="card anim-4">
            <div style="font-weight:700;font-size:15px;margin-bottom:12px">Historial</div>
            ${(ahorros.historial || []).length === 0 ? `
            <div class="empty-state" style="padding:16px">
                <span class="empty-sub">Sin movimientos aún</span>
            </div>` : (ahorros.historial || []).slice().reverse().slice(0,20).map(h => `
            <div class="list-item">
                <div class="list-item-icon" style="background:${h.tipo === 'deposito' ? 'rgba(34,197,94,0.1)' : 'rgba(239,68,68,0.1)'};color:${h.tipo === 'deposito' ? 'var(--success)' : 'var(--danger)'}">
                    <span class="material-icons-outlined">${h.tipo === 'deposito' ? 'arrow_upward' : 'arrow_downward'}</span>
                </div>
                <div class="list-item-content">
                    <div class="list-item-title">${Utils.esc(h.nota || (h.tipo === 'deposito' ? 'Ahorro' : 'Gasto de ahorro'))}</div>
                    <div class="list-item-sub">${Utils.dateLabel(h.fecha)}</div>
                </div>
                <div class="list-item-right">
                    <span style="font-weight:700;color:${h.tipo === 'deposito' ? 'var(--success)' : 'var(--danger)'}">
                        ${h.tipo === 'deposito' ? '+' : '-'}${Utils.fmtCurrency(h.monto)}
                    </span>
                </div>
            </div>`).join('')}
        </div>`;
    },

    showDeposit() {
        Modal.show(`
            <div class="modal-title">💰 Registrar Ahorro</div>
            <div class="form-group">
                <label class="form-label">Monto que ahorré ($)</label>
                <input type="number" id="ah-monto" placeholder="0.00" step="0.01" min="0">
            </div>
            <div class="form-group">
                <label class="form-label">Nota (opcional)</label>
                <input type="text" id="ah-nota" placeholder="Ej: Quincena, bono...">
            </div>
            <button class="btn btn-success" onclick="ViewAhorros.doMove('deposito')">
                <span class="material-icons-outlined">savings</span> Guardar Ahorro
            </button>`);
    },

    showWithdraw() {
        Modal.show(`
            <div class="modal-title">💸 Registrar Gasto de Ahorro</div>
            <div class="form-group">
                <label class="form-label">Monto que gasté ($)</label>
                <input type="number" id="ah-monto" placeholder="0.00" step="0.01" min="0">
            </div>
            <div class="form-group">
                <label class="form-label">Motivo</label>
                <input type="text" id="ah-nota" placeholder="Ej: Emergencia, pago de servicio...">
            </div>
            <button class="btn btn-danger" onclick="ViewAhorros.doMove('retiro')">
                <span class="material-icons-outlined">remove_circle</span> Registrar Gasto
            </button>`);
    },

    showMeta() {
        const a = Store.get('ahorros', { total: 0, meta: 0, historial: [] });
        Modal.show(`
            <div class="modal-title">🏠 Definir Meta de Ahorro</div>
            <div class="form-group">
                <label class="form-label">Mi meta es ($)</label>
                <input type="number" id="ah-meta" placeholder="Ej: 5000" step="1" min="0" value="${a.meta || ''}">
            </div>
            <div class="alert-box alert-info" style="font-size:12px"><span class="material-icons-outlined" style="font-size:16px">lightbulb</span>Ej: Casa propia, carro, electrónico...</div>
            <button class="btn btn-primary" onclick="ViewAhorros.saveMeta()">
                <span class="material-icons-outlined">flag</span> Guardar Meta
            </button>`);
    },

    saveMeta() {
        const meta = parseFloat((Utils.el('ah-meta') || {}).value || 0);
        if (meta <= 0) { toast('Ingresa una meta válida', 'warning'); return; }
        const a = Store.get('ahorros', { total: 0, meta: 0, historial: [] });
        a.meta = meta;
        Store.set('ahorros', a);
        Modal.close();
        toast('Meta de ahorro guardada 🏠', 'flag');
        App.navigate('ahorros');
    },

    doMove(tipo) {
        const monto = parseFloat((Utils.el('ah-monto') || {}).value || 0);
        const nota  = (Utils.el('ah-nota') || {}).value?.trim();
        if (monto <= 0) { toast('Ingresa un monto válido', 'warning'); return; }
        const a = Store.get('ahorros', { total: 0, meta: 0, historial: [] });
        if (tipo === 'deposito') {
            a.total += monto;
        } else {
            if (monto > a.total) { toast('No tienes suficientes ahorros', 'warning'); return; }
            a.total -= monto;
        }
        if (!a.historial) a.historial = [];
        a.historial.push({ tipo, monto, nota, fecha: Utils.today() });
        Store.set('ahorros', a);
        Modal.close();
        toast(tipo === 'deposito' ? `¡Ahorraste ${Utils.fmtCurrency(monto)}! 💪` : `Gasto registrado`, tipo === 'deposito' ? 'savings' : 'payments');
        App.navigate('ahorros');
    }
};

// ─────────────────────────────────────────────
// MÓDULO 6: HORARIOS
// ─────────────────────────────────────────────
const ViewHorarios = {
    render() {
        const config = Store.get('horario_config', null);
        if (!config) return this.renderSetup();
        return this.renderSchedule(config);
    },

    renderSetup() {
        return `
        <div class="section-title anim-1">
            <span class="material-icons-outlined">schedule</span>
            Planificación de Horario
        </div>

        <div class="alert-box alert-info anim-2">
            <span class="material-icons-outlined" style="font-size:20px">lightbulb</span>
            <span>Configura tu horario una vez y VeloApp creará tu planificación perfecta, incluyendo tiempo para comer en casa.</span>
        </div>

        <div class="card anim-3">
            <div style="font-weight:700;font-size:16px;margin-bottom:14px">Configurar Mi Horario</div>
            <div class="form-group">
                <label class="form-label">¿A qué hora empiezas a trabajar?</label>
                <input type="time" id="h-inicio" value="07:00">
            </div>
            <div class="form-group">
                <label class="form-label">¿A qué hora terminas?</label>
                <input type="time" id="h-fin" value="17:00">
            </div>
            <div class="form-group">
                <label class="form-label">¿Cuál es tu trabajo principal?</label>
                <select id="h-oficio">
                    <option>Refrigeración / Aire Acondicionado</option>
                    <option>Construcción / Albañilería</option>
                    <option>Electricidad</option>
                    <option>Mecánica / Automotriz</option>
                    <option>Plomería</option>
                    <option>Carpintería</option>
                    <option>Transporte / Delivery</option>
                    <option>Otro</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">¿Llegas al mediodía? (tiempo para cocinar)</label>
                <select id="h-cocina">
                    <option value="si">Sí, puedo llegar a comer en casa</option>
                    <option value="no">No, como en la calle</option>
                </select>
            </div>
            <button class="btn btn-primary" onclick="ViewHorarios.generateSchedule()">
                <span class="material-icons-outlined">auto_fix_high</span> Generar Mi Horario
            </button>
        </div>`;
    },

    generateSchedule() {
        const inicio = (Utils.el('h-inicio') || {}).value;
        const fin    = (Utils.el('h-fin') || {}).value;
        const oficio = (Utils.el('h-oficio') || {}).value;
        const cocina = (Utils.el('h-cocina') || {}).value;
        if (!inicio || !fin) { toast('Completa los horarios', 'warning'); return; }
        const config = { inicio, fin, oficio, cocina };
        Store.set('horario_config', config);
        toast('¡Horario generado exitosamente! 📅', 'schedule');
        App.navigate('horarios');
    },

    renderSchedule(cfg) {
        const slots = this.buildSlots(cfg);
        const [hIni] = cfg.inicio.split(':').map(Number);
        const bedHour = hIni <= 7 ? 20 : 22; // Si llega temprano, dormir a las 8 PM hora Venezuela

        return `
        <div class="section-title anim-1">
            <span class="material-icons-outlined">schedule</span>
            Mi Horario Diario
        </div>

        <div class="card card-accent-top anim-2">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                <div>
                    <div style="font-weight:700;font-size:15px">${Utils.esc(cfg.oficio)}</div>
                    <div style="font-size:12px;color:var(--text-secondary)">${cfg.inicio} — ${cfg.fin}</div>
                </div>
                <button onclick="Store.del('horario_config');App.navigate('horarios')" style="padding:6px 10px;border-radius:8px;background:var(--accent-soft);color:var(--accent-glow);border:1px solid var(--glass-border);cursor:pointer;font-size:12px;font-family:var(--font-body)">Cambiar</button>
            </div>
        </div>

        ${cfg.cocina === 'no' ? `
        <div class="alert-box alert-warning anim-3">
            <span class="material-icons-outlined" style="font-size:20px">restaurant</span>
            <span>💡 <strong>Consejo:</strong> Cocinar en casa te ahorra dinero. Si puedes organizarte para volver al mediodía, ahorrarás significativamente al mes.</span>
        </div>` : ''}

        <div class="card anim-3">
            <div style="font-weight:700;font-size:15px;margin-bottom:14px">📅 Planificación del Día</div>
            ${slots.map(s => `
            <div class="schedule-slot">
                <div class="slot-time">${s.hora}</div>
                <div class="slot-bar ${s.activo ? 'active' : ''}"></div>
                <div class="slot-content">
                    <div class="slot-title">${s.emoji} ${Utils.esc(s.titulo)}</div>
                    ${s.sub ? `<div class="slot-sub">${Utils.esc(s.sub)}</div>` : ''}
                </div>
            </div>`).join('')}
        </div>

        <div class="alert-box alert-success anim-4">
            <span class="material-icons-outlined" style="font-size:20px">bedtime</span>
            <span>🌙 Hora recomendada para dormir: <strong>${bedHour}:00 PM</strong> hora Venezuela. Descanso completo = mejor rendimiento laboral.</span>
        </div>`;
    },

    buildSlots(cfg) {
        const [hI] = cfg.inicio.split(':').map(Number);
        const [hF] = cfg.fin.split(':').map(Number);
        const cocina = cfg.cocina === 'si';
        const earlyStart = hI <= 7;
        const slots = [];

        if (earlyStart) slots.push({ hora: '05:30', emoji: '⏰', titulo: 'Despertar', sub: 'Levantarse con tiempo', activo: false });
        slots.push({ hora: earlyStart ? '06:00' : `${String(hI-1).padStart(2,'0')}:00`, emoji: '🌅', titulo: 'Preparación', sub: 'Aseo personal y desayuno en casa', activo: false });
        slots.push({ hora: cfg.inicio, emoji: '🔨', titulo: `Inicio de trabajo — ${cfg.oficio}`, sub: 'Comenzar puntual y con energía', activo: true });

        const midHour = Math.floor((hI + hF) / 2);
        if (cocina) {
            slots.push({ hora: `${String(midHour).padStart(2,'0')}:00`, emoji: '🏠', titulo: 'Pausa — Ir a casa a comer', sub: 'Cocinar en casa ahorra dinero y tiempo', activo: false });
            slots.push({ hora: `${String(midHour+1).padStart(2,'0')}:00`, emoji: '🔨', titulo: 'Retomar trabajo', sub: 'Segunda jornada del día', activo: true });
        } else {
            slots.push({ hora: `${String(midHour).padStart(2,'0')}:00`, emoji: '🍽️', titulo: 'Hora de almuerzo', sub: 'Tómate 30min para comer bien', activo: false });
        }

        slots.push({ hora: cfg.fin, emoji: '✅', titulo: 'Fin de jornada', sub: 'Registrar trabajos e ingresos del día', activo: false });
        slots.push({ hora: `${String(hF+1).padStart(2,'0')}:00`, emoji: '🚿', titulo: 'Descanso personal', sub: 'Aseo y tiempo familiar', activo: false });

        const bedH = earlyStart ? 20 : 22;
        if (hF < bedH - 1) {
            slots.push({ hora: `${String(bedH-1).padStart(2,'0')}:00`, emoji: '📱', titulo: 'Revisión de finanzas', sub: 'Revisar gastos e ingresos del día en VeloApp', activo: false });
        }
        slots.push({ hora: `${String(bedH).padStart(2,'0')}:00`, emoji: '🌙', titulo: 'Hora de dormir', sub: earlyStart ? 'Descanso necesario — comienzas temprano' : 'Buen descanso para mañana', activo: false });

        return slots;
    }
};

// ─────────────────────────────────────────────
// MÓDULO 7: INGRESOS
// ─────────────────────────────────────────────
const ViewIngresos = {
    render() {
        const config  = Store.get('ingreso_config', null);
        const month   = Utils.monthKey();
        const ingresos = Store.get('ingresos_' + month, []);
        const total    = ingresos.reduce((a,i) => a + parseFloat(i.monto || 0), 0);
        const meses    = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Sep','Oct','Nov','Dic'];
        const now      = new Date();

        return `
        <div class="section-title anim-1">
            <span class="material-icons-outlined">attach_money</span>
            Mis Ingresos
        </div>

        ${!config ? `
        <div class="card card-accent-top anim-2">
            <div style="font-weight:700;font-size:16px;margin-bottom:12px">⚙️ Configurar Tarifa</div>
            <div class="form-group">
                <label class="form-label">¿A qué te dedicas?</label>
                <select id="ing-oficio">
                    <option>Refrigeración / Aire Acondicionado</option>
                    <option>Construcción / Albañilería</option>
                    <option>Electricidad</option>
                    <option>Mecánica / Automotriz</option>
                    <option>Plomería</option>
                    <option>Carpintería</option>
                    <option>Otro</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">¿Cuánto cobras por servicio/unidad? ($)</label>
                <input type="number" id="ing-tarifa" placeholder="Ej: 30 por equipo de A/C" step="0.01" min="0">
            </div>
            <button class="btn btn-primary" onclick="ViewIngresos.saveConfig()">
                <span class="material-icons-outlined">save</span> Guardar Configuración
            </button>
        </div>` : `
        <div class="card anim-2" style="display:flex;align-items:center;justify-content:space-between;padding:12px 16px">
            <div>
                <div style="font-size:12px;color:var(--text-muted)">Tarifa configurada</div>
                <div style="font-weight:700">${Utils.esc(config.oficio)} · ${Utils.fmtCurrency(config.tarifa)}/servicio</div>
            </div>
            <button onclick="Store.del('ingreso_config');App.navigate('ingresos')" style="padding:6px 10px;border-radius:8px;background:var(--accent-soft);color:var(--accent-glow);border:1px solid var(--glass-border);cursor:pointer;font-size:12px;font-family:var(--font-body)">Cambiar</button>
        </div>`}

        <div class="card card-success-top anim-3" style="text-align:center;padding:20px">
            <div class="label">Total Ganado — ${meses[now.getMonth()]} ${now.getFullYear()}</div>
            <div class="income-total">${Utils.fmtCurrency(total)}</div>
            <div style="font-size:12px;color:var(--text-muted)">${ingresos.length} servicio(s) este mes</div>
        </div>

        <div class="card anim-4">
            <div style="font-weight:700;font-size:15px;margin-bottom:12px">Registros del Mes</div>
            ${ingresos.length === 0 ? `
            <div class="empty-state" style="padding:16px">
                <span class="empty-sub">Registra lo que cobraste hoy</span>
            </div>` : ingresos.slice().reverse().map((ing, ri) => {
                const i = ingresos.length - 1 - ri;
                return `
            <div class="list-item">
                <div class="list-item-icon" style="background:rgba(34,197,94,0.1);color:var(--success)">
                    <span class="material-icons-outlined">payments</span>
                </div>
                <div class="list-item-content">
                    <div class="list-item-title">${Utils.esc(ing.desc)}</div>
                    <div class="list-item-sub">${Utils.esc(ing.categoria || '')} · ${Utils.dateLabel(ing.fecha)}</div>
                </div>
                <div style="display:flex;align-items:center;gap:8px">
                    <span style="font-weight:700;color:var(--success)">${Utils.fmtCurrency(ing.monto)}</span>
                    <button onclick="ViewIngresos.del(${i})" style="width:28px;height:28px;border-radius:8px;background:rgba(239,68,68,0.1);color:var(--danger);border:1px solid rgba(239,68,68,0.2);cursor:pointer;display:flex;align-items:center;justify-content:center">
                        <span class="material-icons-outlined" style="font-size:14px">delete</span>
                    </button>
                </div>
            </div>`; }).join('')}
        </div>

        <button class="btn btn-success anim-5" onclick="ViewIngresos.showAdd()">
            <span class="material-icons-outlined">add</span> Registrar Cobro de Hoy
        </button>`;
    },

    saveConfig() {
        const oficio  = (Utils.el('ing-oficio') || {}).value;
        const tarifa  = parseFloat((Utils.el('ing-tarifa') || {}).value || 0);
        if (tarifa <= 0) { toast('Ingresa tu tarifa por servicio', 'warning'); return; }
        Store.set('ingreso_config', { oficio, tarifa });
        toast('Tarifa guardada', 'check');
        App.navigate('ingresos');
    },

    showAdd() {
        const config = Store.get('ingreso_config', null);
        Modal.show(`
            <div class="modal-title">💵 Registrar Cobro</div>
            <div class="form-group">
                <label class="form-label">¿Qué hiciste hoy?</label>
                <select id="ing-tipo">
                    <option>Instalación de A/C</option>
                    <option>Mantenimiento de equipo</option>
                    <option>Reparación</option>
                    <option>Trabajo de construcción</option>
                    <option>Instalación eléctrica</option>
                    <option>Servicio mecánico</option>
                    <option>Plomería</option>
                    <option>Otro servicio</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Descripción</label>
                <input type="text" id="ing-desc" placeholder="Ej: Instalé un A/C en el sector Las Mercedes">
            </div>
            <div class="form-group">
                <label class="form-label">Monto cobrado ($)</label>
                <input type="number" id="ing-monto" placeholder="${config ? Utils.fmt(config.tarifa) : '0.00'}" step="0.01" min="0" value="${config ? config.tarifa : ''}">
            </div>
            <button class="btn btn-success" onclick="ViewIngresos.save()">
                <span class="material-icons-outlined">payments</span> Guardar Cobro
            </button>`);
    },

    save() {
        const tipo  = (Utils.el('ing-tipo') || {}).value;
        const desc  = (Utils.el('ing-desc') || {}).value?.trim();
        const monto = parseFloat((Utils.el('ing-monto') || {}).value || 0);
        if (!desc || monto <= 0) { toast('Completa descripción y monto', 'warning'); return; }
        const month = Utils.monthKey();
        const ingresos = Store.get('ingresos_' + month, []);
        ingresos.push({ desc: desc || tipo, monto, categoria: tipo, fecha: Utils.today() });
        Store.set('ingresos_' + month, ingresos);
        Modal.close();
        toast(`¡Cobro de ${Utils.fmtCurrency(monto)} registrado! 💪`, 'payments');
        App.navigate('ingresos');
    },

    del(idx) {
        Modal.confirm('¿Eliminar este cobro?', () => {
            const month = Utils.monthKey();
            const ingresos = Store.get('ingresos_' + month, []);
            ingresos.splice(idx, 1);
            Store.set('ingresos_' + month, ingresos);
            toast('Registro eliminado', 'delete');
            App.navigate('ingresos');
        });
    }
};

// ══════════════════════════════════════════════
// ROUTER / APP PRINCIPAL
// ══════════════════════════════════════════════
const App = {
    currentView: 'home',
    views: {
        home:     ViewHome,
        scanner:  ViewScanner,
        gastos:   ViewGastos,
        clientes: ViewClientes,
        creditos: ViewCreditos,
        ahorros:  ViewAhorros,
        horarios: ViewHorarios,
        ingresos: ViewIngresos
    },

    init() {
        // Update date display
        const opts = { weekday: 'long', day: 'numeric', month: 'long' };
        Utils.el('current-date').textContent = new Date().toLocaleDateString('es-VE', opts);

        // Navigation buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const target = btn.getAttribute('data-view');
                if (target) this.navigate(target);
            });
        });

        // Home button
        Utils.el('home-btn').addEventListener('click', () => this.navigate('home'));

        // Notification button 
        Utils.el('notif-btn').addEventListener('click', () => {
            Utils.el('notif-badge').style.display = 'none';
            const creditos = Store.get('creditos', []).filter(c => !c.pagado);
            if (creditos.length > 0) {
                const fecha = Utils.dateLabel(Utils.today());
                Modal.show(`
                    <div class="modal-title">🔔 Recordatorios</div>
                    <div class="alert-box alert-warning">
                        <span class="material-icons-outlined" style="font-size:20px">alarm</span>
                        <span>¡Recuerde pagar su(s) crédito(s) el <strong>${fecha}</strong>! Lindo día 😊</span>
                    </div>
                    ${creditos.map(c => `
                    <div class="list-item">
                        <div class="list-item-icon"><span class="material-icons-outlined">credit_card</span></div>
                        <div class="list-item-content">
                            <div class="list-item-title">${Utils.esc(c.nombre)}</div>
                            <div class="list-item-sub">Cuota: ${Utils.fmtCurrency(c.cuotaMensual)}/mes</div>
                        </div>
                    </div>`).join('')}
                    <button class="btn btn-primary" onclick="Modal.close();App.navigate('creditos')">Ver Créditos</button>`);
            } else {
                toast('No tienes recordatorios pendientes', 'check_circle');
            }
        });

        // Exchange Rates Modal
        const ratesBtn = Utils.el('rates-btn');
        if (ratesBtn) {
            ratesBtn.addEventListener('click', async () => {
                Modal.show(`
                    <div style="text-align:center;padding:20px">
                        <div class="loading-ring" style="width:30px;height:30px;margin-bottom:10px"></div>
                        <div style="font-size:14px;color:var(--text-secondary)">Obteniendo tasas actualizadas...</div>
                    </div>
                `);
                try {
                    const res = await fetch('https://ve.dolarapi.com/v1/dolares');
                    const data = await res.json();
                    
                    const bcv = data.find(d => d.fuente === 'oficial');
                    const paralelo = data.find(d => d.fuente === 'paralelo');
                    const time = bcv?.fechaActualizacion ? new Date(bcv.fechaActualizacion).toLocaleString('es-VE') : '';

                    Modal.show(`
                        <div class="modal-title" style="margin-bottom:15px;display:flex;align-items:center;gap:8px">
                            <span class="material-icons-outlined" style="color:var(--gold)">currency_exchange</span>
                            Tasas de Cambio <span style="font-size:12px;font-weight:400;color:var(--text-muted);margin-left:auto">DolarAPI</span>
                        </div>
                        
                        <div style="background:rgba(255,255,255,0.03);border-radius:12px;padding:18px;margin-bottom:12px;border:1px solid rgba(45,125,210,0.15)">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                                <div>
                                    <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px">🇺🇸 Dólar Oficial</div>
                                    <div style="font-size:16px;font-weight:600">BCV</div>
                                </div>
                                <span style="font-size:22px;font-weight:800;color:var(--success)">Bs. ${Utils.fmt(bcv?.promedio)}</span>
                            </div>
                            <div style="height:1px;background:rgba(45,125,210,0.1);margin:12px 0"></div>
                            <div style="display:flex;justify-content:space-between;align-items:center">
                                <div>
                                    <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:1px">📊 Mercado / USDT</div>
                                    <div style="font-size:16px;font-weight:600">Paralelo</div>
                                </div>
                                <span style="font-size:22px;font-weight:800;color:var(--warning)">Bs. ${Utils.fmt(paralelo?.promedio)}</span>
                            </div>
                        </div>

                        <div style="font-size:11px;color:var(--text-muted);text-align:center;margin-bottom:15px">
                            Última actualización: <br> ${time || 'No disponible'}
                        </div>

                        <button class="btn btn-primary" onclick="Modal.close()" style="width:100%">Cerrar</button>
                    `);
                } catch (e) {
                    toast('Error al obtener tasas', 'error');
                    Modal.close();
                }
            });
        }

        // Modal overlay close
        Utils.el('modal-overlay').addEventListener('click', (e) => {
            if (e.target === Utils.el('modal-overlay')) Modal.close();
        });

        // Notifications
        Notif.init();

        // Auto-month cleanup check
        this.checkMonthReset();

        // Automatic Data Retention Sweep (1mo Mercado / 4mo Universidad)
        this.cleanupExpiredFacturas();

        // Show home
        this.navigate('home');
    },

    checkMonthReset() {
        const lastMonth = Store.get('last_month_check', null);
        const currentMonth = Utils.monthKey();
        if (lastMonth && lastMonth !== currentMonth) {
            // New month – data naturally lives under new monthKey
            toast(`¡Nuevo mes! ${currentMonth} empieza fresh 🌟`, 'calendar_month');
        }
        Store.set('last_month_check', currentMonth);
    },

    cleanupExpiredFacturas() {
        const now = Date.now();
        let purgedCount = 0;

        // Loop through all keys in localStorage to find facturas_*
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key.startsWith('facturas_')) {
                let facturas = Store.get(key, []);
                const originalLength = facturas.length;
                
                // Keep only those that haven't expired
                facturas = facturas.filter(f => {
                    if (!f.expiresAt) return true; // Legacy/Manual items stay
                    return f.expiresAt > now;
                });

                if (facturas.length !== originalLength) {
                    purgedCount += (originalLength - facturas.length);
                    Store.set(key, facturas);
                }
            }
        }
        
        if (purgedCount > 0) {
            console.log(`[VeloApp] Purged ${purgedCount} expired invoices.`);
        }
    },

    async navigate(viewName) {
        this.currentView = viewName;
        // Reset client selection when leaving clientes
        if (viewName !== 'clientes') ViewClientes.selectedClient = null;
        this.updateNav();
        
        const view = this.views[viewName];
        if (view && view.init) await view.init();
        
        this.renderCurrentView();
    },

    updateNav() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-view') === this.currentView);
        });
    },

    renderCurrentView() {
        const content = Utils.el('content-area');
        const view = this.views[this.currentView];
        content.innerHTML = view ? view.render() : `<div class="empty-state"><span class="material-icons-outlined">error</span><span class="empty-title">Vista no encontrada</span></div>`;
        content.classList.remove('view-enter');
        void content.offsetWidth; // force reflow
        content.classList.add('view-enter');
        content.scrollTop = 0;
    },

    async getBcvRate() {
        // Retornar caché si es reciente (menos de 1 hora)
        const cached = Store.get('bcv_rate_data', null);
        const now = Date.now();
        if (cached && (now - cached.time < 3600000)) return cached.rate;

        try {
            const res = await fetch('https://ve.dolarapi.com/v1/dolares/oficial');
            const d = await res.json();
            const rate = d.promedio;
            Store.set('bcv_rate_data', { rate, time: now });
            Store.set('bcv_rate', rate);
            return rate;
        } catch (e) {
            console.warn('Error fetching rate, using fallback:', e);
            return Store.get('bcv_rate', 48.00);
        }
    }
};

// ══════════════════════════════════════════════
// ARRANQUE
// ══════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
    // Show splash then init
    setTimeout(() => {
        const splash = Utils.el('splash-screen');
        const main   = Utils.el('main-app');
        splash.style.opacity = '0';
        splash.style.transition = 'opacity 0.5s ease';
        setTimeout(() => {
            splash.style.display = 'none';
            main.classList.remove('hidden');
            App.init();
        }, 500);
    }, 2000);

    // Expose globals for inline HTML event handlers
    window.App      = App;
    window.Modal    = Modal;
    window.Store    = Store;
    window.Utils    = Utils;
    window.ViewScanner  = ViewScanner;
    window.ViewGastos   = ViewGastos;
    window.ViewClientes = ViewClientes;
    window.ViewCreditos = ViewCreditos;
    window.ViewAhorros  = ViewAhorros;
    window.ViewHorarios = ViewHorarios;
    window.ViewIngresos = ViewIngresos;
});
