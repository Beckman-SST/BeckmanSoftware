/**
 * Upload Management Module
 * Handles file upload, drag & drop, and file preview functionality
 */

class UploadManager {
    constructor(apiManager) {
        this.apiManager = apiManager;
        this.selectedFiles = [];
        this.isUploading = false;
        this.uploadProgress = 0;
        
        this.initializeElements();
        this.attachEventListeners();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('files');
        this.previewContainer = document.getElementById('preview-container');
        this.filePreview = document.getElementById('file-preview');
        this.uploadForm = document.getElementById('upload-form');
        this.uploadBtn = document.getElementById('btn-upload');
        this.clearBtn = document.getElementById('btn-clear');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        if (!this.uploadArea || !this.fileInput) return;

        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files);
        });

        // Drag and drop events
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            if (!this.uploadArea.contains(e.relatedTarget)) {
                this.uploadArea.classList.remove('dragover');
            }
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            this.handleFileSelect(e.dataTransfer.files);
        });

        // Form submission
        if (this.uploadForm) {
            this.uploadForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleUpload();
            });
        }

        // Clear button
        if (this.clearBtn) {
            this.clearBtn.addEventListener('click', () => {
                this.clearFiles();
            });
        }
    }

    /**
     * Handle file selection
     */
    handleFileSelect(files) {
        if (!files || files.length === 0) return;

        try {
            // Validate files
            this.apiManager.validateFiles(files);
            
            // Convert FileList to Array and add to selected files
            const newFiles = Array.from(files);
            this.selectedFiles = [...this.selectedFiles, ...newFiles];
            
            // Remove duplicates based on name and size
            this.selectedFiles = this.removeDuplicateFiles(this.selectedFiles);
            
            // Update preview
            this.updatePreview();
            
            // Show success message
            if (window.flashManager) {
                window.flashManager.show(
                    `${newFiles.length} arquivo(s) selecionado(s) com sucesso`, 
                    'success'
                );
            }
        } catch (error) {
            if (window.flashManager) {
                window.flashManager.show(error.message, 'danger');
            }
        }
    }

    /**
     * Remove duplicate files
     */
    removeDuplicateFiles(files) {
        const seen = new Set();
        return files.filter(file => {
            const key = `${file.name}-${file.size}-${file.lastModified}`;
            if (seen.has(key)) {
                return false;
            }
            seen.add(key);
            return true;
        });
    }

    /**
     * Update file preview
     */
    updatePreview() {
        if (!this.previewContainer || !this.filePreview) return;

        if (this.selectedFiles.length === 0) {
            this.previewContainer.style.display = 'none';
            return;
        }

        this.previewContainer.style.display = 'block';
        this.filePreview.innerHTML = '';

        this.selectedFiles.forEach((file, index) => {
            const previewItem = this.createPreviewItem(file, index);
            this.filePreview.appendChild(previewItem);
        });

        // Update upload button state
        if (this.uploadBtn) {
            this.uploadBtn.disabled = this.selectedFiles.length === 0 || this.isUploading;
        }
    }

    /**
     * Create preview item for a file
     */
    createPreviewItem(file, index) {
        const item = document.createElement('div');
        item.className = 'preview-item hover-lift';
        item.dataset.index = index;

        const isImage = file.type.startsWith('image/');
        const isVideo = file.type.startsWith('video/');

        let mediaElement = '';
        if (isImage) {
            const imageUrl = URL.createObjectURL(file);
            mediaElement = `<img src="${imageUrl}" alt="${file.name}" loading="lazy">`;
        } else if (isVideo) {
            const videoUrl = URL.createObjectURL(file);
            mediaElement = `<video src="${videoUrl}" muted></video>`;
        } else {
            mediaElement = `<div class="file-icon"><i class="bi bi-file-earmark"></i></div>`;
        }

        item.innerHTML = `
            ${mediaElement}
            <div class="preview-overlay">
                <div class="file-name">${this.truncateFileName(file.name, 20)}</div>
                <div class="file-size">${this.formatFileSize(file.size)}</div>
            </div>
            <button type="button" class="preview-remove" onclick="uploadManager.removeFile(${index})">
                <i class="bi bi-x"></i>
            </button>
        `;

        return item;
    }

    /**
     * Remove file from selection
     */
    removeFile(index) {
        if (index >= 0 && index < this.selectedFiles.length) {
            // Revoke object URL to free memory
            const file = this.selectedFiles[index];
            if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
                const previewItem = this.filePreview.querySelector(`[data-index="${index}"]`);
                if (previewItem) {
                    const mediaElement = previewItem.querySelector('img, video');
                    if (mediaElement && mediaElement.src.startsWith('blob:')) {
                        URL.revokeObjectURL(mediaElement.src);
                    }
                }
            }

            this.selectedFiles.splice(index, 1);
            this.updatePreview();

            if (window.flashManager) {
                window.flashManager.show('Arquivo removido', 'info');
            }
        }
    }

    /**
     * Clear all selected files
     */
    clearFiles() {
        // Revoke all object URLs
        this.selectedFiles.forEach((file, index) => {
            if (file.type.startsWith('image/') || file.type.startsWith('video/')) {
                const previewItem = this.filePreview.querySelector(`[data-index="${index}"]`);
                if (previewItem) {
                    const mediaElement = previewItem.querySelector('img, video');
                    if (mediaElement && mediaElement.src.startsWith('blob:')) {
                        URL.revokeObjectURL(mediaElement.src);
                    }
                }
            }
        });

        this.selectedFiles = [];
        this.fileInput.value = '';
        this.updatePreview();

        if (window.flashManager) {
            window.flashManager.show('Todos os arquivos foram removidos', 'info');
        }
    }

    /**
     * Handle file upload
     */
    async handleUpload() {
        if (this.selectedFiles.length === 0) {
            if (window.flashManager) {
                window.flashManager.show('Selecione pelo menos um arquivo', 'warning');
            }
            return;
        }

        if (this.isUploading) {
            return;
        }

        this.isUploading = true;
        this.updateUploadButton(true);

        try {
            // Show upload progress
            if (window.flashManager) {
                window.flashManager.show('Enviando arquivos...', 'info');
            }

            // Upload files with progress tracking
            const result = await this.apiManager.uploadFiles(
                this.selectedFiles,
                (progress) => {
                    this.uploadProgress = progress;
                    this.updateUploadProgress(progress);
                }
            );

            if (result.success) {
                // Clear files after successful upload
                this.clearFiles();
                
                // Show success message
                if (window.flashManager) {
                    window.flashManager.show(
                        'Arquivos enviados com sucesso! Processamento iniciado.', 
                        'success'
                    );
                }

                // Switch to status section
                if (window.navigationManager) {
                    window.navigationManager.showSection('status');
                }

                // Start status monitoring
                if (window.statusManager) {
                    window.statusManager.startMonitoring();
                }
            } else {
                throw new Error(result.message || 'Erro no upload');
            }
        } catch (error) {
            console.error('Upload error:', error);
            if (window.flashManager) {
                window.flashManager.show(
                    `Erro no upload: ${error.message}`, 
                    'danger'
                );
            }
        } finally {
            this.isUploading = false;
            this.uploadProgress = 0;
            this.updateUploadButton(false);
        }
    }

    /**
     * Update upload button state
     */
    updateUploadButton(uploading) {
        if (!this.uploadBtn) return;

        this.uploadBtn.disabled = uploading || this.selectedFiles.length === 0;
        
        if (uploading) {
            this.uploadBtn.innerHTML = `
                <span class="spinner-border spinner-border-sm me-2" role="status"></span>
                Enviando...
            `;
        } else {
            this.uploadBtn.innerHTML = `
                <i class="bi bi-play-circle me-1"></i>
                Iniciar Processamento
            `;
        }
    }

    /**
     * Update upload progress
     */
    updateUploadProgress(progress) {
        // This could be used to show a progress bar during upload
        console.log(`Upload progress: ${progress.toFixed(1)}%`);
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
     * Get file type icon
     */
    getFileTypeIcon(file) {
        if (file.type.startsWith('image/')) {
            return 'bi-image';
        } else if (file.type.startsWith('video/')) {
            return 'bi-camera-video';
        } else {
            return 'bi-file-earmark';
        }
    }

    /**
     * Validate file type and size
     */
    validateFile(file) {
        return this.apiManager.validateFile(file);
    }

    /**
     * Get selected files count
     */
    getSelectedFilesCount() {
        return this.selectedFiles.length;
    }

    /**
     * Get total size of selected files
     */
    getTotalSize() {
        return this.selectedFiles.reduce((total, file) => total + file.size, 0);
    }

    /**
     * Check if upload is in progress
     */
    isUploadInProgress() {
        return this.isUploading;
    }

    /**
     * Reset upload manager
     */
    reset() {
        this.clearFiles();
        this.isUploading = false;
        this.uploadProgress = 0;
        this.updateUploadButton(false);
    }
}

// Export for use in other modules
window.UploadManager = UploadManager;