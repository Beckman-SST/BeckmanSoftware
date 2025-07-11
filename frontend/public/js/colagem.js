/**
 * Colagem Management Module
 * Handles display and organization of processed images
 */
class ColagemManager {
    constructor() {
        this.executiveImages = [];
        this.operationalImages = [];
        this.isLoading = false;
        
        this.initializeElements();
        this.loadImages();
        this.attachEventListeners();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.loadingState = document.getElementById('loadingState');
        this.emptyState = document.getElementById('emptyState');
        this.executiveSection = document.getElementById('executiveSection');
        this.operationalSection = document.getElementById('operationalSection');
        this.executiveImages = document.getElementById('executiveImages');
        this.operationalImages = document.getElementById('operationalImages');
        this.executiveCount = document.getElementById('executiveCount');
        this.operationalCount = document.getElementById('operationalCount');
        this.imageModal = document.getElementById('imageModal');
        this.modalImage = document.getElementById('modalImage');
        this.modalTitle = document.getElementById('imageModalLabel');
        this.downloadModalBtn = document.getElementById('downloadModalBtn');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Modal download button
        if (this.downloadModalBtn) {
            this.downloadModalBtn.addEventListener('click', () => {
                this.downloadCurrentImage();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
                e.preventDefault();
                this.refreshImages();
            }
        });
    }

    /**
     * Load processed images from the server
     */
    async loadImages() {
        if (this.isLoading) return;
        
        this.setLoadingState(true);
        
        try {
            const response = await fetch('/api/files');
            const result = await response.json();
            
            if (result.success) {
                // Categoriza as imagens baseado no nome do arquivo
                const allImages = result.images || [];
                this.categorizeImages(allImages);
                this.renderImages();
            } else {
                this.showMessage('Erro ao carregar imagens: ' + (result.error || 'Erro desconhecido'), 'error');
                this.showEmptyState();
            }
        } catch (error) {
            console.error('Erro ao carregar imagens:', error);
            this.showMessage('Erro ao carregar imagens processadas', 'error');
            this.showEmptyState();
        } finally {
            this.setLoadingState(false);
        }
    }

    /**
     * Categorize images based on filename prefixes
     */
    categorizeImages(images) {
        this.executiveImages = [];
        this.operationalImages = [];
        
        images.forEach(image => {
            if (this.isExecutiveImage(image)) {
                this.executiveImages.push(image);
            } else if (this.isOperationalImage(image)) {
                this.operationalImages.push(image);
            }
        });
        
        // Sort images by date (newest first)
        this.executiveImages.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
        this.operationalImages.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
    }

    /**
     * Check if file is an image
     */
    isImageFile(file) {
        const filename = file.name || file.filename || '';
        const imageExtensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'];
        return imageExtensions.some(ext => filename.toLowerCase().endsWith(ext));
    }

    /**
     * Determine if image is from executive processing
     */
    isExecutiveImage(file) {
        const filename = (file.name || file.filename || '').toLowerCase();
        
        // Check for 'ex_' prefix
        if (filename.startsWith('ex_')) return true;
        
        // Check processing type if available
        if (file.processing_type === 'executivo') return true;
        
        // Fallback to legacy keywords
        const executiveKeywords = ['executivo', 'executive', 'postura', 'angulo', 'angle'];
        return executiveKeywords.some(keyword => filename.includes(keyword)) && 
                !filename.includes('tarja') && !filename.includes('operacional');
    }

    /**
     * Determine if image is from operational processing (tarja)
     */
    isOperationalImage(file) {
        const filename = (file.name || file.filename || '').toLowerCase();
        
        // Check for 'op_' prefix
        if (filename.startsWith('op_')) return true;
        
        // Check processing type if available
        if (file.processing_type === 'operacional') return true;
        
        // Fallback to legacy keywords
        const operationalKeywords = ['tarja', 'operacional', 'operational'];
        return operationalKeywords.some(keyword => filename.includes(keyword));
    }

    /**
     * Render images in their respective sections
     */
    renderImages() {
        const hasExecutive = this.executiveImages.length > 0;
        const hasOperational = this.operationalImages.length > 0;
        
        if (!hasExecutive && !hasOperational) {
            this.showEmptyState();
            return;
        }
        
        // Hide empty state
        if (this.emptyState) {
            this.emptyState.style.display = 'none';
        }
        
        // Render executive images
        if (hasExecutive) {
            this.renderImageSection(this.executiveImages, this.executiveImages, this.executiveSection, this.executiveCount);
        } else {
            if (this.executiveSection) this.executiveSection.style.display = 'none';
        }
        
        // Render operational images
        if (hasOperational) {
            this.renderImageSection(this.operationalImages, this.operationalImages, this.operationalSection, this.operationalCount);
        } else {
            if (this.operationalSection) this.operationalSection.style.display = 'none';
        }
    }

    /**
     * Render a specific image section
     */
    renderImageSection(images, container, section, countElement) {
        if (!container || !section) return;
        
        // Show section
        section.style.display = 'block';
        
        // Update count
        if (countElement) {
            countElement.textContent = images.length;
        }
        
        // Clear existing content
        container.innerHTML = '';
        
        // Create image cards
        const fragment = document.createDocumentFragment();
        
        images.forEach(image => {
            const imageCard = this.createImageCard(image);
            fragment.appendChild(imageCard);
        });
        
        container.appendChild(fragment);
    }

    /**
     * Create an image card element
     */
    createImageCard(image) {
        const card = document.createElement('div');
        card.className = 'image-card';
        
        const imageUrl = this.getImageUrl(image.name || image.filename);
        const displayName = image.original_name || image.name || image.filename;
        
        card.innerHTML = `
            <img src="${imageUrl}" alt="${this.escapeHtml(displayName)}" loading="lazy" 
                 onclick="colagemManager.openImageModal('${imageUrl}', '${this.escapeHtml(displayName)}', '${image.filename}')">
            <div class="image-info">
                <div class="image-name" title="${this.escapeHtml(displayName)}">
                    ${this.escapeHtml(this.truncateText(displayName, 30))}
                </div>
                <div class="image-actions">
                    <button class="btn btn-outline-primary btn-action" 
                            onclick="colagemManager.viewImage('${imageUrl}')" 
                            title="Visualizar">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-outline-success btn-action" 
                            onclick="colagemManager.downloadImage('${imageUrl}', '${this.escapeHtml(displayName)}')" 
                            title="Baixar">
                        <i class="bi bi-download"></i>
                    </button>
                </div>
            </div>
        `;
        
        return card;
    }

    /**
     * Get image URL for display
     */
    getImageUrl(filename) {
        return `/api/output_file/${encodeURIComponent(filename)}`;
    }

    /**
     * Open image in modal
     */
    openImageModal(imageUrl, imageName, filename) {
        if (!this.imageModal || !this.modalImage || !this.modalTitle) return;
        
        this.modalImage.src = imageUrl;
        this.modalTitle.innerHTML = `<i class="bi bi-zoom-in me-2"></i>${this.escapeHtml(imageName)}`;
        
        // Store current image info for download
        this.currentModalImage = { url: imageUrl, name: imageName, filename: filename || imageName };
        
        const bootstrapModal = new bootstrap.Modal(this.imageModal);
        bootstrapModal.show();
    }

    /**
     * View image in new tab
     */
    viewImage(imageUrl) {
        window.open(imageUrl, '_blank');
    }

    /**
     * Download image
     */
    downloadImage(image) {
        const link = document.createElement('a');
        link.href = this.getImageUrl(image.name || image.filename);
        link.download = image.original_name || image.name || image.filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    /**
     * Download current modal image
     */
    downloadCurrentImage() {
        if (this.currentModalImage) {
            this.downloadImage(this.currentModalImage.url, this.currentModalImage.name);
        }
    }

    /**
     * Refresh images
     */
    async refreshImages() {
        await this.loadImages();
        this.showMessage('Imagens atualizadas com sucesso!', 'success');
    }

    /**
     * Show empty state
     */
    showEmptyState() {
        if (this.emptyState) {
            this.emptyState.style.display = 'block';
        }
        if (this.executiveSection) {
            this.executiveSection.style.display = 'none';
        }
        if (this.operationalSection) {
            this.operationalSection.style.display = 'none';
        }
    }

    /**
     * Set loading state
     */
    setLoadingState(loading) {
        this.isLoading = loading;
        
        if (this.loadingState) {
            this.loadingState.style.display = loading ? 'flex' : 'none';
        }
        
        if (loading) {
            if (this.emptyState) this.emptyState.style.display = 'none';
            if (this.executiveSection) this.executiveSection.style.display = 'none';
            if (this.operationalSection) this.operationalSection.style.display = 'none';
        }
    }

    /**
     * Show message to user
     */
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

    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Truncate text to specified length
     */
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }
}

// Global functions for onclick handlers
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('show');
    }
}

function refreshImages() {
    if (window.colagemManager) {
        window.colagemManager.refreshImages();
    }
}

// Initialize the application
const colagemManager = new ColagemManager();
window.colagemManager = colagemManager;

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    // Cleanup if needed
});