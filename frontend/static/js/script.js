// URL base do backend
const API_URL = "https://reposture-backend.onrender.com";

// Função para pré-visualizar os arquivos selecionados
function previewFiles() {
    const fileInput = document.getElementById('files');
    const previewContainer = document.getElementById('preview-container');
    const filePreview = document.getElementById('file-preview');
    
    // Limpa a área de pré-visualização
    filePreview.innerHTML = '';
    
    // Verifica se há arquivos selecionados
    if (fileInput.files.length > 0) {
        previewContainer.style.display = 'block';
        
        // Cria um elemento para cada arquivo
        for (let i = 0; i < fileInput.files.length; i++) {
            const file = fileInput.files[i];
            const fileItem = document.createElement('div');
            fileItem.className = 'gallery-item';
            fileItem.dataset.index = i;
            
            // Cria um elemento para exibir o arquivo
            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.alt = file.name;
                fileItem.appendChild(img);
            } else if (file.type.startsWith('video/')) {
                const video = document.createElement('video');
                video.src = URL.createObjectURL(file);
                video.controls = false;
                fileItem.appendChild(video);
            }
            
            // Adiciona o nome do arquivo
            const overlay = document.createElement('div');
            overlay.className = 'overlay';
            overlay.textContent = file.name;
            fileItem.appendChild(overlay);
            
            // Adiciona botão de remoção
            const removeBtn = document.createElement('button');
            removeBtn.className = 'btn btn-sm btn-danger position-absolute top-0 end-0 m-1';
            removeBtn.innerHTML = '&times;';
            removeBtn.onclick = function(e) {
                e.preventDefault();
                removeFile(i);
            };
            fileItem.appendChild(removeBtn);
            
            filePreview.appendChild(fileItem);
        }
    } else {
        previewContainer.style.display = 'none';
    }
}

// Função para remover um arquivo da seleção
function removeFile(index) {
    const fileInput = document.getElementById('files');
    const dt = new DataTransfer();
    
    // Cria uma nova lista de arquivos sem o arquivo removido
    for (let i = 0; i < fileInput.files.length; i++) {
        if (i !== index) {
            dt.items.add(fileInput.files[i]);
        }
    }
    
    // Atualiza o input de arquivos
    fileInput.files = dt.files;
    
    // Atualiza a pré-visualização
    previewFiles();
}

// Função para formatar o tempo em minutos e segundos
function formatarTempo(segundos) {
    if (segundos === undefined || segundos === null) return "calculando...";
    
    if (segundos < 60) {
        return segundos + ' segundos';
    } else if (segundos < 3600) {
        const minutos = Math.floor(segundos / 60);
        const segs = segundos % 60;
        return minutos + ' minuto' + (minutos > 1 ? 's' : '') + ' e ' + segs + ' segundo' + (segs > 1 ? 's' : '');
    } else {
        const horas = Math.floor(segundos / 3600);
        const minutos = Math.floor((segundos % 3600) / 60);
        return horas + ' hora' + (horas > 1 ? 's' : '') + ' e ' + minutos + ' minuto' + (minutos > 1 ? 's' : '');
    }
}

// Função para verificar o status do processamento
function checkStatus() {
    fetch(`${API_URL}/status`)
        .then(response => response.json())
        .then(data => {
            const statusContainer = document.getElementById('status-container');
            const uploadButton = document.getElementById('btn-upload');
            
            if (data.ativo) {
                statusContainer.style.display = 'block';
                uploadButton.disabled = true;
                
                if (data.cancelando) {
                    document.getElementById('status-message').textContent = 'Cancelando processamento...';
                } else {
                    // Atualiza as informações de progresso
                    if (data.arquivo_atual && data.total_arquivos) {
                        document.getElementById('current-file').textContent = data.arquivo_atual;
                        document.getElementById('total-files').textContent = data.total_arquivos;
                        document.getElementById('progress-bar').style.width = data.progresso + '%';
                        
                        // Atualiza o tempo restante
                        if (data.tempo_restante !== undefined) {
                            document.getElementById('remaining-time').textContent = formatarTempo(data.tempo_restante);
                        }
                    }
                }
                
                // Continua verificando o status
                setTimeout(checkStatus, 1000);
            } else {
                statusContainer.style.display = 'none';
                uploadButton.disabled = false;
                
                // Recarrega os arquivos processados
                loadProcessedFiles();
            }
        })
        .catch(error => console.error('Erro ao verificar status:', error));
}

// Função para carregar arquivos processados
function loadProcessedFiles() {
    fetch(`${API_URL}/processed_files`)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('processed-files-container');
            
            if (data.processed_files.length > 0 || data.error_files.length > 0) {
                let html = '';
                
                // Arquivos processados com sucesso
                if (data.processed_files.length > 0) {
                    html += '<h6 class="mb-3">Arquivos processados com sucesso:</h6>';
                    html += '<div class="gallery">';
                    
                    data.processed_files.forEach(file => {
                        const fileUrl = `${API_URL}/output_file/${file}`;
                        const isImage = file.toLowerCase().endsWith('.jpg') || 
                                       file.toLowerCase().endsWith('.jpeg') || 
                                       file.toLowerCase().endsWith('.png');
                        
                        html += `<div class="gallery-item">`;
                        
                        if (isImage) {
                            html += `<a href="javascript:void(0)" class="image-link" data-src="${fileUrl}">`;
                            html += `<img src="${fileUrl}" alt="${file}">`;
                            html += `</a>`;
                        } else {
                            html += `<a href="${fileUrl}" target="_blank">`;
                            html += `<video><source src="${fileUrl}" type="video/mp4">Seu navegador não suporta vídeos.</video>`;
                            html += `</a>`;
                        }
                        
                        html += `<div class="overlay">${file}</div>`;
                        html += `</div>`;
                    });
                    
                    html += '</div>';
                }
                
                // Arquivos com erro
                if (data.error_files.length > 0) {
                    html += '<h6 class="mb-3 mt-4 text-danger">Arquivos com erro de processamento:</h6>';
                    html += '<div class="gallery">';
                    
                    data.error_files.forEach(file => {
                        const fileUrl = `${API_URL}/output_file/${file}`;
                        const isImage = file.toLowerCase().endsWith('.jpg') || 
                                       file.toLowerCase().endsWith('.jpeg') || 
                                       file.toLowerCase().endsWith('.png');
                        
                        html += `<div class="gallery-item">`;
                        
                        if (isImage) {
                            html += `<a href="javascript:void(0)" class="image-link" data-src="${fileUrl}">`;
                            html += `<img src="${fileUrl}" alt="${file}">`;
                            html += `<div class="error-badge">Erro: Landmarks não detectados</div>`;
                            html += `</a>`;
                        } else {
                            html += `<a href="${fileUrl}" target="_blank">`;
                            html += `<video><source src="${fileUrl}" type="video/mp4">Seu navegador não suporta vídeos.</video>`;
                            html += `<div class="error-badge">Erro: Landmarks não detectados</div>`;
                            html += `</a>`;
                        }
                        
                        html += `<div class="overlay">${file}</div>`;
                        html += `</div>`;
                    });
                    
                    html += '</div>';
                }
                
                container.innerHTML = html;
                
                // Adiciona evento de clique para as imagens
                document.querySelectorAll('.image-link').forEach(function(link) {
                    link.addEventListener('click', function(e) {
                        e.preventDefault();
                        const imageSrc = this.getAttribute('data-src');
                        document.getElementById('modalImage').src = imageSrc;
                        const imageModal = new bootstrap.Modal(document.getElementById('imageModal'));
                        imageModal.show();
                    });
                });
            } else {
                container.innerHTML = '<p class="text-center">Nenhum arquivo processado ainda.</p>';
            }
        })
        .catch(error => {
            console.error('Erro ao carregar arquivos processados:', error);
            document.getElementById('processed-files-container').innerHTML = 
                '<p class="text-center text-danger">Erro ao carregar arquivos processados.</p>';
        });
}

// Função para mostrar mensagem flash
function showFlashMessage(message, category) {
    const flashContainer = document.getElementById('flash-messages');
    const alertClass = category === 'error' ? 'danger' : category;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${alertClass} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    flashContainer.appendChild(alertDiv);
    
    // Auto-remove após 5 segundos
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 5000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Verifica o status ao carregar a página
    checkStatus();
    
    // Carrega arquivos processados
    loadProcessedFiles();
    
    // Form de upload
    document.getElementById('upload-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('files');
        const apenasTarja = document.getElementById('apenas-tarja');
        if (fileInput.files.length === 0) {
            showFlashMessage('Selecione pelo menos um arquivo para processamento.', 'warning');
            return;
        }
        
        const formData = new FormData();
        for (let i = 0; i < fileInput.files.length; i++) {
            formData.append('files', fileInput.files[i]);
        }
        formData.append('apenas_tarja', apenasTarja.checked ? '1' : '0');
        document.getElementById('btn-upload').disabled = true;
        showFlashMessage('Enviando arquivos para processamento...', 'info');
        fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            fileInput.value = '';
            showFlashMessage(data.message || 'Erro ao enviar arquivos.', data.success ? 'success' : 'error');
            document.getElementById('btn-upload').disabled = false;
        })
        .catch(() => {
            showFlashMessage('Erro ao enviar arquivos para processamento.', 'error');
            document.getElementById('btn-upload').disabled = false;
        });
    });
    
    // Botão de cancelar processamento
    document.getElementById('btn-cancelar').addEventListener('click', function() {
        fetch(`${API_URL}/cancelar`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showFlashMessage('Cancelando processamento...', 'warning');
            } else {
                showFlashMessage('Erro ao cancelar processamento.', 'error');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showFlashMessage('Erro ao cancelar processamento.', 'error');
        });
    });
    
    // Botão de limpar temporários
    document.getElementById('btn-limpar').addEventListener('click', function() {
        fetch(`${API_URL}/limpar`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showFlashMessage('Arquivos temporários limpos com sucesso!', 'success');
                loadProcessedFiles();
            } else {
                showFlashMessage('Erro ao limpar arquivos temporários.', 'error');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            showFlashMessage('Erro ao limpar arquivos temporários.', 'error');
        });
    });
    
    // Botão de abrir pasta
    document.getElementById('btn-abrir-pasta').addEventListener('click', function() {
        fetch(`${API_URL}/abrir-pasta`)
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    showFlashMessage('Não foi possível abrir a pasta de output.', 'error');
                }
            })
            .catch(error => {
                console.error('Erro ao abrir pasta:', error);
                showFlashMessage('Erro ao abrir pasta de output.', 'error');
            });
    });
});