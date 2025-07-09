/**
 * Configuration Management Module
 * Handles application configuration and settings
 */

class ConfigManager {
    constructor() {
        this.apiUrl = this.getApiUrl();
        this.config = {};
        this.isLoaded = false;
    }

    /**
     * Determine API URL based on environment
     */
    getApiUrl() {
        // Check if running locally
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:5000';
        }
        // Production URL
        return 'https://reposture-backend.onrender.com';
    }

    /**
     * Load configuration from backend
     */
    async loadConfig() {
        try {
            const response = await fetch(`${this.apiUrl}/config`);
            if (response.ok) {
                this.config = await response.json();
                this.isLoaded = true;
                this.renderConfigForm();
                return this.config;
            } else {
                throw new Error('Failed to load configuration');
            }
        } catch (error) {
            console.error('Error loading configuration:', error);
            this.showError('Erro ao carregar configurações');
            return null;
        }
    }

    /**
     * Save configuration to backend
     */
    async saveConfig(configData) {
        try {
            const response = await fetch(`${this.apiUrl}/save_config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(configData)
            });

            const result = await response.json();
            
            if (result.success) {
                this.config = { ...this.config, ...configData };
                this.showSuccess('Configurações salvas com sucesso!');
                return true;
            } else {
                throw new Error(result.message || 'Failed to save configuration');
            }
        } catch (error) {
            console.error('Error saving configuration:', error);
            this.showError('Erro ao salvar configurações');
            return false;
        }
    }

    /**
     * Render configuration form
     */
    renderConfigForm() {
        const container = document.getElementById('config-container');
        if (!container) return;

        const formHtml = `
            <form id="config-form" class="config-form">
                <div class="row">
                    <div class="col-md-6">
                        <div class="config-section">
                            <h6 class="config-section-title">
                                <i class="bi bi-sliders me-2"></i>
                                Parâmetros de Processamento
                            </h6>
                            
                            <div class="mb-3">
                                <label for="confidence_threshold" class="form-label">
                                    Limite de Confiança
                                    <span class="text-muted">(${this.config.confidence_threshold || 0.5})</span>
                                </label>
                                <input type="range" class="form-range" id="confidence_threshold" 
                                       name="confidence_threshold" min="0.1" max="1" step="0.1" 
                                       value="${this.config.confidence_threshold || 0.5}">
                                <div class="form-text">
                                    Ajusta a sensibilidade da detecção de landmarks
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="min_detection_confidence" class="form-label">
                                    Confiança Mínima de Detecção
                                    <span class="text-muted">(${this.config.min_detection_confidence || 0.5})</span>
                                </label>
                                <input type="range" class="form-range" id="min_detection_confidence" 
                                       name="min_detection_confidence" min="0.1" max="1" step="0.1" 
                                       value="${this.config.min_detection_confidence || 0.5}">
                                <div class="form-text">
                                    Confiança mínima para detectar uma pessoa
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="min_tracking_confidence" class="form-label">
                                    Confiança Mínima de Rastreamento
                                    <span class="text-muted">(${this.config.min_tracking_confidence || 0.5})</span>
                                </label>
                                <input type="range" class="form-range" id="min_tracking_confidence" 
                                       name="min_tracking_confidence" min="0.1" max="1" step="0.1" 
                                       value="${this.config.min_tracking_confidence || 0.5}">
                                <div class="form-text">
                                    Confiança mínima para rastrear landmarks
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <div class="config-section">
                            <h6 class="config-section-title">
                                <i class="bi bi-palette me-2"></i>
                                Configurações Visuais
                            </h6>
                            
                            <div class="mb-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="draw_landmarks" 
                                           name="draw_landmarks" ${this.config.draw_landmarks ? 'checked' : ''}>
                                    <label class="form-check-label" for="draw_landmarks">
                                        Desenhar Landmarks
                                    </label>
                                </div>
                                <div class="form-text">
                                    Exibe pontos de referência na imagem
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="draw_connections" 
                                           name="draw_connections" ${this.config.draw_connections ? 'checked' : ''}>
                                    <label class="form-check-label" for="draw_connections">
                                        Desenhar Conexões
                                    </label>
                                </div>
                                <div class="form-text">
                                    Conecta os landmarks com linhas
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="show_pose_analysis" 
                                           name="show_pose_analysis" ${this.config.show_pose_analysis ? 'checked' : ''}>
                                    <label class="form-check-label" for="show_pose_analysis">
                                        Mostrar Análise de Postura
                                    </label>
                                </div>
                                <div class="form-text">
                                    Exibe informações sobre a postura detectada
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="landmark_color" class="form-label">Cor dos Landmarks</label>
                                <input type="color" class="form-control form-control-color" 
                                       id="landmark_color" name="landmark_color" 
                                       value="${this.config.landmark_color || '#ff0000'}">
                            </div>
                            
                            <div class="mb-3">
                                <label for="connection_color" class="form-label">Cor das Conexões</label>
                                <input type="color" class="form-control form-control-color" 
                                       id="connection_color" name="connection_color" 
                                       value="${this.config.connection_color || '#00ff00'}">
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-12">
                        <div class="config-section">
                            <h6 class="config-section-title">
                                <i class="bi bi-gear me-2"></i>
                                Configurações Avançadas
                            </h6>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="max_file_size" class="form-label">
                                            Tamanho Máximo do Arquivo (MB)
                                        </label>
                                        <input type="number" class="form-control" id="max_file_size" 
                                               name="max_file_size" min="1" max="100" 
                                               value="${this.config.max_file_size || 16}">
                                    </div>
                                </div>
                                
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="output_quality" class="form-label">
                                            Qualidade de Saída (%)
                                        </label>
                                        <input type="number" class="form-control" id="output_quality" 
                                               name="output_quality" min="10" max="100" 
                                               value="${this.config.output_quality || 95}">
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <div class="form-check form-switch">
                                    <input class="form-check-input" type="checkbox" id="auto_cleanup" 
                                           name="auto_cleanup" ${this.config.auto_cleanup ? 'checked' : ''}>
                                    <label class="form-check-label" for="auto_cleanup">
                                        Limpeza Automática de Arquivos Temporários
                                    </label>
                                </div>
                                <div class="form-text">
                                    Remove automaticamente arquivos temporários após o processamento
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="config-actions mt-4">
                    <button type="button" id="btn-reset-config" class="btn btn-outline-secondary">
                        <i class="bi bi-arrow-clockwise me-1"></i>Restaurar Padrões
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-check-circle me-1"></i>Salvar Configurações
                    </button>
                </div>
            </form>
        `;

        container.innerHTML = formHtml;
        this.attachConfigEventListeners();
    }

    /**
     * Attach event listeners to configuration form
     */
    attachConfigEventListeners() {
        const form = document.getElementById('config-form');
        if (!form) return;

        // Range input updates
        const rangeInputs = form.querySelectorAll('input[type="range"]');
        rangeInputs.forEach(input => {
            input.addEventListener('input', (e) => {
                const label = form.querySelector(`label[for="${e.target.id}"] .text-muted`);
                if (label) {
                    label.textContent = `(${e.target.value})`;
                }
            });
        });

        // Form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleConfigSubmit(e);
        });

        // Reset button
        const resetBtn = document.getElementById('btn-reset-config');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetToDefaults();
            });
        }
    }

    /**
     * Handle configuration form submission
     */
    async handleConfigSubmit(event) {
        const formData = new FormData(event.target);
        const configData = {};

        // Process form data
        for (let [key, value] of formData.entries()) {
            if (event.target.elements[key].type === 'checkbox') {
                configData[key] = event.target.elements[key].checked;
            } else if (event.target.elements[key].type === 'range' || event.target.elements[key].type === 'number') {
                configData[key] = parseFloat(value);
            } else {
                configData[key] = value;
            }
        }

        // Add unchecked checkboxes as false
        const checkboxes = event.target.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            if (!formData.has(checkbox.name)) {
                configData[checkbox.name] = false;
            }
        });

        await this.saveConfig(configData);
    }

    /**
     * Reset configuration to defaults
     */
    resetToDefaults() {
        const defaults = {
            confidence_threshold: 0.5,
            min_detection_confidence: 0.5,
            min_tracking_confidence: 0.5,
            draw_landmarks: true,
            draw_connections: true,
            show_pose_analysis: true,
            landmark_color: '#ff0000',
            connection_color: '#00ff00',
            max_file_size: 16,
            output_quality: 95,
            auto_cleanup: false
        };

        this.config = defaults;
        this.renderConfigForm();
        this.showInfo('Configurações restauradas para os valores padrão');
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        if (window.flashManager) {
            window.flashManager.show(message, 'success');
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (window.flashManager) {
            window.flashManager.show(message, 'danger');
        }
    }

    /**
     * Show info message
     */
    showInfo(message) {
        if (window.flashManager) {
            window.flashManager.show(message, 'info');
        }
    }
}

// Export for use in other modules
window.ConfigManager = ConfigManager;