/**
 * Navigation Management Module
 * Handles section switching and navigation state
 */

class NavigationManager {
    constructor() {
        this.currentSection = 'upload';
        this.sections = ['upload', 'status', 'results', 'config'];
        this.history = [];
        
        this.initializeElements();
        this.attachEventListeners();
        this.initializeNavigation();
    }

    /**
     * Initialize DOM elements
     */
    initializeElements() {
        this.navButtons = document.querySelectorAll('.nav-btn');
        this.sectionElements = {};
        
        // Map section elements
        this.sections.forEach(section => {
            this.sectionElements[section] = document.getElementById(`${section}-section`);
        });
        
        // Additional elements
        this.navbar = document.querySelector('.navbar');
        this.breadcrumb = document.getElementById('breadcrumb');
        this.backBtn = document.getElementById('btn-back');
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Navigation buttons
        this.navButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const section = btn.dataset.section;
                if (section) {
                    this.showSection(section);
                }
            });
        });

        // Back button
        if (this.backBtn) {
            this.backBtn.addEventListener('click', () => {
                this.goBack();
            });
        }

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });

        // Browser back/forward
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.section) {
                this.showSection(e.state.section, false);
            }
        });
    }

    /**
     * Initialize navigation state
     */
    initializeNavigation() {
        // Check URL hash for initial section
        const hash = window.location.hash.substring(1);
        const initialSection = this.sections.includes(hash) ? hash : 'upload';
        
        this.showSection(initialSection, false);
    }

    /**
     * Show specific section
     */
    showSection(sectionName, addToHistory = true) {
        if (!this.sections.includes(sectionName)) {
            console.warn(`Unknown section: ${sectionName}`);
            return;
        }

        // Add current section to history
        if (addToHistory && this.currentSection !== sectionName) {
            this.history.push(this.currentSection);
            
            // Limit history size
            if (this.history.length > 10) {
                this.history.shift();
            }
        }

        // Hide all sections
        Object.values(this.sectionElements).forEach(element => {
            if (element) {
                element.style.display = 'none';
                element.classList.remove('active');
            }
        });

        // Show target section
        const targetElement = this.sectionElements[sectionName];
        if (targetElement) {
            targetElement.style.display = 'block';
            targetElement.classList.add('active');
            
            // Add entrance animation
            targetElement.style.opacity = '0';
            targetElement.style.transform = 'translateY(20px)';
            
            requestAnimationFrame(() => {
                targetElement.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                targetElement.style.opacity = '1';
                targetElement.style.transform = 'translateY(0)';
            });
        }

        // Update navigation state
        this.currentSection = sectionName;
        this.updateNavButtons();
        this.updateBreadcrumb();
        this.updateBackButton();
        this.updateUrl();

        // Trigger section-specific actions
        this.handleSectionChange(sectionName);

        // Emit custom event
        this.emitNavigationEvent(sectionName);
    }

    /**
     * Update navigation buttons
     */
    updateNavButtons() {
        this.navButtons.forEach(btn => {
            const isActive = btn.dataset.section === this.currentSection;
            btn.classList.toggle('active', isActive);
            
            // Update ARIA attributes
            btn.setAttribute('aria-current', isActive ? 'page' : 'false');
        });
    }

    /**
     * Update breadcrumb
     */
    updateBreadcrumb() {
        if (!this.breadcrumb) return;

        const sectionNames = {
            upload: 'Upload',
            status: 'Status',
            results: 'Resultados',
            config: 'Configurações'
        };

        const breadcrumbItems = [];
        
        // Add home
        breadcrumbItems.push(`<li class="breadcrumb-item"><a href="#upload">Início</a></li>`);
        
        // Add current section if not upload
        if (this.currentSection !== 'upload') {
            breadcrumbItems.push(
                `<li class="breadcrumb-item active" aria-current="page">${sectionNames[this.currentSection]}</li>`
            );
        }

        this.breadcrumb.innerHTML = breadcrumbItems.join('');
    }

    /**
     * Update back button
     */
    updateBackButton() {
        if (!this.backBtn) return;

        const canGoBack = this.history.length > 0;
        this.backBtn.style.display = canGoBack ? 'inline-block' : 'none';
        this.backBtn.disabled = !canGoBack;
    }

    /**
     * Update URL
     */
    updateUrl() {
        const newUrl = `${window.location.pathname}#${this.currentSection}`;
        
        // Update URL without triggering popstate
        history.pushState(
            { section: this.currentSection }, 
            '', 
            newUrl
        );
    }

    /**
     * Go back to previous section
     */
    goBack() {
        if (this.history.length > 0) {
            const previousSection = this.history.pop();
            this.showSection(previousSection, false);
        }
    }

    /**
     * Handle section-specific actions
     */
    handleSectionChange(sectionName) {
        switch (sectionName) {
            case 'upload':
                // Focus on file input or upload area
                const fileInput = document.getElementById('files');
                if (fileInput) {
                    setTimeout(() => fileInput.focus(), 100);
                }
                break;
                
            case 'status':
                // Start status monitoring if not already active
                if (window.statusManager && !window.statusManager.isMonitoringActive()) {
                    window.statusManager.startMonitoring();
                }
                break;
                
            case 'results':
                // Load results if not already loaded
                if (window.resultsManager) {
                    window.resultsManager.loadResults();
                }
                break;
                
            case 'config':
                // Load configuration
                if (window.configManager) {
                    window.configManager.loadConfig();
                }
                break;
        }
    }

    /**
     * Handle keyboard navigation
     */
    handleKeyboardNavigation(e) {
        // Only handle if no input is focused
        if (document.activeElement.tagName === 'INPUT' || 
            document.activeElement.tagName === 'TEXTAREA' ||
            document.activeElement.tagName === 'SELECT') {
            return;
        }

        switch (e.key) {
            case 'ArrowLeft':
            case 'ArrowUp':
                e.preventDefault();
                this.navigateToPrevious();
                break;
                
            case 'ArrowRight':
            case 'ArrowDown':
                e.preventDefault();
                this.navigateToNext();
                break;
                
            case 'Escape':
                e.preventDefault();
                this.goBack();
                break;
                
            case '1':
                e.preventDefault();
                this.showSection('upload');
                break;
                
            case '2':
                e.preventDefault();
                this.showSection('status');
                break;
                
            case '3':
                e.preventDefault();
                this.showSection('results');
                break;
                
            case '4':
                e.preventDefault();
                this.showSection('config');
                break;
        }
    }

    /**
     * Navigate to previous section
     */
    navigateToPrevious() {
        const currentIndex = this.sections.indexOf(this.currentSection);
        const previousIndex = currentIndex > 0 ? currentIndex - 1 : this.sections.length - 1;
        this.showSection(this.sections[previousIndex]);
    }

    /**
     * Navigate to next section
     */
    navigateToNext() {
        const currentIndex = this.sections.indexOf(this.currentSection);
        const nextIndex = currentIndex < this.sections.length - 1 ? currentIndex + 1 : 0;
        this.showSection(this.sections[nextIndex]);
    }

    /**
     * Emit navigation event
     */
    emitNavigationEvent(sectionName) {
        const event = new CustomEvent('sectionChanged', {
            detail: {
                section: sectionName,
                previousSection: this.history[this.history.length - 1] || null
            }
        });
        
        document.dispatchEvent(event);
    }

    /**
     * Get current section
     */
    getCurrentSection() {
        return this.currentSection;
    }

    /**
     * Check if section exists
     */
    hasSection(sectionName) {
        return this.sections.includes(sectionName);
    }

    /**
     * Get navigation history
     */
    getHistory() {
        return [...this.history];
    }

    /**
     * Clear navigation history
     */
    clearHistory() {
        this.history = [];
        this.updateBackButton();
    }

    /**
     * Add section to navigation
     */
    addSection(sectionName, element) {
        if (!this.sections.includes(sectionName)) {
            this.sections.push(sectionName);
            this.sectionElements[sectionName] = element;
        }
    }

    /**
     * Remove section from navigation
     */
    removeSection(sectionName) {
        const index = this.sections.indexOf(sectionName);
        if (index > -1) {
            this.sections.splice(index, 1);
            delete this.sectionElements[sectionName];
            
            // If current section is removed, go to upload
            if (this.currentSection === sectionName) {
                this.showSection('upload');
            }
        }
    }

    /**
     * Set section visibility
     */
    setSectionVisibility(sectionName, visible) {
        const navBtn = document.querySelector(`[data-section="${sectionName}"]`);
        if (navBtn) {
            navBtn.style.display = visible ? 'block' : 'none';
        }
    }

    /**
     * Enable/disable section
     */
    setSectionEnabled(sectionName, enabled) {
        const navBtn = document.querySelector(`[data-section="${sectionName}"]`);
        if (navBtn) {
            navBtn.disabled = !enabled;
            navBtn.classList.toggle('disabled', !enabled);
        }
    }

    /**
     * Show loading state for section
     */
    setSectionLoading(sectionName, loading) {
        const navBtn = document.querySelector(`[data-section="${sectionName}"]`);
        if (navBtn) {
            const icon = navBtn.querySelector('i');
            if (loading) {
                if (icon) {
                    icon.className = 'bi bi-arrow-clockwise spin';
                }
                navBtn.disabled = true;
            } else {
                if (icon) {
                    // Restore original icon based on section
                    const iconMap = {
                        upload: 'bi-cloud-upload',
                        status: 'bi-activity',
                        results: 'bi-grid-3x3-gap',
                        config: 'bi-gear'
                    };
                    icon.className = `bi ${iconMap[sectionName] || 'bi-circle'}`;
                }
                navBtn.disabled = false;
            }
        }
    }

    /**
     * Reset navigation to initial state
     */
    reset() {
        this.clearHistory();
        this.showSection('upload', false);
    }

    /**
     * Get section progress indicator
     */
    setSectionProgress(sectionName, progress) {
        const navBtn = document.querySelector(`[data-section="${sectionName}"]`);
        if (navBtn) {
            let progressBar = navBtn.querySelector('.nav-progress');
            
            if (!progressBar) {
                progressBar = document.createElement('div');
                progressBar.className = 'nav-progress';
                navBtn.appendChild(progressBar);
            }
            
            if (progress > 0 && progress < 100) {
                progressBar.style.width = `${progress}%`;
                progressBar.style.display = 'block';
            } else {
                progressBar.style.display = 'none';
            }
        }
    }
}

// Export for use in other modules
window.NavigationManager = NavigationManager;