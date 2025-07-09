/**
 * Flash Messages Management Module
 * Handles display of notifications and alerts
 */

class FlashManager {
    constructor() {
        this.messages = [];
        this.maxMessages = 5;
        this.defaultDuration = 5000; // 5 seconds
        this.container = null;
        
        this.initializeContainer();
        this.attachEventListeners();
    }

    /**
     * Initialize flash messages container
     */
    initializeContainer() {
        // Look for existing container
        this.container = document.getElementById('flash-messages');
        
        // Create container if it doesn't exist
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'flash-messages';
            this.container.className = 'flash-messages-container';
            
            // Insert at the beginning of body
            document.body.insertBefore(this.container, document.body.firstChild);
        }
        
        // Ensure container has proper styling
        this.container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
            pointer-events: none;
        `;
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Listen for custom flash events
        document.addEventListener('flash', (e) => {
            this.show(e.detail.message, e.detail.type, e.detail.duration);
        });
        
        // Listen for API responses that might contain flash messages
        document.addEventListener('apiResponse', (e) => {
            if (e.detail.flash) {
                this.show(e.detail.flash.message, e.detail.flash.type);
            }
        });
    }

    /**
     * Show flash message
     */
    show(message, type = 'info', duration = null, persistent = false) {
        if (!message) return;
        
        const messageObj = {
            id: this.generateId(),
            message: message,
            type: this.validateType(type),
            duration: duration || this.defaultDuration,
            persistent: persistent,
            timestamp: Date.now()
        };
        
        // Add to messages array
        this.messages.push(messageObj);
        
        // Remove oldest messages if exceeding limit
        while (this.messages.length > this.maxMessages) {
            const oldestMessage = this.messages.shift();
            this.removeMessage(oldestMessage.id);
        }
        
        // Create and show message element
        this.createMessageElement(messageObj);
        
        // Auto-remove after duration (if not persistent)
        if (!persistent && messageObj.duration > 0) {
            setTimeout(() => {
                this.hide(messageObj.id);
            }, messageObj.duration);
        }
        
        return messageObj.id;
    }

    /**
     * Create message DOM element
     */
    createMessageElement(messageObj) {
        const element = document.createElement('div');
        element.id = `flash-${messageObj.id}`;
        element.className = `alert alert-${messageObj.type} alert-dismissible fade show flash-message`;
        element.style.cssText = `
            pointer-events: auto;
            margin-bottom: 10px;
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border: none;
            border-radius: 8px;
        `;
        
        // Get appropriate icon
        const icon = this.getIcon(messageObj.type);
        
        element.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="${icon} me-2 mt-1 flex-shrink-0"></i>
                <div class="flex-grow-1">
                    <div class="flash-message-content">${this.escapeHtml(messageObj.message)}</div>
                    ${messageObj.persistent ? '<small class="text-muted">Esta mensagem não será removida automaticamente</small>' : ''}
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Add click handler for close button
        const closeBtn = element.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.hide(messageObj.id);
            });
        }
        
        // Add click handler for message body (optional dismiss)
        if (!messageObj.persistent) {
            element.addEventListener('click', (e) => {
                if (e.target !== closeBtn && !closeBtn.contains(e.target)) {
                    this.hide(messageObj.id);
                }
            });
            
            element.style.cursor = 'pointer';
            element.title = 'Clique para fechar';
        }
        
        // Add to container
        this.container.appendChild(element);
        
        // Trigger entrance animation
        requestAnimationFrame(() => {
            element.classList.add('show');
        });
    }

    /**
     * Hide specific message
     */
    hide(messageId) {
        const element = document.getElementById(`flash-${messageId}`);
        if (element) {
            // Add exit animation
            element.style.animation = 'slideOutRight 0.3s ease-in';
            
            setTimeout(() => {
                this.removeMessage(messageId);
            }, 300);
        }
    }

    /**
     * Remove message from DOM and array
     */
    removeMessage(messageId) {
        const element = document.getElementById(`flash-${messageId}`);
        if (element) {
            element.remove();
        }
        
        this.messages = this.messages.filter(msg => msg.id !== messageId);
    }

    /**
     * Clear all messages
     */
    clear() {
        this.messages.forEach(msg => {
            this.removeMessage(msg.id);
        });
        this.messages = [];
    }

    /**
     * Show success message
     */
    success(message, duration = null, persistent = false) {
        return this.show(message, 'success', duration, persistent);
    }

    /**
     * Show error message
     */
    error(message, duration = null, persistent = false) {
        return this.show(message, 'danger', duration || 8000, persistent);
    }

    /**
     * Show warning message
     */
    warning(message, duration = null, persistent = false) {
        return this.show(message, 'warning', duration || 6000, persistent);
    }

    /**
     * Show info message
     */
    info(message, duration = null, persistent = false) {
        return this.show(message, 'info', duration, persistent);
    }

    /**
     * Show loading message
     */
    loading(message, persistent = true) {
        const messageId = this.show(message, 'info', 0, persistent);
        
        // Add spinner to the message
        const element = document.getElementById(`flash-${messageId}`);
        if (element) {
            const icon = element.querySelector('i');
            if (icon) {
                icon.className = 'spinner-border spinner-border-sm me-2 mt-1 flex-shrink-0';
            }
        }
        
        return messageId;
    }

    /**
     * Update existing message
     */
    update(messageId, newMessage, newType = null) {
        const messageObj = this.messages.find(msg => msg.id === messageId);
        if (!messageObj) return false;
        
        const element = document.getElementById(`flash-${messageId}`);
        if (!element) return false;
        
        // Update message object
        messageObj.message = newMessage;
        if (newType) {
            messageObj.type = this.validateType(newType);
            element.className = `alert alert-${messageObj.type} alert-dismissible fade show flash-message`;
        }
        
        // Update DOM content
        const contentElement = element.querySelector('.flash-message-content');
        if (contentElement) {
            contentElement.innerHTML = this.escapeHtml(newMessage);
        }
        
        // Update icon
        const icon = element.querySelector('i');
        if (icon && newType) {
            icon.className = this.getIcon(messageObj.type) + ' me-2 mt-1 flex-shrink-0';
        }
        
        return true;
    }

    /**
     * Show confirmation dialog
     */
    confirm(message, onConfirm, onCancel = null) {
        const messageId = this.generateId();
        const element = document.createElement('div');
        element.id = `flash-${messageId}`;
        element.className = 'alert alert-warning alert-dismissible fade show flash-message flash-confirm';
        element.style.cssText = `
            pointer-events: auto;
            margin-bottom: 10px;
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border: none;
            border-radius: 8px;
        `;
        
        element.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="bi bi-question-circle me-2 mt-1 flex-shrink-0"></i>
                <div class="flex-grow-1">
                    <div class="flash-message-content">${this.escapeHtml(message)}</div>
                    <div class="mt-2">
                        <button type="button" class="btn btn-sm btn-success me-2 confirm-yes">Sim</button>
                        <button type="button" class="btn btn-sm btn-secondary confirm-no">Não</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listeners
        const yesBtn = element.querySelector('.confirm-yes');
        const noBtn = element.querySelector('.confirm-no');
        
        yesBtn.addEventListener('click', () => {
            this.removeMessage(messageId);
            if (onConfirm) onConfirm();
        });
        
        noBtn.addEventListener('click', () => {
            this.removeMessage(messageId);
            if (onCancel) onCancel();
        });
        
        this.container.appendChild(element);
        
        return messageId;
    }

    /**
     * Validate message type
     */
    validateType(type) {
        const validTypes = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark'];
        return validTypes.includes(type) ? type : 'info';
    }

    /**
     * Get icon for message type
     */
    getIcon(type) {
        const iconMap = {
            success: 'bi bi-check-circle',
            danger: 'bi bi-exclamation-triangle',
            warning: 'bi bi-exclamation-triangle',
            info: 'bi bi-info-circle',
            primary: 'bi bi-info-circle',
            secondary: 'bi bi-info-circle',
            light: 'bi bi-info-circle',
            dark: 'bi bi-info-circle'
        };
        
        return iconMap[type] || 'bi bi-info-circle';
    }

    /**
     * Generate unique ID
     */
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
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
     * Get all active messages
     */
    getMessages() {
        return [...this.messages];
    }

    /**
     * Get message by ID
     */
    getMessage(messageId) {
        return this.messages.find(msg => msg.id === messageId);
    }

    /**
     * Check if message exists
     */
    hasMessage(messageId) {
        return this.messages.some(msg => msg.id === messageId);
    }

    /**
     * Set maximum number of messages
     */
    setMaxMessages(max) {
        this.maxMessages = Math.max(1, max);
        
        // Remove excess messages
        while (this.messages.length > this.maxMessages) {
            const oldestMessage = this.messages.shift();
            this.removeMessage(oldestMessage.id);
        }
    }

    /**
     * Set default duration
     */
    setDefaultDuration(duration) {
        this.defaultDuration = Math.max(0, duration);
    }

    /**
     * Show progress message
     */
    progress(message, progress = 0) {
        const messageId = this.generateId();
        const element = document.createElement('div');
        element.id = `flash-${messageId}`;
        element.className = 'alert alert-info alert-dismissible fade show flash-message flash-progress';
        element.style.cssText = `
            pointer-events: auto;
            margin-bottom: 10px;
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            border: none;
            border-radius: 8px;
        `;
        
        element.innerHTML = `
            <div class="d-flex align-items-start">
                <i class="bi bi-arrow-clockwise spin me-2 mt-1 flex-shrink-0"></i>
                <div class="flex-grow-1">
                    <div class="flash-message-content">${this.escapeHtml(message)}</div>
                    <div class="progress mt-2" style="height: 6px;">
                        <div class="progress-bar" role="progressbar" style="width: ${progress}%" aria-valuenow="${progress}" aria-valuemin="0" aria-valuemax="100"></div>
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        // Add close handler
        const closeBtn = element.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.removeMessage(messageId);
            });
        }
        
        this.container.appendChild(element);
        
        // Add to messages array
        this.messages.push({
            id: messageId,
            message: message,
            type: 'info',
            duration: 0,
            persistent: true,
            timestamp: Date.now()
        });
        
        return messageId;
    }

    /**
     * Update progress message
     */
    updateProgress(messageId, progress, newMessage = null) {
        const element = document.getElementById(`flash-${messageId}`);
        if (!element) return false;
        
        const progressBar = element.querySelector('.progress-bar');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
            progressBar.setAttribute('aria-valuenow', progress);
        }
        
        if (newMessage) {
            const contentElement = element.querySelector('.flash-message-content');
            if (contentElement) {
                contentElement.innerHTML = this.escapeHtml(newMessage);
            }
        }
        
        return true;
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .spin {
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .flash-message {
        transition: all 0.3s ease;
    }
    
    .flash-message:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2) !important;
    }
`;
document.head.appendChild(style);

// Export for use in other modules
window.FlashManager = FlashManager;