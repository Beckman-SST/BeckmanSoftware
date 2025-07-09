/**
 * Main Application Module
 * Initializes and coordinates all application modules
 */

class App {
    constructor() {
        this.managers = {};
        this.isInitialized = false;
        this.config = {
            apiBaseUrl: this.determineApiUrl(),
            maxFileSize: 100 * 1024 * 1024, // 100MB
            allowedTypes: ['image/*', 'video/*'],
            statusCheckInterval: 1000,
            maxRetries: 3
        };
        
        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('Initializing RePosture Application...');
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }
            
            // Initialize managers in order
            await this.initializeManagers();
            
            // Setup global event listeners
            this.setupGlobalEventListeners();
            
            // Setup error handling
            this.setupErrorHandling();
            
            // Check server health
            await this.checkServerHealth();
            
            // Mark as initialized
            this.isInitialized = true;
            
            console.log('Application initialized successfully');
            
            // Show welcome message
            this.showWelcomeMessage();
            
        } catch (error) {
            console.error('Failed to initialize application:', error);
            this.handleInitializationError(error);
        }
    }

    /**
     * Initialize all managers
     */
    async initializeManagers() {
        // Initialize Flash Manager first (needed by others)
        this.managers.flash = new FlashManager();
        window.flashManager = this.managers.flash;
        
        // Initialize API Manager
        this.managers.api = new ApiManager();
        window.apiManager = this.managers.api;
        
        // Initialize Navigation Manager
        this.managers.navigation = new NavigationManager();
        window.navigationManager = this.managers.navigation;
        
        // Initialize Upload Manager
        this.managers.upload = new UploadManager(this.managers.api);
        window.uploadManager = this.managers.upload;
        
        // Initialize Status Manager
        this.managers.status = new StatusManager(this.managers.api);
        window.statusManager = this.managers.status;
        
        // Initialize Results Manager
        this.managers.results = new ResultsManager(this.managers.api);
        window.resultsManager = this.managers.results;
        
        // Initialize Config Manager
        this.managers.config = new ConfigManager(this.managers.api);
        window.configManager = this.managers.config;
        
        console.log('All managers initialized');
    }

    /**
     * Setup global event listeners
     */
    setupGlobalEventListeners() {
        // Listen for section changes
        document.addEventListener('sectionChanged', (e) => {
            this.handleSectionChange(e.detail.section, e.detail.previousSection);
        });
        
        // Listen for API errors
        document.addEventListener('apiError', (e) => {
            this.handleApiError(e.detail);
        });
        
        // Listen for network status changes
        window.addEventListener('online', () => {
            this.handleNetworkStatusChange(true);
        });
        
        window.addEventListener('offline', () => {
            this.handleNetworkStatusChange(false);
        });
        
        // Listen for visibility changes (tab switching)
        document.addEventListener('visibilitychange', () => {
            this.handleVisibilityChange();
        });
        
        // Listen for beforeunload (page refresh/close)
        window.addEventListener('beforeunload', (e) => {
            this.handleBeforeUnload(e);
        });
        
        // Listen for keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleGlobalKeyboard(e);
        });
    }

    /**
     * Setup global error handling
     */
    setupErrorHandling() {
        // Handle uncaught errors
        window.addEventListener('error', (e) => {
            console.error('Uncaught error:', e.error);
            this.managers.flash?.error(
                'Ocorreu um erro inesperado. Por favor, recarregue a página.',
                10000,
                true
            );
        });
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            this.managers.flash?.error(
                'Erro de comunicação. Verifique sua conexão.',
                8000
            );
        });
    }

    /**
     * Check server health
     */
    async checkServerHealth() {
        try {
            const health = await this.managers.api.checkHealth();
            
            if (health.status === 'ok') {
                console.log('Server is healthy');
            } else {
                throw new Error('Server health check failed');
            }
        } catch (error) {
            console.warn('Server health check failed:', error);
            this.managers.flash?.warning(
                'Não foi possível conectar ao servidor. Algumas funcionalidades podem não estar disponíveis.',
                8000
            );
        }
    }

    /**
     * Handle section changes
     */
    handleSectionChange(section, previousSection) {
        console.log(`Section changed: ${previousSection} -> ${section}`);
        
        // Update page title
        this.updatePageTitle(section);
        
        // Handle section-specific logic
        switch (section) {
            case 'upload':
                // Reset upload if coming from other sections
                if (previousSection && previousSection !== 'upload') {
                    this.managers.upload?.reset();
                }
                break;
                
            case 'status':
                // Ensure status monitoring is active if processing
                if (!this.managers.status?.isMonitoringActive()) {
                    this.checkIfShouldStartMonitoring();
                }
                break;
                
            case 'results':
                // Load results when entering results section
                this.managers.results?.loadResults();
                break;
                
            case 'config':
                // Load config when entering config section
                this.managers.config?.loadConfig();
                break;
        }
    }

    /**
     * Handle API errors
     */
    handleApiError(error) {
        console.error('API Error:', error);
        
        if (error.status === 0 || error.status >= 500) {
            this.managers.flash?.error(
                'Erro de conexão com o servidor. Verifique sua conexão.',
                8000
            );
        } else if (error.status === 404) {
            this.managers.flash?.error(
                'Recurso não encontrado.',
                5000
            );
        } else if (error.status >= 400 && error.status < 500) {
            this.managers.flash?.error(
                error.message || 'Erro na requisição.',
                5000
            );
        }
    }

    /**
     * Handle network status changes
     */
    handleNetworkStatusChange(isOnline) {
        if (isOnline) {
            this.managers.flash?.success('Conexão restaurada', 3000);
            
            // Retry failed operations
            this.retryFailedOperations();
        } else {
            this.managers.flash?.warning(
                'Conexão perdida. Algumas funcionalidades podem não estar disponíveis.',
                0,
                true
            );
        }
    }

    /**
     * Handle visibility changes
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // Page is hidden - pause non-critical operations
            console.log('Page hidden - pausing operations');
        } else {
            // Page is visible - resume operations
            console.log('Page visible - resuming operations');
            
            // Check if we need to refresh status
            if (this.managers.status?.isMonitoringActive()) {
                this.managers.status.checkStatus();
            }
        }
    }

    /**
     * Handle before unload
     */
    handleBeforeUnload(e) {
        // Check if there are ongoing operations
        const hasUploads = this.managers.upload?.isUploadInProgress();
        const hasProcessing = this.managers.status?.isMonitoringActive();
        
        if (hasUploads || hasProcessing) {
            const message = 'Existem operações em andamento. Tem certeza que deseja sair?';
            e.preventDefault();
            e.returnValue = message;
            return message;
        }
    }

    /**
     * Handle global keyboard shortcuts
     */
    handleGlobalKeyboard(e) {
        // Only handle if no input is focused
        if (document.activeElement.tagName === 'INPUT' || 
            document.activeElement.tagName === 'TEXTAREA' ||
            document.activeElement.tagName === 'SELECT') {
            return;
        }
        
        // Ctrl/Cmd + R - Refresh results
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            if (this.managers.navigation?.getCurrentSection() === 'results') {
                this.managers.results?.loadResults();
            }
        }
        
        // Ctrl/Cmd + U - Go to upload
        if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
            e.preventDefault();
            this.managers.navigation?.showSection('upload');
        }
        
        // F5 - Refresh current section
        if (e.key === 'F5') {
            e.preventDefault();
            this.refreshCurrentSection();
        }
    }

    /**
     * Update page title based on current section
     */
    updatePageTitle(section) {
        const titles = {
            upload: 'Upload - RePosture',
            status: 'Status - RePosture',
            results: 'Resultados - RePosture',
            config: 'Configurações - RePosture'
        };
        
        document.title = titles[section] || 'RePosture';
    }

    /**
     * Check if should start monitoring
     */
    async checkIfShouldStartMonitoring() {
        try {
            const status = await this.managers.api.getStatus();
            if (status.processing) {
                this.managers.status?.startMonitoring();
            }
        } catch (error) {
            console.warn('Could not check processing status:', error);
        }
    }

    /**
     * Retry failed operations
     */
    retryFailedOperations() {
        // This could be expanded to retry specific failed operations
        console.log('Retrying failed operations...');
    }

    /**
     * Refresh current section
     */
    refreshCurrentSection() {
        const currentSection = this.managers.navigation?.getCurrentSection();
        
        switch (currentSection) {
            case 'results':
                this.managers.results?.loadResults();
                break;
            case 'config':
                this.managers.config?.loadConfig();
                break;
            case 'status':
                this.managers.status?.checkStatus();
                break;
        }
        
        this.managers.flash?.info('Seção atualizada', 2000);
    }

    /**
     * Show welcome message
     */
    showWelcomeMessage() {
        // Only show on first visit
        if (!localStorage.getItem('reposture_welcomed')) {
            setTimeout(() => {
                this.managers.flash?.info(
                    'Bem-vindo ao RePosture! Faça upload de suas imagens e vídeos para análise de postura.',
                    8000
                );
                localStorage.setItem('reposture_welcomed', 'true');
            }, 1000);
        }
    }

    /**
     * Handle initialization error
     */
    handleInitializationError(error) {
        console.error('Initialization error:', error);
        
        // Show error message
        const errorContainer = document.createElement('div');
        errorContainer.className = 'alert alert-danger m-3';
        errorContainer.innerHTML = `
            <h4>Erro de Inicialização</h4>
            <p>Não foi possível inicializar a aplicação. Por favor, recarregue a página.</p>
            <button class="btn btn-primary" onclick="window.location.reload()">Recarregar</button>
        `;
        
        document.body.insertBefore(errorContainer, document.body.firstChild);
    }

    /**
     * Determine API URL
     */
    determineApiUrl() {
        // Check if running in development
        if (window.location.hostname === 'localhost' || 
            window.location.hostname === '127.0.0.1' ||
            window.location.hostname === '') {
            return 'http://localhost:5000';
        }
        
        // Production - use same origin
        return window.location.origin;
    }

    /**
     * Get manager instance
     */
    getManager(name) {
        return this.managers[name];
    }

    /**
     * Check if app is initialized
     */
    isReady() {
        return this.isInitialized;
    }

    /**
     * Get app configuration
     */
    getConfig() {
        return { ...this.config };
    }

    /**
     * Update app configuration
     */
    updateConfig(newConfig) {
        this.config = { ...this.config, ...newConfig };
    }

    /**
     * Reset application state
     */
    reset() {
        // Reset all managers
        Object.values(this.managers).forEach(manager => {
            if (manager.reset) {
                manager.reset();
            }
        });
        
        // Clear flash messages
        this.managers.flash?.clear();
        
        // Go to upload section
        this.managers.navigation?.showSection('upload');
        
        console.log('Application reset');
    }

    /**
     * Cleanup and destroy
     */
    destroy() {
        // Stop all ongoing operations
        this.managers.status?.stopMonitoring();
        
        // Clear all managers
        Object.keys(this.managers).forEach(key => {
            delete window[key + 'Manager'];
            delete this.managers[key];
        });
        
        this.isInitialized = false;
        console.log('Application destroyed');
    }
}

// Initialize application when script loads
let app;

// Wait for all required classes to be loaded
function initializeApp() {
    if (typeof FlashManager !== 'undefined' &&
        typeof ApiManager !== 'undefined' &&
        typeof NavigationManager !== 'undefined' &&
        typeof UploadManager !== 'undefined' &&
        typeof StatusManager !== 'undefined' &&
        typeof ResultsManager !== 'undefined' &&
        typeof ConfigManager !== 'undefined') {
        
        app = new App();
        window.app = app;
    } else {
        // Retry after a short delay
        setTimeout(initializeApp, 100);
    }
}

// Start initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Export for use in other modules
window.App = App;