class ConfigManager {
    constructor() {
        this.apiUrl = this.getApiUrl();
        this.defaultConfig = {
            min_detection_confidence: 0.70,
            min_tracking_confidence: 0.60,
            yolo_confidence: 0.50,
            moving_average_window: 5,
            resize_width: 800,
            show_face_blur: true,
            show_electronics: false,
            show_angles: true,
            show_upper_body: true,
            show_lower_body: true,
            process_lower_body: true
        };
        this.init();
    }

    getApiUrl() {
        const protocol = window.location.protocol;
        const hostname = window.location.hostname;
        const port = window.location.port || (protocol === 'https:' ? '443' : '80');
        
        // Se estamos em desenvolvimento local, usar porta 5000
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return `${protocol}//${hostname}:5000`;
        }
        
        return `${protocol}//${hostname}:${port}`;
    }

    init() {
        this.attachEventListeners();
        this.loadConfig();
        this.updateRangeValues();
    }

    attachEventListeners() {
        // Form submission
        const form = document.getElementById('config-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Reset button
        const resetBtn = document.getElementById('btn-reset-config');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetToDefaults());
        }

        // Load button
        const loadBtn = document.getElementById('btn-load-config');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadConfig());
        }

        // Range inputs - update display values
        const rangeInputs = document.querySelectorAll('input[type="range"]');
        rangeInputs.forEach(input => {
            input.addEventListener('input', (e) => this.updateRangeValue(e.target));
        });

        // Back button
        const backBtn = document.querySelector('.back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                window.location.href = 'index.html';
            });
        }
    }

    updateRangeValues() {
        const rangeInputs = document.querySelectorAll('input[type="range"]');
        rangeInputs.forEach(input => {
            this.updateRangeValue(input);
        });
    }

    updateRangeValue(input) {
        const fieldName = input.name || input.id;
        const valueSpan = document.getElementById(fieldName + '_value');
        if (valueSpan) {
            valueSpan.textContent = `(${parseFloat(input.value).toFixed(2)})`;
        }
    }

    async loadConfig() {
        try {
            this.showLoading('Carregando configurações...');
            
            const response = await fetch(`${this.apiUrl}/api/config`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            // Check if the response has the expected structure
            if (result.success && result.config) {
                this.populateForm(result.config);
                this.showSuccess('Configurações carregadas com sucesso!');
            } else {
                throw new Error('Invalid response format');
            }
            
        } catch (error) {
            console.error('Erro ao carregar configurações:', error);
            this.showError('Erro ao carregar configurações. Usando valores padrão.');
            this.populateForm(this.defaultConfig);
        }
    }

    populateForm(config) {
        // Merge with defaults to ensure all fields have values
        const fullConfig = { ...this.defaultConfig, ...config };
        
        Object.keys(fullConfig).forEach(key => {
            const element = document.querySelector(`[name="${key}"]`);
            if (element) {
                if (element.type === 'checkbox') {
                    element.checked = fullConfig[key];
                } else {
                    element.value = fullConfig[key];
                    if (element.type === 'range') {
                        this.updateRangeValue(element);
                    }
                }
            }
        });
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        try {
            this.showLoading('Salvando configurações...');
            
            const formData = new FormData(e.target);
            const config = {};
            
            // Process form data
            for (const [key, value] of formData.entries()) {
                const element = document.querySelector(`[name="${key}"]`);
                if (element) {
                    if (element.type === 'checkbox') {
                        config[key] = true; // If in FormData, checkbox is checked
                    } else if (element.type === 'number' || element.type === 'range') {
                        config[key] = parseFloat(value);
                    } else {
                        config[key] = value;
                    }
                }
            }
            
            // Handle unchecked checkboxes (not in FormData)
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                if (!formData.has(checkbox.name)) {
                    config[checkbox.name] = false;
                }
            });
            
            const response = await fetch(`${this.apiUrl}/api/config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess('Configurações salvas com sucesso!');
                // Reload config to confirm it was saved
                setTimeout(() => {
                    this.loadConfig();
                }, 1000);
            } else {
                throw new Error(result.error || 'Falha ao salvar configurações');
            }
            
        } catch (error) {
            console.error('Erro ao salvar configurações:', error);
            this.showError('Erro ao salvar configurações. Tente novamente.');
        }
    }

    resetToDefaults() {
        // Exibe o modal de confirmação
        const resetModal = new bootstrap.Modal(document.getElementById('resetConfirmModal'));
        resetModal.show();
        
        // Adiciona event listener para o botão de confirmação
        const confirmResetBtn = document.getElementById('confirmResetBtn');
        const handleReset = async () => {
            // Remove o event listener para evitar múltiplas execuções
            confirmResetBtn.removeEventListener('click', handleReset);
            
            try {
                // Chama a API para resetar as configurações no backend
                const response = await fetch('/api/config/reset', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    // Recarrega as configurações do backend
                    await this.loadConfig();
                    this.showMessage('Configurações resetadas para valores padrão de fábrica!', 'success');
                } else {
                    throw new Error(result.error || 'Erro ao resetar configurações');
                }
            } catch (error) {
                console.error('Erro ao resetar configurações:', error);
                this.showMessage('Erro ao resetar configurações: ' + error.message, 'error');
            } finally {
                // Esconde o modal
                resetModal.hide();
            }
        };
        
        confirmResetBtn.addEventListener('click', handleReset);
    }

    showLoading(message) {
        this.showNotification(message, 'info', false);
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'danger');
    }

    showInfo(message) {
        this.showNotification(message, 'info');
    }

    showNotification(message, type = 'info', autoHide = true) {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.config-notification');
        existingNotifications.forEach(notification => notification.remove());

        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} config-notification`;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            border: none;
            border-radius: 8px;
        `;
        notification.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-${this.getIconForType(type)} me-2"></i>
                <span>${message}</span>
                <button type="button" class="btn-close ms-auto" aria-label="Close"></button>
            </div>
        `;

        // Add close functionality
        const closeBtn = notification.querySelector('.btn-close');
        closeBtn.addEventListener('click', () => notification.remove());

        // Add to page
        document.body.appendChild(notification);

        // Auto-hide after 3 seconds (except for loading messages)
        if (autoHide) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 3000);
        }
    }

    getIconForType(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-triangle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ConfigManager();
});