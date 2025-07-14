/**
 * Colagem Management Module
 * Handles display and organization of processed images
 */
class ColagemManager {
    constructor() {
        this.executiveImagesList = [];
        this.operationalImagesList = [];
        this.isLoading = false;
        
        // Selection and collage properties
        this.selectedImages = [];
        this.collageGroups = [];
        this.currentGroupNumber = 1;
        this.maxSelectionPerGroup = 3;
        this.usedInCollages = new Set(); // Track images used in collages
        
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
        this.executiveImagesContainer = document.getElementById('executiveImages');
        this.operationalImagesContainer = document.getElementById('operationalImages');
        this.executiveCount = document.getElementById('executiveCount');
        this.operationalCount = document.getElementById('operationalCount');
        this.imageModal = document.getElementById('imageModal');
        this.modalImage = document.getElementById('modalImage');
        this.modalTitle = document.getElementById('imageModalLabel');
        this.downloadModalBtn = document.getElementById('downloadModalBtn');
        
        // Selection panel elements
        this.selectionPanel = document.getElementById('selectionPanel');
        this.selectionCounter = document.getElementById('selectionCounter');
        this.currentGroupNumberEl = document.getElementById('currentGroupNumber');
        this.selectedImagesPreview = document.getElementById('selectedImagesPreview');
        this.finishGroupBtn = document.getElementById('finishGroupBtn');
        this.createCollageBtn = document.getElementById('createCollageBtn');
        this.clearSelectionBtn = document.getElementById('clearSelectionBtn');
        this.collageQueue = document.getElementById('collageQueue');
        this.queueItems = document.getElementById('queueItems');
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

        // Selection panel buttons
        if (this.finishGroupBtn) {
            this.finishGroupBtn.addEventListener('click', () => {
                this.finishCurrentGroup();
            });
        }
        
        if (this.createCollageBtn) {
            this.createCollageBtn.addEventListener('click', () => {
                this.createAllCollages();
            });
        }
        
        if (this.clearSelectionBtn) {
            this.clearSelectionBtn.addEventListener('click', () => {
                this.clearAllSelections();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'F5' || (e.ctrlKey && e.key === 'r')) {
                e.preventDefault();
                this.refreshImages();
            }
            if (e.key === 'Escape') {
                this.clearCurrentSelection();
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
        this.executiveImagesList = [];
        this.operationalImagesList = [];
        
        images.forEach(image => {
            if (this.isExecutiveImage(image)) {
                this.executiveImagesList.push(image);
            } else if (this.isOperationalImage(image)) {
                this.operationalImagesList.push(image);
            }
        });
        
        // Sort images by date (newest first)
        this.executiveImagesList.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
        this.operationalImagesList.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));
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
        const hasExecutive = this.executiveImagesList.length > 0;
        const hasOperational = this.operationalImagesList.length > 0;
        
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
            this.renderImageSection(this.executiveImagesList, this.executiveImagesContainer, this.executiveSection, this.executiveCount);
        } else {
            if (this.executiveSection) this.executiveSection.style.display = 'none';
        }
        
        // Render operational images
        if (hasOperational) {
            this.renderImageSection(this.operationalImagesList, this.operationalImagesContainer, this.operationalSection, this.operationalCount);
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
        const imageId = image.name || image.filename;
        card.className = 'image-card';
        card.dataset.imageId = imageId;
        
        // Check if image was used in collages
        if (this.usedInCollages.has(imageId)) {
            card.classList.add('used-in-collage');
        }
        
        const imageUrl = this.getImageUrl(imageId);
        const displayName = image.original_name || image.name || image.filename;
        
        const checkMarkHtml = this.usedInCollages.has(imageId) ? 
            '<div class="collage-check-mark"><i class="bi bi-check"></i></div>' : '';
        
        card.innerHTML = `
            ${checkMarkHtml}
            <img src="${imageUrl}" alt="${this.escapeHtml(displayName)}" loading="lazy">
            <div class="image-info">
                <div class="image-name" title="${this.escapeHtml(displayName)}">
                    ${this.escapeHtml(this.truncateText(displayName, 30))}
                </div>
                <div class="image-actions">
                    <button class="btn btn-outline-info btn-action" 
                            onclick="colagemManager.toggleImageSelection('${imageId}')" 
                            title="Selecionar para Colagem">
                        <i class="bi bi-check-square"></i>
                    </button>
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
        
        // Add click event for image selection
        card.addEventListener('click', (e) => {
            // Don't trigger selection if clicking on action buttons
            if (!e.target.closest('.image-actions')) {
                this.toggleImageSelection(imageId);
            }
        });
        
        return card;
    }

    /**
     * Get image URL for display
     */
    getImageUrl(filename) {
        return `/output/${encodeURIComponent(filename)}`;
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
     * Toggle image selection for collage
     */
    toggleImageSelection(imageId) {
        const imageIndex = this.selectedImages.findIndex(img => img.id === imageId);
        
        if (imageIndex > -1) {
            // Remove from selection
            this.selectedImages.splice(imageIndex, 1);
            this.updateImageCardSelection(imageId, false);
        } else {
            // Add to selection if not at max
            if (this.selectedImages.length < this.maxSelectionPerGroup) {
                const imageData = this.findImageById(imageId);
                if (imageData) {
                    this.selectedImages.push({
                        id: imageId,
                        data: imageData,
                        url: this.getImageUrl(imageId)
                    });
                    this.updateImageCardSelection(imageId, true);
                }
            } else {
                this.showMessage(`Máximo de ${this.maxSelectionPerGroup} imagens por grupo!`, 'warning');
                return;
            }
        }
        
        this.updateSelectionPanel();
        
        // Auto-finish group when reaching max selection
        if (this.selectedImages.length === this.maxSelectionPerGroup) {
            setTimeout(() => {
                this.finishCurrentGroup();
            }, 500);
        }
    }

    /**
     * Find image data by ID
     */
    findImageById(imageId) {
        const allImages = [...this.executiveImagesList, ...this.operationalImagesList];
        return allImages.find(img => (img.name || img.filename) === imageId);
    }

    /**
     * Update image card visual selection state
     */
    updateImageCardSelection(imageId, isSelected) {
        const card = document.querySelector(`[data-image-id="${imageId}"]`);
        if (card) {
            // Remove existing selection indicators
            card.classList.remove('selected');
            const existingNumber = card.querySelector('.selection-group-number');
            if (existingNumber) {
                existingNumber.remove();
            }
            
            if (isSelected) {
                card.classList.add('selected');
                
                // Add group number indicator with color class
                const groupNumber = document.createElement('div');
                groupNumber.className = `selection-group-number group-${this.currentGroupNumber}`;
                groupNumber.textContent = this.currentGroupNumber;
                card.insertBefore(groupNumber, card.firstChild);
            }
        }
    }

    /**
     * Update selection panel display
     */
    updateSelectionPanel() {
        if (this.selectedImages.length > 0 || this.collageGroups.length > 0) {
            this.selectionPanel.classList.add('show');
        } else {
            this.selectionPanel.classList.remove('show');
        }
        
        // Update counter
        this.selectionCounter.textContent = `${this.selectedImages.length}/${this.maxSelectionPerGroup}`;
        
        // Update group number
        this.currentGroupNumberEl.textContent = this.currentGroupNumber;
        
        // Update preview thumbnails
        this.updatePreviewThumbnails();
        
        // Update button states
        this.finishGroupBtn.disabled = this.selectedImages.length === 0;
        this.createCollageBtn.disabled = this.collageGroups.length === 0;
        
        // Update queue display
        this.updateQueueDisplay();
    }

    /**
     * Update preview thumbnails
     */
    updatePreviewThumbnails() {
        this.selectedImagesPreview.innerHTML = '';
        
        this.selectedImages.forEach(img => {
            const thumb = document.createElement('img');
            thumb.src = img.url;
            thumb.className = 'selected-image-thumb';
            thumb.title = img.data.name || img.data.filename;
            this.selectedImagesPreview.appendChild(thumb);
        });
    }

    /**
     * Finish current group and start new one
     */
    finishCurrentGroup() {
        if (this.selectedImages.length === 0) return;
        
        // Add current selection to groups
        this.collageGroups.push({
            id: Date.now(),
            groupNumber: this.currentGroupNumber,
            images: [...this.selectedImages]
        });
        
        // Clear current selection but keep visual indicators (numbers)
        this.selectedImages.forEach(img => {
            const card = document.querySelector(`[data-image-id="${img.id}"]`);
            if (card) {
                card.classList.remove('selected');
            }
        });
        this.selectedImages = [];
        
        // Increment group number
        this.currentGroupNumber++;
        
        this.updateSelectionPanel();
        this.showMessage(`Grupo ${this.currentGroupNumber - 1} adicionado à fila!`, 'success');
    }

    /**
     * Clear current selection only
     */
    clearCurrentSelection() {
        // Remove visual indicators for each selected image
        this.selectedImages.forEach(img => {
            const card = document.querySelector(`[data-image-id="${img.id}"]`);
            if (card) {
                card.classList.remove('selected');
                const groupNumber = card.querySelector('.selection-group-number');
                if (groupNumber) {
                    groupNumber.remove();
                }
            }
        });
        
        this.selectedImages = [];
        this.updateSelectionPanel();
    }

    /**
     * Clear all selections and groups
     */
    clearAllSelections() {
        this.selectedImages = [];
        this.collageGroups = [];
        this.currentGroupNumber = 1;
        this.updateSelectionPanel();
        this.updateQueueDisplay();
        
        // Remove selection visual indicators
        document.querySelectorAll('.image-card.selected').forEach(card => {
            card.classList.remove('selected');
        });
        
        // Remove all group number indicators
        document.querySelectorAll('.selection-group-number').forEach(indicator => {
            indicator.remove();
        });
        
        this.showMessage('Todas as seleções foram limpas!', 'info');
    }

    /**
     * Update visual indicators for images used in collages
     */
    updateUsedImagesVisuals() {
        // Update existing image cards to show used status
        document.querySelectorAll('.image-card').forEach(card => {
            const imageId = card.dataset.imageId;
            if (this.usedInCollages.has(imageId)) {
                card.classList.add('used-in-collage');
                
                // Add check mark if not already present
                if (!card.querySelector('.collage-check-mark')) {
                    const checkMark = document.createElement('div');
                    checkMark.className = 'collage-check-mark';
                    checkMark.innerHTML = '<i class="bi bi-check"></i>';
                    card.insertBefore(checkMark, card.firstChild);
                }
            }
        });
    }

    /**
     * Update queue display
     */
    updateQueueDisplay() {
        if (this.collageGroups.length > 0) {
            this.collageQueue.style.display = 'block';
            this.queueItems.innerHTML = '';
            
            this.collageGroups.forEach((group, index) => {
                const queueItem = document.createElement('div');
                queueItem.className = 'queue-item';
                
                const imagesDiv = document.createElement('div');
                imagesDiv.className = 'queue-images';
                
                group.images.forEach(img => {
                    const thumb = document.createElement('img');
                    thumb.src = img.url;
                    thumb.className = 'queue-thumb';
                    thumb.title = img.data.name || img.data.filename;
                    imagesDiv.appendChild(thumb);
                });
                
                const infoDiv = document.createElement('div');
                infoDiv.innerHTML = `
                    <small><strong>Grupo ${group.groupNumber}</strong> - ${group.images.length} imagens</small>
                `;
                
                const removeBtn = document.createElement('button');
                removeBtn.className = 'btn btn-outline-danger btn-sm';
                removeBtn.innerHTML = '<i class="bi bi-trash"></i>';
                removeBtn.onclick = () => this.removeGroup(index);
                
                queueItem.appendChild(imagesDiv);
                queueItem.appendChild(infoDiv);
                queueItem.appendChild(removeBtn);
                
                this.queueItems.appendChild(queueItem);
            });
        } else {
            this.collageQueue.style.display = 'none';
        }
    }

    /**
     * Remove group from queue
     */
    removeGroup(index) {
        const groupToRemove = this.collageGroups[index];
        
        // Remove visual indicators from images in this group
        if (groupToRemove && groupToRemove.images) {
            groupToRemove.images.forEach(img => {
                const card = document.querySelector(`[data-image-id="${img.id}"]`);
                if (card) {
                    card.classList.remove('selected');
                    const groupNumber = card.querySelector('.selection-group-number');
                    if (groupNumber) {
                        groupNumber.remove();
                    }
                }
            });
        }
        
        this.collageGroups.splice(index, 1);
        this.updateSelectionPanel();
        this.showMessage('Grupo removido da fila!', 'info');
    }

    /**
     * Create all collages
     */
    async createAllCollages() {
        if (this.collageGroups.length === 0) {
            this.showMessage('Nenhum grupo na fila para criar colagens!', 'warning');
            return;
        }
        
        // Add current selection to groups if any
        if (this.selectedImages.length > 0) {
            this.finishCurrentGroup();
        }
        
        this.showMessage('Criando colagens...', 'info');
        
        try {
            const response = await fetch('/api/create-collages', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    groups: this.collageGroups.map(group => ({
                        images: group.images.map(img => img.id)
                    }))
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Mark all images from completed groups as used
                this.collageGroups.forEach(group => {
                    group.images.forEach(img => {
                        this.usedInCollages.add(img.id);
                    });
                });
                
                // Remove all group number indicators before updating used images visuals
                document.querySelectorAll('.selection-group-number').forEach(indicator => {
                    indicator.remove();
                });
                
                // Update visual indicators for used images
                this.updateUsedImagesVisuals();
                
                this.showMessage(`${result.collages.length} colagens criadas com sucesso!`, 'success');
                this.clearAllSelections();
                
                // Refresh images to show new collages
                setTimeout(() => {
                    this.refreshImages();
                }, 1000);
            } else {
                this.showMessage('Erro ao criar colagens: ' + (result.error || 'Erro desconhecido'), 'error');
            }
        } catch (error) {
            console.error('Erro ao criar colagens:', error);
            this.showMessage('Erro ao criar colagens', 'error');
        }
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