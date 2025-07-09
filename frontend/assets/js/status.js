/**
 * Status Management Module
 * Handles processing status monitoring and progress display
 */

class StatusManager {
    constructor(apiManager) {
        this.apiManager = apiManager;
        this.isMonitoring = false;
        this.monitoringInterval = null;
        this.currentStatus = null;
        this.lastUpdateTime = null;
        
        this.initializeElements();
        this.attachEventListeners();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.statusSection = document.getElementById('status-section');
        this.statusCard = document.getElementById('status-card');
        this.statusText = document.getElementById('status-text');
        this.progressBar = document.getElementById('progress-bar');
        this.progressText = document.getElementById('progress-text');
        this.currentFile = document.getElementById('current-file');
        this.processedCount = document.getElementById('processed-count');
        this.totalCount = document.getElementById('total-count');
        this.elapsedTime = document.getElementById('elapsed-time');
        this.estimatedTime = document.getElementById('estimated-time');
        this.cancelBtn = document.getElementById('btn-cancel');
        this.errorsList = document.getElementById('errors-list');
        this.errorsContainer = document.getElementById('errors-container');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        if (this.cancelBtn) {
            this.cancelBtn.addEventListener('click', () => {
                this.handleCancel();
            });
        }
    }

    /**
     * Start monitoring processing status
     */
    startMonitoring() {
        if (this.isMonitoring) return;

        this.isMonitoring = true;
        this.lastUpdateTime = Date.now();
        
        // Show status section
        if (this.statusSection) {
            this.statusSection.style.display = 'block';
        }

        // Start polling
        this.monitoringInterval = setInterval(() => {
            this.checkStatus();
        }, 1000); // Check every second

        // Initial check
        this.checkStatus();
    }

    /**
     * Stop monitoring
     */
    stopMonitoring() {
        this.isMonitoring = false;
        
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
    }

    /**
     * Check processing status
     */
    async checkStatus() {
        try {
            const status = await this.apiManager.getStatus();
            this.updateStatus(status);
        } catch (error) {
            console.error('Error checking status:', error);
            
            // If we get a network error, show it but don't stop monitoring
            if (error.message.includes('network') || error.message.includes('fetch')) {
                this.updateStatusText('Verificando conexão...', 'warning');
            } else {
                this.updateStatusText('Erro ao verificar status', 'danger');
            }
        }
    }

    /**
     * Update status display
     */
    updateStatus(status) {
        this.currentStatus = status;
        
        if (!status) {
            this.updateStatusText('Status não disponível', 'warning');
            return;
        }

        // Update progress bar
        this.updateProgressBar(status.progress || 0);
        
        // Update status text based on processing state
        if (status.processing) {
            this.updateStatusText('Processando...', 'primary');
            this.updateProcessingInfo(status);
        } else if (status.completed) {
            this.updateStatusText('Processamento concluído!', 'success');
            this.handleProcessingComplete(status);
        } else if (status.error) {
            this.updateStatusText('Erro no processamento', 'danger');
            this.handleProcessingError(status);
        } else {
            this.updateStatusText('Aguardando...', 'secondary');
        }

        // Update errors if any
        this.updateErrors(status.errors || []);
        
        // Update elapsed time
        this.updateElapsedTime();
    }

    /**
     * Update status text and style
     */
    updateStatusText(text, type = 'primary') {
        if (this.statusText) {
            this.statusText.textContent = text;
            
            // Update card style based on status type
            if (this.statusCard) {
                this.statusCard.className = `card status-card status-${type}`;
            }
        }
    }

    /**
     * Update progress bar
     */
    updateProgressBar(progress) {
        const percentage = Math.max(0, Math.min(100, progress));
        
        if (this.progressBar) {
            this.progressBar.style.width = `${percentage}%`;
            this.progressBar.setAttribute('aria-valuenow', percentage);
            
            // Update progress bar color based on percentage
            this.progressBar.className = 'progress-bar progress-bar-striped progress-bar-animated';
            if (percentage >= 100) {
                this.progressBar.classList.add('bg-success');
            } else if (percentage >= 75) {
                this.progressBar.classList.add('bg-info');
            } else if (percentage >= 50) {
                this.progressBar.classList.add('bg-warning');
            } else {
                this.progressBar.classList.add('bg-primary');
            }
        }
        
        if (this.progressText) {
            this.progressText.textContent = `${percentage.toFixed(1)}%`;
        }
    }

    /**
     * Update processing information
     */
    updateProcessingInfo(status) {
        // Current file
        if (this.currentFile && status.current_file) {
            this.currentFile.textContent = this.truncateFileName(status.current_file, 30);
        }
        
        // File counts
        if (this.processedCount && status.processed_count !== undefined) {
            this.processedCount.textContent = status.processed_count;
        }
        
        if (this.totalCount && status.total_count !== undefined) {
            this.totalCount.textContent = status.total_count;
        }
        
        // Estimated time
        if (this.estimatedTime && status.estimated_time) {
            this.estimatedTime.textContent = this.formatTime(status.estimated_time);
        }
    }

    /**
     * Handle processing completion
     */
    handleProcessingComplete(status) {
        this.stopMonitoring();
        
        // Update progress to 100%
        this.updateProgressBar(100);
        
        // Show completion message
        if (window.flashManager) {
            const message = status.total_count > 0 
                ? `Processamento concluído! ${status.processed_count || status.total_count} arquivo(s) processado(s).`
                : 'Processamento concluído!';
            window.flashManager.show(message, 'success');
        }
        
        // Switch to results section
        setTimeout(() => {
            if (window.navigationManager) {
                window.navigationManager.showSection('results');
            }
            
            // Load results
            if (window.resultsManager) {
                window.resultsManager.loadResults();
            }
        }, 2000);
    }

    /**
     * Handle processing error
     */
    handleProcessingError(status) {
        this.stopMonitoring();
        
        if (window.flashManager) {
            const errorMessage = status.error_message || 'Erro desconhecido no processamento';
            window.flashManager.show(`Erro: ${errorMessage}`, 'danger');
        }
    }

    /**
     * Update errors list
     */
    updateErrors(errors) {
        if (!this.errorsList || !this.errorsContainer) return;
        
        if (errors.length === 0) {
            this.errorsContainer.style.display = 'none';
            return;
        }
        
        this.errorsContainer.style.display = 'block';
        this.errorsList.innerHTML = '';
        
        errors.forEach(error => {
            const errorItem = document.createElement('div');
            errorItem.className = 'error-item alert alert-warning alert-dismissible fade show';
            errorItem.innerHTML = `
                <div class="d-flex align-items-start">
                    <i class="bi bi-exclamation-triangle me-2 mt-1"></i>
                    <div class="flex-grow-1">
                        <strong>${this.truncateFileName(error.file || 'Arquivo desconhecido', 40)}</strong>
                        <div class="small text-muted">${error.message || 'Erro desconhecido'}</div>
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            this.errorsList.appendChild(errorItem);
        });
    }

    /**
     * Handle cancel button click
     */
    async handleCancel() {
        if (!this.isMonitoring) return;
        
        try {
            // Disable cancel button
            if (this.cancelBtn) {
                this.cancelBtn.disabled = true;
                this.cancelBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Cancelando...
                `;
            }
            
            // Send cancel request
            const result = await this.apiManager.cancelProcessing();
            
            if (result.success) {
                this.updateStatusText('Processamento cancelado', 'warning');
                this.stopMonitoring();
                
                if (window.flashManager) {
                    window.flashManager.show('Processamento cancelado pelo usuário', 'warning');
                }
            } else {
                throw new Error(result.message || 'Erro ao cancelar processamento');
            }
        } catch (error) {
            console.error('Cancel error:', error);
            if (window.flashManager) {
                window.flashManager.show(`Erro ao cancelar: ${error.message}`, 'danger');
            }
        } finally {
            // Re-enable cancel button
            if (this.cancelBtn) {
                this.cancelBtn.disabled = false;
                this.cancelBtn.innerHTML = `
                    <i class="bi bi-stop-circle me-1"></i>
                    Cancelar Processamento
                `;
            }
        }
    }

    /**
     * Update elapsed time
     */
    updateElapsedTime() {
        if (!this.elapsedTime || !this.lastUpdateTime) return;
        
        const elapsed = Math.floor((Date.now() - this.lastUpdateTime) / 1000);
        this.elapsedTime.textContent = this.formatTime(elapsed);
    }

    /**
     * Format time in seconds to readable format
     */
    formatTime(seconds) {
        if (seconds < 60) {
            return `${seconds}s`;
        } else if (seconds < 3600) {
            const minutes = Math.floor(seconds / 60);
            const remainingSeconds = seconds % 60;
            return `${minutes}m ${remainingSeconds}s`;
        } else {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }
    }

    /**
     * Truncate file name
     */
    truncateFileName(fileName, maxLength) {
        if (fileName.length <= maxLength) return fileName;
        
        const extension = fileName.split('.').pop();
        const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf('.'));
        const truncatedName = nameWithoutExt.substring(0, maxLength - extension.length - 4) + '...';
        
        return truncatedName + '.' + extension;
    }

    /**
     * Get current status
     */
    getCurrentStatus() {
        return this.currentStatus;
    }

    /**
     * Check if monitoring is active
     */
    isMonitoringActive() {
        return this.isMonitoring;
    }

    /**
     * Reset status manager
     */
    reset() {
        this.stopMonitoring();
        this.currentStatus = null;
        this.lastUpdateTime = null;
        
        // Reset UI elements
        this.updateProgressBar(0);
        this.updateStatusText('Aguardando...', 'secondary');
        
        if (this.currentFile) this.currentFile.textContent = '';
        if (this.processedCount) this.processedCount.textContent = '0';
        if (this.totalCount) this.totalCount.textContent = '0';
        if (this.elapsedTime) this.elapsedTime.textContent = '0s';
        if (this.estimatedTime) this.estimatedTime.textContent = '--';
        
        this.updateErrors([]);
        
        // Hide status section
        if (this.statusSection) {
            this.statusSection.style.display = 'none';
        }
    }

    /**
     * Show status section
     */
    show() {
        if (this.statusSection) {
            this.statusSection.style.display = 'block';
        }
    }

    /**
     * Hide status section
     */
    hide() {
        if (this.statusSection) {
            this.statusSection.style.display = 'none';
        }
    }
}

// Export for use in other modules
window.StatusManager = StatusManager;