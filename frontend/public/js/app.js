/**
 * RePosture Application - Main JavaScript Module
 * Optimized and modularized version
 */

class RePostureApp {
    constructor() {
        this.selectedFiles = [];
        this.processingType = 'executivo';
        this.statusInterval = null;
        this.isProcessing = false;
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        this.initializeElements();
        this.attachEventListeners();
        this.loadProcessedFiles();
    }

    initializeElements() {
        // Cache DOM elements for better performance
        this.elements = {
            fileUploadArea: document.getElementById('fileUploadArea'),
            fileInput: document.getElementById('fileInput'),
            filesList: document.getElementById('filesList'),
            selectedFiles: document.getElementById('selectedFiles'),
            uploadBtn: document.getElementById('uploadBtn'),
            processingStatus: document.getElementById('processingStatus'),
            progressBar: document.getElementById('progressBar'),
            progressText: document.getElementById('progressText'),
            filesProcessed: document.getElementById('filesProcessed'),
            totalFiles: document.getElementById('totalFiles'),
            timeRemaining: document.getElementById('timeRemaining'),
            currentFileText: document.getElementById('currentFileText'),
            cancelProcessingBtn: document.getElementById('cancelProcessingBtn'),
            openFolderBtn: document.getElementById('openFolderBtn'),
            clearTempBtn: document.getElementById('clearTempBtn'),
            emptyState: document.getElementById('emptyState'),
            executiveImagesSection: document.getElementById('executiveImagesSection'),
            operationalImagesSection: document.getElementById('operationalImagesSection'),
            videosSection: document.getElementById('videosSection'),
            executiveImages: document.getElementById('executiveImages'),
            operationalImages: document.getElementById('operationalImages'),
            processedVideos: document.getElementById('processedVideos')
        };
    }

    attachEventListeners() {
        // File upload events
        this.elements.fileUploadArea?.addEventListener('click', () => {
            this.elements.fileInput?.click();
        });

        this.elements.fileInput?.addEventListener('change', (e) => {
            this.handleFileSelection(e);
        });

        // Drag and drop events
        if (this.elements.fileUploadArea) {
            this.elements.fileUploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
            this.elements.fileUploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            this.elements.fileUploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        }

        // Processing type tabs
        document.querySelectorAll('.processing-tabs .btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.processing-tabs .btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.processingType = e.target.dataset.type;
            });
        });

        // Action buttons
        this.elements.uploadBtn?.addEventListener('click', () => this.uploadFiles());
        this.elements.openFolderBtn?.addEventListener('click', () => this.openOutputFolder());
        this.elements.clearTempBtn?.addEventListener('click', () => this.clearTempFiles());
        this.elements.cancelProcessingBtn?.addEventListener('click', () => this.cancelProcessing());

        // Header action buttons
        document.querySelectorAll('.header-actions .btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const title = e.currentTarget.getAttribute('title');
                if (title === 'Configurações') {
                    window.location.href = 'configuracoes.html';
                }
            });
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'u') {
                e.preventDefault();
                this.elements.fileInput?.click();
            }
        });
    }

    // File handling methods
    handleFileSelection(event) {
        const files = Array.from(event.target.files);
        this.selectedFiles = files;
        this.displaySelectedFiles();
    }

    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('dragover');
    }

    handleDragLeave(event) {
        event.currentTarget.classList.remove('dragover');
    }

    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('dragover');
        
        const files = Array.from(event.dataTransfer.files);
        this.selectedFiles = files;
        this.displaySelectedFiles();
    }

    displaySelectedFiles() {
        if (!this.elements.filesList || !this.elements.selectedFiles) return;
        
        if (this.selectedFiles.length === 0) {
            this.elements.selectedFiles.style.display = 'none';
            return;
        }

        this.elements.selectedFiles.style.display = 'block';
        this.elements.filesList.innerHTML = '';

        // Use DocumentFragment for better performance
        const fragment = document.createDocumentFragment();

        this.selectedFiles.forEach((file, index) => {
            const fileItem = this.createFilePreviewItem(file, index);
            fragment.appendChild(fileItem);
        });

        this.elements.filesList.appendChild(fragment);
    }

    createFilePreviewItem(file, index) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-thumbnail-item';
        
        const isImage = file.type.startsWith('image/');
        
        if (isImage) {
            this.createImageThumbnail(file, fileItem, index);
        } else {
            this.createFileThumbnail(file, fileItem, index);
        }
        
        return fileItem;
    }

    createImageThumbnail(file, container, index) {
        const reader = new FileReader();
        reader.onload = (e) => {
            container.innerHTML = `
                <div class="thumbnail-container">
                    <img src="${e.target.result}" alt="${this.escapeHtml(file.name)}" class="thumbnail-image" loading="lazy">
                    <button class="remove-btn" onclick="app.removeFile(${index})" title="Remover imagem" aria-label="Remover ${this.escapeHtml(file.name)}">
                        <i class="bi bi-x"></i>
                    </button>
                    <div class="thumbnail-info">
                        <span class="file-name">${this.escapeHtml(file.name)}</span>
                        <small class="file-size">${this.formatFileSize(file.size)}</small>
                    </div>
                </div>
            `;
        };
        reader.readAsDataURL(file);
    }

    createFileThumbnail(file, container, index) {
        container.innerHTML = `
            <div class="thumbnail-container file-icon-container">
                <div class="file-icon">
                    <i class="bi bi-file-earmark"></i>
                </div>
                <button class="remove-btn" onclick="app.removeFile(${index})" title="Remover arquivo" aria-label="Remover ${this.escapeHtml(file.name)}">
                    <i class="bi bi-x"></i>
                </button>
                <div class="thumbnail-info">
                    <span class="file-name">${this.escapeHtml(file.name)}</span>
                    <small class="file-size">${this.formatFileSize(file.size)}</small>
                </div>
            </div>
        `;
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.displaySelectedFiles();
    }

    // Upload and processing methods
    async uploadFiles() {
        if (this.selectedFiles.length === 0) {
            this.showMessage('Por favor, selecione arquivos para upload.', 'warning');
            return;
        }

        if (this.isProcessing) {
            this.showMessage('Já existe um processamento em andamento.', 'warning');
            return;
        }

        const formData = new FormData();
        this.selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        formData.append('processing_type', this.processingType);

        try {
            this.setLoadingState(true);
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.showMessage('Upload realizado com sucesso!', 'success');
                this.selectedFiles = [];
                this.displaySelectedFiles();
                this.showProcessingStatus();
                this.startStatusMonitoring();
                this.isProcessing = true;
            } else {
                this.showMessage(result.message || 'Erro no upload', 'error');
            }
        } catch (error) {
            this.showMessage('Erro na comunicação com o servidor', 'error');
            console.error('Upload error:', error);
        } finally {
            this.setLoadingState(false);
        }
    }

    // Status monitoring methods
    startStatusMonitoring() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
        }
        this.statusInterval = setInterval(() => this.checkProcessingStatus(), 2000);
    }

    showProcessingStatus() {
        if (!this.elements.processingStatus) return;
        
        this.elements.processingStatus.style.display = 'block';
        
        // Reset status
        this.updateProgressBar(0);
        this.updateStatusNumbers(0, 0, '--');
        this.updateCurrentFileText('Preparando...');
    }

    hideProcessingStatus() {
        if (this.elements.processingStatus) {
            this.elements.processingStatus.style.display = 'none';
        }
        this.isProcessing = false;
    }

    updateProcessingStatus(status) {
        if (!status.ativo) return;

        const progress = status.progresso || 0;
        this.updateProgressBar(progress);
        this.updateStatusNumbers(
            status.arquivo_atual || 0,
            status.total_arquivos || 0,
            this.formatTimeRemaining(status.tempo_restante || 0)
        );

        if (status.cancelando) {
            this.updateCurrentFileText('Cancelando processamento...');
        } else {
            this.updateCurrentFileText(
                `Processando arquivo ${status.arquivo_atual || 0} de ${status.total_arquivos || 0}`
            );
        }
    }

    updateProgressBar(progress) {
        if (this.elements.progressBar) {
            this.elements.progressBar.style.width = progress + '%';
        }
        if (this.elements.progressText) {
            this.elements.progressText.textContent = Math.round(progress) + '%';
        }
    }

    updateStatusNumbers(processed, total, timeRemaining) {
        if (this.elements.filesProcessed) {
            this.elements.filesProcessed.textContent = processed;
        }
        if (this.elements.totalFiles) {
            this.elements.totalFiles.textContent = total;
        }
        if (this.elements.timeRemaining) {
            this.elements.timeRemaining.textContent = timeRemaining;
        }
    }

    updateCurrentFileText(text) {
        if (this.elements.currentFileText) {
            this.elements.currentFileText.textContent = text;
        }
    }

    async cancelProcessing() {
        try {
            const response = await fetch('/api/cancel', {
                method: 'POST'
            });

            const result = await response.json();

            if (result.success) {
                this.showMessage('Cancelamento solicitado. Aguarde...', 'warning');
                this.updateCurrentFileText('Cancelando processamento...');
            } else {
                this.showMessage(result.error || 'Erro ao cancelar processamento', 'error');
            }
        } catch (error) {
            this.showMessage('Erro na comunicação com o servidor', 'error');
            console.error('Cancel error:', error);
        }
    }

    async checkProcessingStatus() {
        try {
            const response = await fetch('/api/status');
            const status = await response.json();

            if (status.ativo) {
                this.updateProcessingStatus(status);
            } else {
                this.hideProcessingStatus();
                if (this.statusInterval) {
                    clearInterval(this.statusInterval);
                    this.statusInterval = null;
                }
                await this.loadProcessedFiles();
            }
        } catch (error) {
            console.error('Status check error:', error);
            this.hideProcessingStatus();
        }
    }

    // File display methods
    async loadProcessedFiles() {
        try {
            const response = await fetch('/api/files');
            const data = await response.json();

            if (data.success) {
                const allFiles = [
                    ...(data.images || []),
                    ...(data.videos || []),
                    ...(data.errors || [])
                ];
                this.displayProcessedFiles(allFiles);
            }
        } catch (error) {
            console.error('Load files error:', error);
        }
    }

    displayProcessedFiles(files) {
        // Clear all containers
        this.clearResultContainers();

        if (files.length === 0) {
            this.showEmptyState();
            return;
        }

        this.hideEmptyState();
        const categorizedFiles = this.categorizeFiles(files);
        this.displayCategorizedFiles(categorizedFiles);
    }

    clearResultContainers() {
        const containers = [
            this.elements.executiveImages,
            this.elements.operationalImages,
            this.elements.processedVideos
        ];
        
        containers.forEach(container => {
            if (container) container.innerHTML = '';
        });

        const sections = [
            this.elements.executiveImagesSection,
            this.elements.operationalImagesSection,
            this.elements.videosSection
        ];
        
        sections.forEach(section => {
            if (section) section.style.display = 'none';
        });
    }

    showEmptyState() {
        if (this.elements.emptyState) {
            this.elements.emptyState.style.display = 'block';
        }
    }

    hideEmptyState() {
        if (this.elements.emptyState) {
            this.elements.emptyState.style.display = 'none';
        }
    }

    categorizeFiles(files) {
        const categories = {
            executive: [],
            operational: [],
            videos: []
        };

        files.forEach(file => {
            const isVideo = /\.(mp4|avi|mov|wmv)$/i.test(file.name);
            const isOperational = file.name.startsWith('op_');
            const isExecutive = file.name.startsWith('ex_');

            if (isVideo) {
                categories.videos.push(file);
            } else if (isOperational) {
                categories.operational.push(file);
            } else if (isExecutive) {
                categories.executive.push(file);
            } else {
                // Fallback: se não tem prefixo, considera como executivo
                categories.executive.push(file);
            }
        });

        return categories;
    }

    displayCategorizedFiles(categories) {
        if (categories.executive.length > 0) {
            this.elements.executiveImagesSection.style.display = 'block';
            this.displayFilesInContainer(categories.executive, this.elements.executiveImages);
        }

        if (categories.operational.length > 0) {
            this.elements.operationalImagesSection.style.display = 'block';
            this.displayFilesInContainer(categories.operational, this.elements.operationalImages);
        }

        if (categories.videos.length > 0) {
            this.elements.videosSection.style.display = 'block';
            this.displayFilesInContainer(categories.videos, this.elements.processedVideos);
        }
    }

    displayFilesInContainer(files, container) {
        if (!container) return;
        
        const fragment = document.createDocumentFragment();
        
        files.forEach(file => {
            const fileItem = this.createFileItem(file);
            fragment.appendChild(fileItem);
        });
        
        container.appendChild(fragment);
    }

    createFileItem(file) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const isImage = /\.(jpg|jpeg|png|gif)$/i.test(file.name);
        const isVideo = /\.(mp4|avi|mov|wmv)$/i.test(file.name);
        
        let thumbnailHtml;
        if (isImage) {
            thumbnailHtml = `<img src="${file.url}" class="file-thumbnail" alt="${this.escapeHtml(file.name)}" onclick="app.openImageModal('${file.url}', '${this.escapeHtml(file.name)}')" loading="lazy">`;
        } else if (isVideo) {
            thumbnailHtml = '<div class="file-thumbnail d-flex align-items-center justify-content-center bg-dark text-white"><i class="bi bi-play-circle" style="font-size: 2rem;"></i></div>';
        } else {
            thumbnailHtml = '<div class="file-thumbnail d-flex align-items-center justify-content-center"><i class="bi bi-file-earmark"></i></div>';
        }

        fileItem.innerHTML = `
            ${thumbnailHtml}
            <div class="file-info">
                <div class="file-name">${this.escapeHtml(file.name)}</div>
                <small class="text-muted">${this.formatFileSize(file.size)}</small>
                <div class="file-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="app.viewFile('${file.url}')" title="Visualizar arquivo">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="app.downloadFile('${file.url}', '${this.escapeHtml(file.name)}')" title="Baixar arquivo">
                        <i class="bi bi-download"></i>
                    </button>
                </div>
            </div>
        `;

        return fileItem;
    }

    // File action methods
    viewFile(url) {
        window.open(url, '_blank');
    }

    downloadFile(url, filename) {
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    openImageModal(imageUrl, imageName) {
        const modal = document.getElementById('imageModal');
        const modalImage = document.getElementById('modalImage');
        const modalTitle = document.getElementById('imageModalLabel');

        if (modal && modalImage && modalTitle) {
            modalImage.src = imageUrl;
            modalTitle.innerHTML = `<i class="bi bi-zoom-in me-2"></i>${this.escapeHtml(imageName)}`;

            const bootstrapModal = new bootstrap.Modal(modal);
            bootstrapModal.show();
        }
    }

    // Utility methods
    async openOutputFolder() {
        try {
            const response = await fetch('/api/open-folder', { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                this.showMessage('Pasta aberta com sucesso!', 'success');
            } else {
                this.showMessage(result.message || 'Erro ao abrir pasta', 'error');
            }
        } catch (error) {
            this.showMessage('Erro na comunicação com o servidor', 'error');
        }
    }

    async clearTempFiles() {
        if (!confirm('Tem certeza que deseja limpar todos os arquivos temporários?')) {
            return;
        }

        try {
            const response = await fetch('/api/cleanup', { method: 'POST' });
            const result = await response.json();

            if (result.success) {
                this.showMessage(`${result.removed_count} arquivos removidos com sucesso!`, 'success');
                await this.loadProcessedFiles();
            } else {
                this.showMessage(result.message || 'Erro ao limpar arquivos', 'error');
            }
        } catch (error) {
            this.showMessage('Erro na comunicação com o servidor', 'error');
        }
    }

    showMessage(message, type = 'info') {
        const toast = document.createElement('div');
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'warning' ? 'alert-warning' : 
                          type === 'error' ? 'alert-danger' : 'alert-info';
        
        toast.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px; max-width: 500px;';
        toast.innerHTML = `
            ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        `;

        document.body.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    toggleSidebar() {
        const sidebar = document.getElementById('sidebar');
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    }

    toggleSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (!section) return;
        
        if (section.style.display === 'none' || section.style.display === '') {
            // Hide all other sections first
            document.querySelectorAll('.content-section').forEach(s => {
                if (s.id !== sectionId) {
                    s.style.display = 'none';
                }
            });
            section.style.display = 'block';
        } else {
            section.style.display = 'none';
        }
    }

    setLoadingState(loading) {
        const elements = [this.elements.uploadBtn];
        elements.forEach(el => {
            if (el) {
                if (loading) {
                    el.classList.add('loading');
                    el.disabled = true;
                } else {
                    el.classList.remove('loading');
                    el.disabled = false;
                }
            }
        });
    }

    // Helper methods
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatTimeRemaining(seconds) {
        if (seconds <= 0) return '--';
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return minutes > 0 ? `${minutes}m ${remainingSeconds}s` : `${remainingSeconds}s`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Cleanup method
    destroy() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = null;
        }
    }
}

// Global functions for onclick handlers
window.toggleSidebar = () => app.toggleSidebar();

// Initialize the application
const app = new RePostureApp();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    app.destroy();
});