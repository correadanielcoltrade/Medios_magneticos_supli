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

    parseJsonResponse(res) {
        return res.text().then(text => {
            let data = null;

            if (text) {
                try {
                    data = JSON.parse(text);
                } catch (error) {
                    data = null;
                }
            }

            if (!res.ok) {
                const serverMessage = data && data.message ? data.message : this.buildHttpErrorMessage(res, text);
                throw new Error(serverMessage);
            }

            return data || {};
        });
    }

    buildHttpErrorMessage(res, text = '') {
        const htmlResponse = text.trim().startsWith('<');
        if (htmlResponse) {
            return `El servidor devolvio una pagina de error (${res.status}). Espera unos segundos y vuelve a intentar; si se repite, revisa los logs de Render.`;
        }
        return `Error HTTP ${res.status}: ${res.statusText || 'respuesta no valida del servidor'}`;
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
            .then(res => this.parseJsonResponse(res))
            .then(data => {
                if (data.processing && data.job_id) {
                    this.updateLoadingMessage(data.message || 'Procesando archivo...');
                    this.pollUploadStatus(data.job_id);
                    return;
                }

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

    pollUploadStatus(jobId, attempt = 0) {
        if (attempt > 180) {
            this.hideLoading();
            this.showError('Error al procesar el archivo: el servidor tardo demasiado en responder. Intenta con un archivo mas pequeno o vuelve a cargarlo.');
            return;
        }

        fetch(`/upload-status/${jobId}`, { cache: 'no-store' })
            .then(res => this.parseJsonResponse(res))
            .then(data => {
                if (data.status === 'done') {
                    this.hideLoading();
                    if (data.dataframe_id) {
                        localStorage.setItem('dataframe_id', data.dataframe_id);
                    }
                    this.setFileLoaded(data.file_name, data.file_size, data.resumen_formatos);
                    this.showSuccess(data.message, data.file_size);
                    return;
                }

                if (data.status === 'error' || data.success === false) {
                    this.hideLoading();
                    this.showError('Error al procesar el archivo: ' + (data.message || 'No se pudo completar el procesamiento.'));
                    return;
                }

                this.updateLoadingMessage(data.message || 'Procesando archivo...');
                setTimeout(() => this.pollUploadStatus(jobId, attempt + 1), 1000);
            })
            .catch(err => {
                this.hideLoading();
                this.showError('Error al consultar el procesamiento: ' + err.message);
                console.error('Upload status error:', err);
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
        const dataframe_id = localStorage.getItem('dataframe_id') || '';

        // Formatos pesados que requieren procesamiento asíncrono (Odoo + muchos registros)
        const formatosAsincronicos = ['1001', '1008'];
        if (formatosAsincronicos.includes(codigo)) {
            this.handleAsyncDownload(codigo, dataframe_id, card, btn, loading, startTime);
            return;
        }

        fetch(`/download/${codigo}?dataframe_id=${encodeURIComponent(dataframe_id)}`)
            .then(res => {
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
                console.log(`[DESCARGA] Respuesta recibida en ${elapsed}s, status: ${res.status}`);

                if (!res.ok) {
                    return this.parseJsonResponse(res);
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

    handleAsyncDownload(codigo, dataframe_id, card, btn, loading, startTime) {
        fetch(`/download-job/${codigo}?dataframe_id=${encodeURIComponent(dataframe_id)}`, {
            method: 'POST'
        })
            .then(res => this.parseJsonResponse(res))
            .then(data => {
                if (!data.job_id) {
                    throw new Error('El servidor no devolvio un identificador de generacion');
                }

                this.showDownloadProgress(codigo, 10);
                return this.waitForDownloadJob(codigo, data.job_id, startTime);
            })
            .then(job => {
                this.showDownloadProgress(codigo, 85);
                return fetch(`/download-job/file/${job.job_id}`)
                    .then(res => {
                        if (!res.ok) {
                            return this.parseJsonResponse(res);
                        }
                        return res.blob();
                    });
            })
            .then(blob => {
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
                console.log(`[DESCARGA] Blob recibido: ${(blob.size / 1024).toFixed(2)} KB en ${elapsed}s`);

                if (!blob || blob.size === 0) {
                    throw new Error('Archivo vacio recibido');
                }

                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Formato_${codigo}_COLTRADE_2025.xlsx`;
                document.body.appendChild(a);
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

    waitForDownloadJob(codigo, jobId, startTime) {
        const maxAttempts = 300;  // 300 attempts * 2 segundos = 600 segundos = 10 minutos
        let attempts = 0;

        return new Promise((resolve, reject) => {
            const poll = () => {
                attempts += 1;

                fetch(`/download-job/status/${jobId}`)
                    .then(res => this.parseJsonResponse(res))
                    .then(data => {
                        const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
                        console.log(`[DESCARGA] Estado job ${jobId}: ${data.status} (${elapsed}s)`);

                        if (data.status === 'done') {
                            resolve({ job_id: jobId });
                            return;
                        }

                        if (data.status === 'error') {
                            reject(new Error(data.message || 'Error generando el reporte'));
                            return;
                        }

                        const progress = Math.min(80, 10 + (attempts / 3));
                        this.showDownloadProgress(codigo, progress);

                        if (attempts >= maxAttempts) {
                            reject(new Error('La generacion del reporte esta tardando demasiado. Por favor, verifica tu conexion a Odoo.'));
                            return;
                        }

                        setTimeout(poll, 2000);
                    })
                    .catch(reject);
            };

            poll();
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
        this.updateLoadingMessage('Procesando archivo...');
    }

    hideLoading() {
        this.loadingIndicator.classList.add('d-none');
    }

    updateLoadingMessage(message) {
        const text = this.loadingIndicator.querySelector('span:not(.visually-hidden)');
        if (text) {
            text.textContent = message;
        }
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
