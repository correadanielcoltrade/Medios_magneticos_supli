/**
 * App.js - Lógica principal del generador de reportes
 * Maneja: carga de archivos, validaciones y descargas
 */

class ReportApp {
    constructor() {
        this.isFileLoaded = false;
        this.fileName = '';
        this.initializeElements();
        this.attachEventListeners();
        this.checkInitialStatus();
    }

    // ==================== INICIALIZACIÓN ====================

    initializeElements() {
        this.dropzone = document.getElementById('dropzone');
        this.fileInput = document.getElementById('file-input');
        this.fileInfo = document.getElementById('file-info');
        this.formatSummary = document.getElementById('format-summary');
        this.errorMessage = document.getElementById('error-message');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.clearSection = document.getElementById('clear-section');
        this.clearBtn = document.getElementById('clear-btn');
        this.formatsGrid = document.getElementById('formats-grid');
        this.formatButtons = document.querySelectorAll('.format-btn');
    }

    attachEventListeners() {
        // Dropzone events
        this.dropzone.addEventListener('click', () => this.fileInput.click());
        this.dropzone.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.dropzone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.dropzone.addEventListener('drop', (e) => this.handleDrop(e));

        // File input change
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Clear button
        this.clearBtn.addEventListener('click', () => this.clearSession());

        // Format buttons - SIEMPRE agregar listeners, independientemente de si está disabled
        this.formatButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (!btn.disabled) {
                    this.handleDownload(e);
                }
            });
        });
    }

    checkInitialStatus() {
        fetch('/status')
            .then(res => res.json())
            .then(data => {
                if (data.file_loaded) {
                    this.setFileLoaded(data.file_name, '', data.resumen_formatos);
                }
            })
            .catch(err => console.error('Error checking status:', err));
    }

    // ==================== MANEJO DE CARGA ====================

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.dropzone.classList.add('active');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.dropzone.classList.remove('active');
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.dropzone.classList.remove('active');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.fileInput.files = files;
            this.uploadFile(files[0]);
        }
    }

    handleFileSelect(e) {
        if (e.target.files.length > 0) {
            this.uploadFile(e.target.files[0]);
        }
    }

    uploadFile(file) {
        // Validaciones iniciales
        if (!file.name.endsWith('.xlsx')) {
            this.showError('❌ Solo se permiten archivos .xlsx');
            return;
        }

        if (file.size > 50 * 1024 * 1024) {
            this.showError('❌ El archivo es demasiado grande (máximo 50MB)');
            return;
        }

        if (!file.name.toLowerCase().includes('balance')) {
            this.showError('❌ El archivo debe contener "balance" en el nombre');
            return;
        }

        // Mostrar loading
        this.showLoading();
        this.hideError();

        // Crear FormData y enviar
        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
            .then(res => {
                if (!res.ok) {
                    throw new Error(`Server error: ${res.status} ${res.statusText}`);
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    this.hideLoading();
                    this.setFileLoaded(data.file_name, data.file_size, data.resumen_formatos);
                    this.showSuccess(data.message, data.file_size);
                } else {
                    this.hideLoading();
                    this.showError('❌ ' + data.message);
                }
            })
            .catch(err => {
                this.hideLoading();
                this.showError('❌ Error al procesar el archivo: ' + err.message);
                console.error('Upload error:', err);
            });
    }

    setFileLoaded(fileName, fileSize = '', resumenFormatos = null) {
        this.isFileLoaded = true;
        this.fileName = fileName;

        // Actualizar UI
        this.fileInfo.classList.remove('d-none');
        this.dropzone.style.opacity = '0.5';
        this.dropzone.style.cursor = 'default';
        this.clearSection.classList.remove('d-none');

        // Actualizar detalles
        const details = `📄 <strong>${fileName}</strong>`;
        const sizeInfo = fileSize ? ` | ${fileSize}` : '';
        document.getElementById('file-details').innerHTML = details + sizeInfo;
        this.renderFormatSummary(resumenFormatos);

        // Habilitar botones de descarga
        this.enableFormatButtons();
    }

    renderFormatSummary(resumenFormatos) {
        if (!this.formatSummary) {
            return;
        }

        const codigosOrdenados = ['1001', '1005', '1006', '1007', '1008', '1009', '2276'];
        const codigosDisponibles = codigosOrdenados.filter(codigo => resumenFormatos && resumenFormatos[codigo]);
        if (codigosDisponibles.length === 0) {
            this.formatSummary.classList.add('d-none');
            this.formatSummary.innerHTML = '';
            return;
        }

        this.formatSummary.classList.remove('d-none');
        const bloques = codigosDisponibles.map(codigo => this.renderSummaryBlock(codigo, resumenFormatos[codigo]));
        this.formatSummary.innerHTML = bloques.join('');
    }

    renderSummaryBlock(codigo, resumen) {
        const metricas = [
            ['Registros', this.formatInteger(resumen.registros)],
            ['Cuentas encontradas', this.formatInteger(resumen.cuentas_distintas)],
            ['Cuentas parametrizadas', this.formatInteger(resumen.cuentas_parametrizadas)]
        ];

        if (codigo === '1005') {
            metricas.splice(
                1,
                0,
                ['Impuesto descontable', this.formatCurrency(resumen.impuesto_descontable)],
                ['IVA devoluciones ventas', this.formatCurrency(resumen.iva_devoluciones_ventas)]
            );
        } else if (codigo === '1001') {
            metricas.splice(1, 0, ['Debito', this.formatCurrency(resumen.suma_debito)]);
        } else {
            metricas.splice(
                1,
                0,
                ['Debito', this.formatCurrency(resumen.suma_debito)],
                ['Credito', this.formatCurrency(resumen.suma_credito)],
                ['Saldo', this.formatCurrency(resumen.saldo)]
            );
        }

        return `
            <div class="format-summary-block">
                <div class="format-summary-title">Formato ${codigo}</div>
                <div class="format-summary-grid">
                    ${metricas.map(([label, value]) => `<div><span>${label}</span><strong>${value}</strong></div>`).join('')}
                </div>
            </div>
        `;
    }

    // ==================== MANEJO DE DESCARGAS ====================

    handleDownload(e) {
        const codigo = e.target.closest('.format-card').dataset.codigo;
        const card = document.querySelector(`[data-codigo="${codigo}"]`);
        const btn = card.querySelector('.format-btn');
        const loading = card.querySelector('.format-loading');

        if (!this.isFileLoaded) {
            this.showError('Por favor carga un archivo primero');
            return;
        }

        // Mostrar loading y barra de progreso
        loading.classList.remove('d-none');
        btn.disabled = true;

        console.log(`[DESCARGA] Iniciando generación de reporte Formato ${codigo}...`);
        this.showDownloadProgress(codigo, 0);

        // Realizar descarga
        const startTime = Date.now();

        fetch(`/download/${codigo}`)
            .then(res => {
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
                console.log(`[DESCARGA] Respuesta recibida en ${elapsed}s, status: ${res.status}`);

                if (!res.ok) {
                    return res.json().then(data => {
                        throw new Error(data.message || `Error HTTP ${res.status}`);
                    }).catch(err => {
                        throw new Error(`Error HTTP ${res.status}: ${res.statusText}`);
                    });
                }

                this.showDownloadProgress(codigo, 50);
                return res.blob();
            })
            .then(blob => {
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
                console.log(`[DESCARGA] Blob recibido: ${(blob.size / 1024).toFixed(2)} KB en ${elapsed}s`);

                // Verificar que el blob sea válido
                if (!blob || blob.size === 0) {
                    throw new Error('Archivo vacio recibido');
                }

                this.showDownloadProgress(codigo, 75);

                // Crear y disparar descarga
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Formato_${codigo}_COLTRADE_2025.xlsx`;
                document.body.appendChild(a);

                console.log(`[DESCARGA] Descargando archivo: ${a.download}`);
                a.click();

                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                this.showDownloadProgress(codigo, 100);

                setTimeout(() => {
                    loading.classList.add('d-none');
                    btn.disabled = false;
                    const totalTime = ((Date.now() - startTime) / 1000).toFixed(2);
                    this.showSuccess(`Reporte Formato ${codigo} descargado correctamente (${totalTime}s)`);
                    console.log(`[DESCARGA] Completado en ${totalTime}s`);
                }, 500);
            })
            .catch(err => {
                loading.classList.add('d-none');
                btn.disabled = false;
                this.showError('Error al descargar: ' + err.message);
                console.error('[ERROR DESCARGA]', err);
            });
    }

    showDownloadProgress(codigo, percentage) {
        // Actualizar barra de progreso
        const card = document.querySelector(`[data-codigo="${codigo}"]`);
        let progressBar = card.querySelector('.download-progress-bar');

        if (!progressBar) {
            // Crear barra de progreso si no existe
            const progressContainer = document.createElement('div');
            progressContainer.className = 'download-progress-container';
            progressContainer.innerHTML = `
                <div class="download-progress">
                    <div class="download-progress-bar" style="width: 0%"></div>
                </div>
                <div class="download-progress-text">0%</div>
            `;
            card.querySelector('.format-loading').parentElement.insertBefore(progressContainer, card.querySelector('.format-loading').nextSibling);
            progressBar = card.querySelector('.download-progress-bar');
        }

        progressBar.style.width = percentage + '%';
        card.querySelector('.download-progress-text').textContent = percentage + '%';

        console.log(`[PROGRESO] Formato ${codigo}: ${percentage}%`);
    }

    // ==================== LIMPIAR SESIÓN ====================

    clearSession() {
        if (!confirm('¿Estás seguro de que deseas limpiar la sesión y cargar otro archivo?')) {
            return;
        }

        fetch('/clear-session', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    this.isFileLoaded = false;
                    this.fileName = '';

                    // Resetear UI
                    this.fileInfo.classList.add('d-none');
                    this.renderFormatSummary(null);
                    this.clearSection.classList.add('d-none');
                    this.dropzone.style.opacity = '1';
                    this.dropzone.style.cursor = 'pointer';
                    this.fileInput.value = '';

                    // Deshabilitar botones
                    this.formatButtons.forEach(btn => btn.disabled = true);

                    this.showSuccess('✓ Sesión limpiada. Puedes cargar un nuevo archivo.');
                }
            })
            .catch(err => {
                this.showError('❌ Error al limpiar la sesión: ' + err.message);
                console.error('Clear session error:', err);
            });
    }

    // ==================== UTILIDADES DE UI ====================

    enableFormatButtons() {
        this.formatButtons.forEach(btn => {
            btn.disabled = false;
            btn.style.cursor = 'pointer';
        });
    }

    formatInteger(value) {
        return new Intl.NumberFormat('es-CO', {
            maximumFractionDigits: 0
        }).format(Number(value || 0));
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('es-CO', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(Number(value || 0));
    }

    showLoading() {
        this.loadingIndicator.classList.remove('d-none');
    }

    hideLoading() {
        this.loadingIndicator.classList.add('d-none');
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorMessage.classList.remove('d-none');
        this.errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    hideError() {
        this.errorMessage.classList.add('d-none');
    }

    showSuccess(message, details = '') {
        // Crear alert Bootstrap temporal
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.setAttribute('role', 'alert');
        alert.innerHTML = `
            <strong>✓ Éxito</strong>: ${message}
            ${details ? `<br><small>${details}</small>` : ''}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insertar después del header
        const header = document.querySelector('.header');
        header.insertAdjacentElement('afterend', alert);

        // Auto-remover después de 5 segundos
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
}

// ==================== INICIALIZACIÓN ====================

document.addEventListener('DOMContentLoaded', () => {
    new ReportApp();
});
