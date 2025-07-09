/**
 * Results Management Module
 * Handles display of processed files and results gallery
 */

class ResultsManager {
    constructor(apiManager) {
        this.apiManager = apiManager;
        this.processedFiles = [];
        this.errorFiles = [];
        this.currentFilter = 'all'; // all, images, videos, errors
        this.isLoading = false;
        
        this.initializeElements();
        this.attachEventListeners();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.resultsSection = document.getElementById('results-section');
        this.resultsGallery = document.getElementById('results-gallery');
        this.resultsCount = document.getElementById('results-count');
        this.errorCount = document.getElementById('error-count');
        this.filterButtons = document.querySelectorAll('.filter-btn');
        this.refreshBtn = document.getElementById('btn-refresh');
        this.clearTempBtn = document.getElementById('btn-clear-temp');
        this.openOutputBtn = document.getElementById('btn-open-output');
        this.downloadAllBtn = document.getElementById('btn-download-all');
        this.loadingSpinner = document.getElementById('results-loading');
        this.emptyState = document.getElementById('results-empty');
        this.imageModal = document.getElementById('imageModal');
        this.modalImage = document.getElementById('modalImage');
        this.modalVideo = document.getElementById('modalVideo');
        this.modalTitle = document.getElementById('imageModalLabel');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Filter buttons
        this.filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filter = e.target.dataset.filter;
                this.setFilter(filter);
            });
        });

        // Action buttons
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => {
                this.loadResults();
            });
        }

        if (this.clearTempBtn) {
            this.clearTempBtn.addEventListener('click', () => {
                this.handleClearTemp();
            });
        }

        if (this.openOutputBtn) {
            this.openOutputBtn.addEventListener('click', () => {
                this.handleOpenOutput();
            });
        }

        if (this.downloadAllBtn) {
            this.downloadAllBtn.addEventListener('click', () => {
                this.handleDownloadAll();
            });
        }

        // Modal events
        if (this.imageModal) {
            this.imageModal.addEventListener('hidden.bs.modal', () => {
                this.clearModal();
            });
        }
    }

    /**
     * Load processed files and errors
     */
    async loadResults() {
        if (this.isLoading) return;

        this.isLoading = true;
        this.showLoading(true);

        try {
            // Load processed files and errors in parallel
            const [filesResult, errorsResult] = await Promise.all([
                this.apiManager.getProcessedFiles(),
                this.apiManager.getErrors()
            ]);

            this.processedFiles = filesResult.files || [];
            this.errorFiles = errorsResult.errors || [];

            this.updateCounts();
            this.renderGallery();
            this.updateActionButtons();

        } catch (error) {
            console.error('Error loading results:', error);
            if (window.flashManager) {
                window.flashManager.show(
                    `Erro ao carregar resultados: ${error.message}`, 
                    'danger'
                );
            }
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }

    /**
     * Update file counts
     */
    updateCounts() {
        if (this.resultsCount) {
            this.resultsCount.textContent = this.processedFiles.length;
        }
        
        if (this.errorCount) {
            this.errorCount.textContent = this.errorFiles.length;
            
            // Update error count badge visibility
            const errorBadge = this.errorCount.closest('.badge');
            if (errorBadge) {
                errorBadge.style.display = this.errorFiles.length > 0 ? 'inline' : 'none';
            }
        }
    }

    /**
     * Set active filter
     */
    setFilter(filter) {
        this.currentFilter = filter;
        
        // Update active button
        this.filterButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
        
        this.renderGallery();
    }

    /**
     * Get filtered files based on current filter
     */
    getFilteredFiles() {
        switch (this.currentFilter) {
            case 'images':
                return this.processedFiles.filter(file => 
                    file.type && file.type.startsWith('image/'));
            case 'videos':
                return this.processedFiles.filter(file => 
                    file.type && file.type.startsWith('video/'));
            case 'errors':
                return this.errorFiles;
            case 'all':
            default:
                return [...this.processedFiles, ...this.errorFiles];
        }
    }

    /**
     * Render gallery
     */
    renderGallery() {
        if (!this.resultsGallery) return;

        const filteredFiles = this.getFilteredFiles();
        
        if (filteredFiles.length === 0) {
            this.showEmptyState(true);
            return;
        }
        
        this.showEmptyState(false);
        this.resultsGallery.innerHTML = '';
        
        filteredFiles.forEach((file, index) => {
            const galleryItem = this.createGalleryItem(file, index);
            this.resultsGallery.appendChild(galleryItem);
        });
    }

    /**
     * Create gallery item
     */
    createGalleryItem(file, index) {
        const item = document.createElement('div');
        item.className = 'gallery-item hover-lift';
        
        const isError = this.errorFiles.includes(file);
        const isImage = file.type && file.type.startsWith('image/');
        const isVideo = file.type && file.type.startsWith('video/');
        
        if (isError) {
            item.classList.add('error-item');
        }
        
        let mediaElement = '';
        let clickHandler = '';
        
        if (isError) {
            mediaElement = `
                <div class="error-placeholder">
                    <i class="bi bi-exclamation-triangle"></i>
                    <div class="error-message">${file.error || 'Erro no processamento'}</div>
                </div>
            `;
        } else if (isImage) {
            const imageUrl = this.apiManager.getFileUrl(file.filename);
            mediaElement = `<img src="${imageUrl}" alt="${file.original_name || file.filename}" loading="lazy">`;
            clickHandler = `onclick="resultsManager.openModal('${file.filename}', 'image')"`;
        } else if (isVideo) {
            const videoUrl = this.apiManager.getFileUrl(file.filename);
            mediaElement = `<video src="${videoUrl}" muted preload="metadata"></video>`;
            clickHandler = `onclick="resultsManager.openModal('${file.filename}', 'video')"`;
        } else {
            mediaElement = `
                <div class="file-placeholder">
                    <i class="bi bi-file-earmark"></i>
                </div>
            `;
        }
        
        const downloadButton = !isError ? `
            <button type="button" class="gallery-action" onclick="resultsManager.downloadFile('${file.filename}')" title="Download">
                <i class="bi bi-download"></i>
            </button>
        ` : '';
        
        item.innerHTML = `
            <div class="gallery-media" ${clickHandler}>
                ${mediaElement}
                ${isError ? '<div class="error-badge"><i class="bi bi-exclamation-triangle"></i></div>' : ''}
            </div>
            <div class="gallery-overlay">
                <div class="gallery-info">
                    <div class="file-name" title="${file.original_name || file.filename}">
                        ${this.truncateFileName(file.original_name || file.filename, 20)}
                    </div>
                    ${file.size ? `<div class="file-size">${this.formatFileSize(file.size)}</div>` : ''}
                    ${file.processed_at ? `<div class="file-date">${this.formatDate(file.processed_at)}</div>` : ''}
                </div>
                <div class="gallery-actions">
                    ${downloadButton}
                    <button type="button" class="gallery-action" onclick="resultsManager.deleteFile('${file.filename}')" title="Excluir">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        return item;
    }

    /**
     * Open modal for image/video preview
     */
    openModal(filename, type) {
        if (!this.imageModal || !filename) return;
        
        const fileUrl = this.apiManager.getFileUrl(filename);
        const file = this.processedFiles.find(f => f.filename === filename);
        const title = file ? (file.original_name || file.filename) : filename;
        
        // Clear previous content
        this.clearModal();
        
        // Set modal title
        if (this.modalTitle) {
            this.modalTitle.textContent = title;
        }
        
        // Set content based on type
        if (type === 'image' && this.modalImage) {
            this.modalImage.src = fileUrl;
            this.modalImage.style.display = 'block';
        } else if (type === 'video' && this.modalVideo) {
            this.modalVideo.src = fileUrl;
            this.modalVideo.style.display = 'block';
            this.modalVideo.controls = true;
        }
        
        // Show modal
        const modal = new bootstrap.Modal(this.imageModal);
        modal.show();
    }

    /**
     * Clear modal content
     */
    clearModal() {
        if (this.modalImage) {
            this.modalImage.src = '';
            this.modalImage.style.display = 'none';
        }
        
        if (this.modalVideo) {
            this.modalVideo.src = '';
            this.modalVideo.style.display = 'none';
            this.modalVideo.pause();
        }
    }

    /**
     * Download file
     */
    async downloadFile(filename) {
        try {
            await this.apiManager.downloadFile(filename);
            
            if (window.flashManager) {
                window.flashManager.show('Download iniciado', 'success');
            }
        } catch (error) {
            console.error('Download error:', error);
            if (window.flashManager) {
                window.flashManager.show(
                    `Erro no download: ${error.message}`, 
                    'danger'
                );
            }
        }
    }

    /**
     * Delete file
     */
    async deleteFile(filename) {
        if (!confirm('Tem certeza que deseja excluir este arquivo?')) {
            return;
        }
        
        try {
            const result = await this.apiManager.deleteFile(filename);
            
            if (result.success) {
                // Remove from local arrays
                this.processedFiles = this.processedFiles.filter(f => f.filename !== filename);
                this.errorFiles = this.errorFiles.filter(f => f.filename !== filename);
                
                // Update display
                this.updateCounts();
                this.renderGallery();
                
                if (window.flashManager) {
                    window.flashManager.show('Arquivo excluído com sucesso', 'success');
                }
            } else {
                throw new Error(result.message || 'Erro ao excluir arquivo');
            }
        } catch (error) {
            console.error('Delete error:', error);
            if (window.flashManager) {
                window.flashManager.show(
                    `Erro ao excluir: ${error.message}`, 
                    'danger'
                );
            }
        }
    }

    /**
     * Handle clear temporary files
     */
    async handleClearTemp() {
        if (!confirm('Tem certeza que deseja limpar todos os arquivos temporários?')) {
            return;
        }
        
        try {
            // Disable button during operation
            if (this.clearTempBtn) {
                this.clearTempBtn.disabled = true;
                this.clearTempBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Limpando...
                `;
            }
            
            const result = await this.apiManager.clearTemp();
            
            if (result.success) {
                // Clear local data
                this.processedFiles = [];
                this.errorFiles = [];
                
                // Update display
                this.updateCounts();
                this.renderGallery();
                
                if (window.flashManager) {
                    window.flashManager.show('Arquivos temporários limpos com sucesso', 'success');
                }
            } else {
                throw new Error(result.message || 'Erro ao limpar arquivos');
            }
        } catch (error) {
            console.error('Clear temp error:', error);
            if (window.flashManager) {
                window.flashManager.show(
                    `Erro ao limpar: ${error.message}`, 
                    'danger'
                );
            }
        } finally {
            // Re-enable button
            if (this.clearTempBtn) {
                this.clearTempBtn.disabled = false;
                this.clearTempBtn.innerHTML = `
                    <i class="bi bi-trash me-1"></i>
                    Limpar Temporários
                `;
            }
        }
    }

    /**
     * Handle open output folder
     */
    async handleOpenOutput() {
        try {
            const result = await this.apiManager.openOutputFolder();
            
            if (result.success) {
                if (window.flashManager) {
                    window.flashManager.show('Pasta de saída aberta', 'info');
                }
            } else {
                throw new Error(result.message || 'Erro ao abrir pasta');
            }
        } catch (error) {
            console.error('Open output error:', error);
            if (window.flashManager) {
                window.flashManager.show(
                    `Erro ao abrir pasta: ${error.message}`, 
                    'danger'
                );
            }
        }
    }

    /**
     * Handle download all files
     */
    async handleDownloadAll() {
        if (this.processedFiles.length === 0) {
            if (window.flashManager) {
                window.flashManager.show('Nenhum arquivo para download', 'warning');
            }
            return;
        }
        
        try {
            // Disable button during operation
            if (this.downloadAllBtn) {
                this.downloadAllBtn.disabled = true;
                this.downloadAllBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Baixando...
                `;
            }
            
            // Download files one by one
            for (const file of this.processedFiles) {
                await this.apiManager.downloadFile(file.filename);
                await new Promise(resolve => setTimeout(resolve, 100)); // Small delay
            }
            
            if (window.flashManager) {
                window.flashManager.show(
                    `${this.processedFiles.length} arquivo(s) baixado(s)`, 
                    'success'
                );
            }
        } catch (error) {
            console.error('Download all error:', error);
            if (window.flashManager) {
                window.flashManager.show(
                    `Erro no download: ${error.message}`, 
                    'danger'
                );
            }
        } finally {
            // Re-enable button
            if (this.downloadAllBtn) {
                this.downloadAllBtn.disabled = false;
                this.downloadAllBtn.innerHTML = `
                    <i class="bi bi-download me-1"></i>
                    Baixar Todos
                `;
            }
        }
    }

    /**
     * Update action buttons state
     */
    updateActionButtons() {
        const hasFiles = this.processedFiles.length > 0;
        const hasAnyFiles = hasFiles || this.errorFiles.length > 0;
        
        if (this.clearTempBtn) {
            this.clearTempBtn.disabled = !hasAnyFiles;
        }
        
        if (this.downloadAllBtn) {
            this.downloadAllBtn.disabled = !hasFiles;
        }
    }

    /**
     * Show/hide loading spinner
     */
    showLoading(show) {
        if (this.loadingSpinner) {
            this.loadingSpinner.style.display = show ? 'block' : 'none';
        }
        
        if (this.resultsGallery) {
            this.resultsGallery.style.display = show ? 'none' : 'grid';
        }
    }

    /**
     * Show/hide empty state
     */
    showEmptyState(show) {
        if (this.emptyState) {
            this.emptyState.style.display = show ? 'block' : 'none';
        }
        
        if (this.resultsGallery) {
            this.resultsGallery.style.display = show ? 'none' : 'grid';
        }
    }

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Format date
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
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
     * Get processed files count
     */
    getProcessedCount() {
        return this.processedFiles.length;
    }

    /**
     * Get error files count
     */
    getErrorCount() {
        return this.errorFiles.length;
    }

    /**
     * Reset results manager
     */
    reset() {
        this.processedFiles = [];
        this.errorFiles = [];
        this.currentFilter = 'all';
        
        this.updateCounts();
        this.renderGallery();
        this.updateActionButtons();
        
        // Reset filter buttons
        this.filterButtons.forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === 'all');
        });
    }

    /**
     * Show results section
     */
    show() {
        if (this.resultsSection) {
            this.resultsSection.style.display = 'block';
        }
    }

    /**
     * Hide results section
     */
    hide() {
        if (this.resultsSection) {
            this.resultsSection.style.display = 'none';
        }
    }
}

// Export for use in other modules
window.ResultsManager = ResultsManager;