/**
 * API Communication Module
 * Handles all backend communication and API calls
 */

class ApiManager {
    constructor() {
        this.baseUrl = this.getApiUrl();
        this.isOnline = navigator.onLine;
        this.setupNetworkListeners();
    }

    /**
     * Determine API URL based on environment
     */
    getApiUrl() {
        // Check if running locally
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:5000';
        }
        // Production URL
        return 'https://reposture-backend.onrender.com';
    }

    /**
     * Setup network status listeners
     */
    setupNetworkListeners() {
        window.addEventListener('online', () => {
            this.isOnline = true;
            this.showNetworkStatus('Conexão restaurada', 'success');
        });

        window.addEventListener('offline', () => {
            this.isOnline = false;
            this.showNetworkStatus('Sem conexão com a internet', 'warning');
        });
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async request(endpoint, options = {}) {
        if (!this.isOnline) {
            throw new Error('Sem conexão com a internet');
        }

        const url = `${this.baseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        };

        try {
            const response = await fetch(url, defaultOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return response;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    /**
     * Upload files to backend
     */
    async uploadFiles(files, onProgress = null) {
        const formData = new FormData();
        
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        try {
            const xhr = new XMLHttpRequest();
            
            return new Promise((resolve, reject) => {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable && onProgress) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });

                xhr.addEventListener('load', () => {
                    if (xhr.status === 200) {
                        try {
                            const response = JSON.parse(xhr.responseText);
                            resolve(response);
                        } catch (error) {
                            reject(new Error('Invalid JSON response'));
                        }
                    } else {
                        reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
                    }
                });

                xhr.addEventListener('error', () => {
                    reject(new Error('Upload failed: Network error'));
                });

                xhr.addEventListener('timeout', () => {
                    reject(new Error('Upload failed: Timeout'));
                });

                xhr.open('POST', `${this.baseUrl}/upload`);
                xhr.timeout = 300000; // 5 minutes timeout
                xhr.send(formData);
            });
        } catch (error) {
            console.error('Upload error:', error);
            throw error;
        }
    }

    /**
     * Get processing status
     */
    async getStatus() {
        return await this.request('/status');
    }

    /**
     * Cancel current processing
     */
    async cancelProcessing() {
        return await this.request('/cancelar', {
            method: 'POST'
        });
    }

    /**
     * Get processed files list
     */
    async getProcessedFiles() {
        return await this.request('/processed_files');
    }

    /**
     * Clear temporary files
     */
    async clearTemporaryFiles() {
        return await this.request('/limpar', {
            method: 'POST'
        });
    }

    /**
     * Open output folder
     */
    async openOutputFolder() {
        return await this.request('/abrir-pasta');
    }

    /**
     * Get configuration
     */
    async getConfig() {
        return await this.request('/config');
    }

    /**
     * Save configuration
     */
    async saveConfig(configData) {
        return await this.request('/save_config', {
            method: 'POST',
            body: JSON.stringify(configData)
        });
    }

    /**
     * Get file URL for display
     */
    getFileUrl(filename) {
        return `${this.baseUrl}/output_file/${encodeURIComponent(filename)}`;
    }

    /**
     * Get merge file URL
     */
    getMergeFileUrl(filename) {
        return `${this.baseUrl}/merge/${encodeURIComponent(filename)}`;
    }

    /**
     * Get errors list
     */
    async getErrors() {
        return await this.request('/get_errors');
    }

    /**
     * Merge selected images
     */
    async mergeImages(imageList) {
        return await this.request('/unir_imagens', {
            method: 'POST',
            body: JSON.stringify({ images: imageList })
        });
    }

    /**
     * Health check
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                timeout: 5000
            });
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    /**
     * Retry mechanism for failed requests
     */
    async requestWithRetry(endpoint, options = {}, maxRetries = 3) {
        let lastError;
        
        for (let i = 0; i <= maxRetries; i++) {
            try {
                return await this.request(endpoint, options);
            } catch (error) {
                lastError = error;
                
                if (i < maxRetries) {
                    // Exponential backoff
                    const delay = Math.pow(2, i) * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                    console.log(`Retrying request to ${endpoint} (attempt ${i + 2}/${maxRetries + 1})`);
                }
            }
        }
        
        throw lastError;
    }

    /**
     * Batch file operations
     */
    async batchOperation(operation, items, onProgress = null) {
        const results = [];
        const total = items.length;
        
        for (let i = 0; i < items.length; i++) {
            try {
                const result = await operation(items[i]);
                results.push({ success: true, data: result, item: items[i] });
            } catch (error) {
                results.push({ success: false, error: error.message, item: items[i] });
            }
            
            if (onProgress) {
                onProgress((i + 1) / total * 100, i + 1, total);
            }
        }
        
        return results;
    }

    /**
     * Download file
     */
    async downloadFile(filename, type = 'output') {
        try {
            const url = type === 'merge' ? this.getMergeFileUrl(filename) : this.getFileUrl(filename);
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Failed to download file: ${response.statusText}`);
            }
            
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            window.URL.revokeObjectURL(downloadUrl);
            
            return true;
        } catch (error) {
            console.error('Download error:', error);
            throw error;
        }
    }

    /**
     * Show network status message
     */
    showNetworkStatus(message, type) {
        if (window.flashManager) {
            window.flashManager.show(message, type);
        }
    }

    /**
     * Get server info
     */
    async getServerInfo() {
        try {
            return await this.request('/info');
        } catch (error) {
            return {
                version: 'Unknown',
                status: 'Error',
                uptime: 0
            };
        }
    }

    /**
     * Validate file before upload
     */
    validateFile(file) {
        const allowedTypes = [
            'image/jpeg',
            'image/jpg', 
            'image/png',
            'video/mp4',
            'video/avi'
        ];
        
        const maxSize = 16 * 1024 * 1024; // 16MB
        
        if (!allowedTypes.includes(file.type)) {
            throw new Error(`Tipo de arquivo não suportado: ${file.type}`);
        }
        
        if (file.size > maxSize) {
            throw new Error(`Arquivo muito grande: ${(file.size / 1024 / 1024).toFixed(2)}MB (máximo: 16MB)`);
        }
        
        return true;
    }

    /**
     * Validate multiple files
     */
    validateFiles(files) {
        const errors = [];
        
        for (let i = 0; i < files.length; i++) {
            try {
                this.validateFile(files[i]);
            } catch (error) {
                errors.push(`${files[i].name}: ${error.message}`);
            }
        }
        
        if (errors.length > 0) {
            throw new Error(errors.join('\n'));
        }
        
        return true;
    }
}

// Export for use in other modules
window.ApiManager = ApiManager;