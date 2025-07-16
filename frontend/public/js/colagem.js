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
        
        // Load persisted used images from localStorage
        this.loadPersistedUsedImages();
        
        this.initializeElements();
        this.loadImages();
        this.attachEventListeners();
    }

    /**
     * Load persisted used images from localStorage
     */
    loadPersistedUsedImages() {
        try {
            const savedUsedImages = localStorage.getItem('colagemUsedImages');
            if (savedUsedImages) {
                const usedImagesArray = JSON.parse(savedUsedImages);
                this.usedInCollages = new Set(usedImagesArray);
            }
        } catch (error) {
            console.error('Erro ao carregar imagens marcadas do localStorage:', error);
            this.usedInCollages = new Set();
        }
    }

    /**
     * Save used images to localStorage
     */
    savePersistedUsedImages() {
        try {
            const usedImagesArray = Array.from(this.usedInCollages);
            localStorage.setItem('colagemUsedImages', JSON.stringify(usedImagesArray));
        } catch (error) {
            console.error('Erro ao salvar imagens marcadas no localStorage:', error);
        }
    }

    /**
     * Toggle used in collage status for an image
     */
    toggleUsedInCollage(imageId) {
        if (this.usedInCollages.has(imageId)) {
            this.usedInCollages.delete(imageId);
            this.showMessage('Imagem desmarcada como colada!', 'info');
        } else {
            this.usedInCollages.add(imageId);
            this.showMessage('Imagem marcada como colada!', 'success');
        }
        
        // Save to localStorage
        this.savePersistedUsedImages();
        
        // Update visual indicators
        this.updateImageUsedStatus(imageId);
    }

    /**
     * Update visual status of a specific image
     */
    updateImageUsedStatus(imageId) {
        const card = document.querySelector(`[data-image-id="${imageId}"]`);
        if (card) {
            const isUsed = this.usedInCollages.has(imageId);
            
            if (isUsed) {
                card.classList.add('used-in-collage');
                
                // Add check mark if not already present
                if (!card.querySelector('.collage-check-mark')) {
                    const checkMark = document.createElement('div');
                    checkMark.className = 'collage-check-mark';
                    checkMark.innerHTML = '<i class="bi bi-check"></i>';
                    card.insertBefore(checkMark, card.firstChild);
                }
            } else {
                card.classList.remove('used-in-collage');
                
                // Remove check mark if present
                const checkMark = card.querySelector('.collage-check-mark');
                if (checkMark) {
                    checkMark.remove();
                }
            }
            
            // Update the toggle button
            this.updateToggleButton(card, isUsed);
        }
    }

    /**
     * Clear all used in collage markings
     */
    clearAllUsedMarkings() {
        if (this.usedInCollages.size === 0) {
            this.showMessage('Não há imagens marcadas como coladas!', 'info');
            return;
        }
        
        if (confirm('Tem certeza que deseja desmarcar todas as imagens como coladas?')) {
            // Clear the set
            this.usedInCollages.clear();
            
            // Save to localStorage
            this.savePersistedUsedImages();
            
            // Update all image cards
            document.querySelectorAll('.image-card').forEach(card => {
                const imageId = card.dataset.imageId;
                if (imageId) {
                    this.updateImageUsedStatus(imageId);
                }
            });
            
            this.showMessage('Todas as marcações foram removidas!', 'success');
        }
    }

    /**
     * Update the toggle button appearance based on used status
     */
    updateToggleButton(card, isUsed) {
        const toggleButton = card.querySelector('.image-actions button:first-child');
        if (toggleButton) {
            const toggleButtonText = isUsed ? 'Desmarcar' : 'Marcar como Colada';
            const toggleButtonIcon = isUsed ? 'bi-x-circle' : 'bi-check-circle';
            const toggleButtonClass = isUsed ? 'btn-outline-warning' : 'btn-outline-success';
            
            // Remove old classes
            toggleButton.classList.remove('btn-outline-warning', 'btn-outline-success');
            // Add new class
            toggleButton.classList.add(toggleButtonClass);
            
            // Update icon
            const icon = toggleButton.querySelector('i');
            if (icon) {
                icon.className = `bi ${toggleButtonIcon}`;
            }
            
            // Update title
            toggleButton.title = toggleButtonText;
        }
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
        this.groupNameInput = document.getElementById('groupNameInput');
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
        
        // Determine button text and icon based on current status
        const isUsed = this.usedInCollages.has(imageId);
        const toggleButtonText = isUsed ? 'Desmarcar' : 'Marcar como Colada';
        const toggleButtonIcon = isUsed ? 'bi-x-circle' : 'bi-check-circle';
        const toggleButtonClass = isUsed ? 'btn-outline-warning' : 'btn-outline-success';
        
        card.innerHTML = `
            ${checkMarkHtml}
            <img src="${imageUrl}" alt="${this.escapeHtml(displayName)}" loading="lazy">
            <div class="image-info">
                <div class="image-name" title="${this.escapeHtml(displayName)}">
                    ${this.escapeHtml(this.truncateText(displayName, 30))}
                </div>
                <div class="image-actions">
                    <button class="btn ${toggleButtonClass} btn-action" 
                            onclick="colagemManager.toggleUsedInCollage('${imageId}')" 
                            title="${toggleButtonText}">
                        <i class="bi ${toggleButtonIcon}"></i>
                    </button>
                    <button class="btn btn-outline-primary btn-action" 
                            onclick="colagemManager.viewImage('${imageUrl}')" 
                            title="Visualizar">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-outline-info btn-action" 
                            onclick="colagemManager.downloadImageFromCard('${imageId}')" 
                            title="Baixar">
                        <i class="bi bi-download"></i>
                    </button>
                </div>
            </div>
        `;
        
        // Add click event for image selection for collage
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
     * Download image from card
     */
    downloadImageFromCard(imageId) {
        const imageData = this.findImageById(imageId);
        if (imageData) {
            this.downloadImage(imageData);
        }
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
        
        // Update group name input with default value if empty
        if (this.groupNameInput && !this.groupNameInput.value.trim()) {
            this.groupNameInput.value = `Grupo ${this.currentGroupNumber}`;
        }
        
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
        
        // Get group name from input
        const groupName = this.groupNameInput ? this.groupNameInput.value.trim() : `Grupo ${this.currentGroupNumber}`;
        if (!groupName) {
            this.showMessage('Por favor, insira um nome para o grupo!', 'warning');
            return;
        }
        
        // Add current selection to groups
        this.collageGroups.push({
            id: Date.now(),
            groupNumber: this.currentGroupNumber,
            groupName: groupName,
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
        
        // Increment group number and clear input for next group
        this.currentGroupNumber++;
        if (this.groupNameInput) {
            this.groupNameInput.value = '';
        }
        
        this.updateSelectionPanel();
        this.showMessage(`${groupName} adicionado à fila!`, 'success');
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
                    <small><strong>${group.groupName || `Grupo ${group.groupNumber}`}</strong> - ${group.images.length} imagens</small>
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
                        images: group.images.map(img => img.id),
                        groupName: group.groupName || `Grupo ${group.groupNumber}`
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
                
                // Save to localStorage
                this.savePersistedUsedImages();
                
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
     * Show message to user with improved toast system
     */
    showMessage(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
                pointer-events: none;
            `;
            document.body.appendChild(toastContainer);
        }

        const toast = document.createElement('div');
        const alertClass = type === 'success' ? 'alert-success' : 
                          type === 'warning' ? 'alert-warning' : 
                          type === 'error' ? 'alert-danger' : 'alert-info';
        
        const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        toast.id = toastId;
        toast.className = `alert ${alertClass} alert-dismissible fade show mb-2`;
        toast.style.cssText = `
            min-width: 300px;
            max-width: 400px;
            pointer-events: auto;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease-in-out;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: none;
            border-radius: 8px;
        `;
        
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px;">
                <i class="bi ${this.getToastIcon(type)}" style="font-size: 1.1em;"></i>
                <span style="flex: 1;">${this.escapeHtml(message)}</span>
                <button type="button" class="btn-close" onclick="dismissToast('${toastId}')" aria-label="Fechar" style="font-size: 0.8em;"></button>
            </div>
        `;

        // Add to container
        toastContainer.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        });

        // Auto dismiss after 4 seconds with fade out
        setTimeout(() => {
            this.dismissToast(toastId);
        }, 4000);
    }

    /**
     * Get appropriate icon for toast type
     */
    getToastIcon(type) {
        switch(type) {
            case 'success': return 'bi-check-circle-fill';
            case 'warning': return 'bi-exclamation-triangle-fill';
            case 'error': return 'bi-x-circle-fill';
            default: return 'bi-info-circle-fill';
        }
    }

    /**
     * Dismiss a specific toast with fade out animation
     */
    dismissToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            // Fade out animation
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            
            // Remove from DOM after animation
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                    
                    // Clean up container if empty
                    const container = document.getElementById('toast-container');
                    if (container && container.children.length === 0) {
                        container.remove();
                    }
                }
            }, 300);
        }
    }

    /**
     * Clear all toasts
     */
    clearAllToasts() {
        const container = document.getElementById('toast-container');
        if (container) {
            // Fade out all toasts
            Array.from(container.children).forEach((toast, index) => {
                setTimeout(() => {
                    if (toast) {
                        toast.style.opacity = '0';
                        toast.style.transform = 'translateX(100%)';
                    }
                }, index * 100); // Stagger the animations
            });
            
            // Remove container after all animations
            setTimeout(() => {
                if (container.parentNode) {
                    container.parentNode.removeChild(container);
                }
            }, 500);
        }
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

function dismissToast(toastId) {
    if (window.colagemManager) {
        window.colagemManager.dismissToast(toastId);
    }
}

function clearAllToasts() {
    if (window.colagemManager) {
        window.colagemManager.clearAllToasts();
    }
}

function clearAllUsedMarkings() {
    if (window.colagemManager) {
        window.colagemManager.clearAllUsedMarkings();
    }
}

// Initialize the application
const colagemManager = new ColagemManager();
window.colagemManager = colagemManager;

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    // Cleanup if needed
});