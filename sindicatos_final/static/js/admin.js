// Funcionalidades para a página de administração
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se estamos na página de administração
    const isAdminPage = window.location.pathname.includes('/admin');
    
    if (isAdminPage) {
        // Elementos da página
        const filesTableBody = document.getElementById('filesTableBody');
        const noFilesMessage = document.getElementById('noFilesMessage');
        const deleteAllFilesBtn = document.getElementById('deleteAllFiles');
        const clearDatabaseBtn = document.getElementById('clearDatabase');
        const clearCachesBtn = document.getElementById('clearCaches');
        const configForm = document.getElementById('configForm');
        const logTypeSelect = document.getElementById('logType');
        const logContent = document.getElementById('logContent');
        const refreshLogsBtn = document.getElementById('refreshLogs');
        const clearLogsBtn = document.getElementById('clearLogs');
        
        // Modal de confirmação
        const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
        const confirmationModalTitle = document.getElementById('confirmationModalTitle');
        const confirmationModalBody = document.getElementById('confirmationModalBody');
        const confirmActionBtn = document.getElementById('confirmAction');
        
        // Carregar lista de arquivos
        loadFiles();
        
        // Carregar logs iniciais
        loadLogs();
        
        // Event listeners
        if (deleteAllFilesBtn) {
            deleteAllFilesBtn.addEventListener('click', function() {
                showConfirmation(
                    'Excluir Todos os Arquivos',
                    'Tem certeza que deseja excluir todos os arquivos? Esta ação não pode ser desfeita.',
                    deleteAllFiles
                );
            });
        }
        
        if (clearDatabaseBtn) {
            clearDatabaseBtn.addEventListener('click', function() {
                showConfirmation(
                    'Excluir Base de Dados',
                    'ATENÇÃO! Você está prestes a excluir TODA a base de dados, incluindo arquivos, resultados processados e caches. Esta ação é irreversível. Tem certeza que deseja continuar?',
                    clearDatabase
                );
            });
        }
        
        if (clearCachesBtn) {
            clearCachesBtn.addEventListener('click', function() {
                showConfirmation(
                    'Limpar Caches',
                    'Tem certeza que deseja limpar todos os caches do sistema? Isso afetará o histórico de consultas e o feed de notícias.',
                    clearCaches
                );
            });
        }
        
        if (configForm) {
            configForm.addEventListener('submit', function(e) {
                e.preventDefault();
                saveConfig();
            });
        }
        
        if (logTypeSelect) {
            logTypeSelect.addEventListener('change', loadLogs);
        }
        
        if (refreshLogsBtn) {
            refreshLogsBtn.addEventListener('click', loadLogs);
        }
        
        if (clearLogsBtn) {
            clearLogsBtn.addEventListener('click', function() {
                showConfirmation(
                    'Limpar Logs',
                    'Tem certeza que deseja limpar os logs do sistema?',
                    clearLogs
                );
            });
        }
        
        // Função para mostrar confirmação
        function showConfirmation(title, message, callback) {
            confirmationModalTitle.textContent = title;
            confirmationModalBody.textContent = message;
            
            // Remover event listeners anteriores
            const newConfirmBtn = confirmActionBtn.cloneNode(true);
            confirmActionBtn.parentNode.replaceChild(newConfirmBtn, confirmActionBtn);
            
            // Adicionar novo event listener
            newConfirmBtn.addEventListener('click', function() {
                confirmationModal.hide();
                callback();
            });
            
            confirmationModal.show();
        }
        
        // Função para carregar arquivos
        function loadFiles() {
            if (!filesTableBody) return;
            
            filesTableBody.innerHTML = '<tr><td colspan="5" class="text-center">Carregando arquivos...</td></tr>';
            
            fetch('/api/files')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro ao carregar arquivos');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.files && data.files.length > 0) {
                        filesTableBody.innerHTML = '';
                        
                        data.files.forEach(file => {
                            const row = document.createElement('tr');
                            
                            // Formatar tamanho
                            const sizeInKB = Math.round(file.size / 1024);
                            const sizeFormatted = sizeInKB > 1024 
                                ? `${(sizeInKB / 1024).toFixed(2)} MB` 
                                : `${sizeInKB} KB`;
                            
                            // Formatar data
                            const date = new Date(file.upload_time);
                            const dateFormatted = date.toLocaleDateString('pt-BR', {
                                day: '2-digit',
                                month: '2-digit',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            });
                            
                            // Ícone baseado no tipo
                            let typeIcon = 'fa-file';
                            let typeText = file.type;
                            
                            if (file.type === 'xlsx' || file.type === 'xls') {
                                typeIcon = 'fa-file-excel';
                                typeText = 'Excel';
                            } else if (file.type === 'pdf') {
                                typeIcon = 'fa-file-pdf';
                                typeText = 'PDF';
                            }
                            
                            row.innerHTML = `
                                <td>${file.name}</td>
                                <td><i class="fas ${typeIcon} me-1"></i>${typeText}</td>
                                <td>${sizeFormatted}</td>
                                <td>${dateFormatted}</td>
                                <td>
                                    <button class="btn btn-sm btn-danger delete-file" data-filename="${file.name}">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            `;
                            
                            filesTableBody.appendChild(row);
                        });
                        
                        // Adicionar event listeners para botões de exclusão
                        document.querySelectorAll('.delete-file').forEach(button => {
                            button.addEventListener('click', function() {
                                const filename = this.getAttribute('data-filename');
                                deleteFile(filename);
                            });
                        });
                    } else {
                        filesTableBody.innerHTML = '<tr><td colspan="5" class="text-center">Nenhum arquivo encontrado</td></tr>';
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    filesTableBody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Erro ao carregar arquivos</td></tr>';
                });
        }
        
        // Função para excluir arquivo
        function deleteFile(filename) {
            showConfirmation(
                'Excluir Arquivo',
                `Tem certeza que deseja excluir o arquivo "${filename}"?`,
                function() {
                    fetch(`/api/files/${filename}`, {
                        method: 'DELETE'
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Erro ao excluir arquivo');
                        }
                        return response.json();
                    })
                    .then(data => {
                        showToast('Sucesso', `Arquivo "${filename}" excluído com sucesso`, 'success');
                        loadFiles();
                    })
                    .catch(error => {
                        console.error('Erro:', error);
                        showToast('Erro', `Erro ao excluir arquivo "${filename}"`, 'danger');
                    });
                }
            );
        }
        
        // Função para excluir todos os arquivos
        function deleteAllFiles() {
            fetch('/api/admin/delete-all-files', {
                method: 'POST'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao excluir arquivos');
                }
                return response.json();
            })
            .then(data => {
                showToast('Sucesso', 'Todos os arquivos foram excluídos com sucesso', 'success');
                loadFiles();
            })
            .catch(error => {
                console.error('Erro:', error);
                showToast('Erro', 'Erro ao excluir arquivos', 'danger');
            });
        }
        
        // Função para limpar base de dados
        function clearDatabase() {
            fetch('/api/admin/clear-database', {
                method: 'POST'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao limpar base de dados');
                }
                return response.json();
            })
            .then(data => {
                showToast('Sucesso', 'Base de dados limpa com sucesso', 'success');
                loadFiles();
            })
            .catch(error => {
                console.error('Erro:', error);
                showToast('Erro', 'Erro ao limpar base de dados', 'danger');
            });
        }
        
        // Função para limpar caches
        function clearCaches() {
            fetch('/api/admin/clear-caches', {
                method: 'POST'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao limpar caches');
                }
                return response.json();
            })
            .then(data => {
                showToast('Sucesso', 'Caches limpos com sucesso', 'success');
            })
            .catch(error => {
                console.error('Erro:', error);
                showToast('Erro', 'Erro ao limpar caches', 'danger');
            });
        }
        
        // Função para salvar configurações
        function saveConfig() {
            const geminiModel = document.getElementById('geminiModel').value;
            const maxUploadSize = document.getElementById('maxUploadSize').value;
            const autoProcessing = document.getElementById('autoProcessing').checked;
            
            const config = {
                gemini_model: geminiModel,
                max_upload_size: maxUploadSize,
                auto_processing: autoProcessing
            };
            
            fetch('/api/admin/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao salvar configurações');
                }
                return response.json();
            })
            .then(data => {
                showToast('Sucesso', 'Configurações salvas com sucesso', 'success');
            })
            .catch(error => {
                console.error('Erro:', error);
                showToast('Erro', 'Erro ao salvar configurações', 'danger');
            });
        }
        
        // Função para carregar logs
        function loadLogs() {
            if (!logContent || !logTypeSelect) return;
            
            const logType = logTypeSelect.value;
            logContent.textContent = 'Carregando logs...';
            
            fetch(`/api/admin/logs/${logType}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro ao carregar logs');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.logs) {
                        logContent.textContent = data.logs;
                    } else {
                        logContent.textContent = 'Nenhum log encontrado';
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    logContent.textContent = 'Erro ao carregar logs';
                });
        }
        
        // Função para limpar logs
        function clearLogs() {
            const logType = logTypeSelect.value;
            
            fetch(`/api/admin/logs/${logType}/clear`, {
                method: 'POST'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao limpar logs');
                }
                return response.json();
            })
            .then(data => {
                showToast('Sucesso', 'Logs limpos com sucesso', 'success');
                loadLogs();
            })
            .catch(error => {
                console.error('Erro:', error);
                showToast('Erro', 'Erro ao limpar logs', 'danger');
            });
        }
        
        // Função para mostrar toast
        function showToast(title, message, type) {
            // Verificar se o container de toasts existe
            let toastContainer = document.querySelector('.toast-container');
            
            if (!toastContainer) {
                toastContainer = document.createElement('div');
                toastContainer.classList.add('toast-container', 'position-fixed', 'bottom-0', 'end-0', 'p-3');
                document.body.appendChild(toastContainer);
            }
            
            // Criar toast
            const toastId = `toast-${Date.now()}`;
            const toast = document.createElement('div');
            toast.classList.add('toast', 'show');
            toast.setAttribute('id', toastId);
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            
            toast.innerHTML = `
                <div class="toast-header bg-${type} text-white">
                    <strong class="me-auto">${title}</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            `;
            
            toastContainer.appendChild(toast);
            
            // Inicializar toast
            const bsToast = new bootstrap.Toast(toast, {
                autohide: true,
                delay: 5000
            });
            
            bsToast.show();
            
            // Remover após fechar
            toast.addEventListener('hidden.bs.toast', function() {
                toast.remove();
            });
        }

        // Função para processar arquivo Excel
        async function processarExcel(arquivo) {
            try {
                const formData = new FormData();
                formData.append('file', arquivo);
                formData.append('processar', 'true');
        
                // Mostrar feedback visual
                showProcessingFeedback(arquivo.name);
        
                const response = await fetch('/api/arquivos/upload', {
                    method: 'POST',
                    body: formData
                });
        
                const result = await response.json();
                
                if (result.success) {
                    updateProcessingStatus(arquivo.name, 'success', 'Arquivo processado com sucesso!');
                    // Atualizar tabela de dados
                    await loadProcessedData();
                } else {
                    updateProcessingStatus(arquivo.name, 'error', result.message || 'Erro ao processar arquivo');
                }
            } catch (error) {
                updateProcessingStatus(arquivo.name, 'error', 'Erro ao processar arquivo: ' + error.message);
            }
        }
        
        // Função para mostrar feedback do processamento
        function showProcessingFeedback(fileName) {
            const feedbackContainer = document.getElementById('processingFeedback') || createFeedbackContainer();
            
            const feedbackItem = document.createElement('div');
            feedbackItem.className = 'processing-item mb-3';
            feedbackItem.id = `processing-${fileName.replace(/\s+/g, '-')}`;
            feedbackItem.innerHTML = `
                <div class="d-flex align-items-center">
                    <div class="flex-grow-1">
                        <div class="d-flex justify-content-between">
                            <strong>${fileName}</strong>
                            <span class="status-text">Processando...</span>
                        </div>
                        <div class="progress mt-2" style="height: 5px;">
                            <div class="progress-bar progress-bar-striped progress-bar-animated" 
                                 role="progressbar" style="width: 100%"></div>
                        </div>
                    </div>
                </div>
            `;
            
            feedbackContainer.appendChild(feedbackItem);
        }
        
        // Função para atualizar status do processamento
        function updateProcessingStatus(fileName, status, message) {
            const itemId = `processing-${fileName.replace(/\s+/g, '-')}`;
            const item = document.getElementById(itemId);
            
            if (item) {
                const statusText = item.querySelector('.status-text');
                const progressBar = item.querySelector('.progress-bar');
                
                if (status === 'success') {
                    statusText.textContent = message;
                    statusText.className = 'status-text text-success';
                    progressBar.className = 'progress-bar bg-success';
                } else {
                    statusText.textContent = message;
                    statusText.className = 'status-text text-danger';
                    progressBar.className = 'progress-bar bg-danger';
                }
                
                // Remover após 5 segundos se sucesso
                if (status === 'success') {
                    setTimeout(() => {
                        item.remove();
                    }, 5000);
                }
            }
        }
        
        // Função para criar container de feedback
        function createFeedbackContainer() {
            const container = document.createElement('div');
            container.id = 'processingFeedback';
            container.className = 'position-fixed bottom-0 end-0 p-3';
            container.style.zIndex = '1050';
            document.body.appendChild(container);
            return container;
        }
        
        // Função para carregar dados processados
        async function loadProcessedData() {
            try {
                const response = await fetch('/api/resultados');
                const data = await response.json();
                
                // Atualizar tabela ou visualização de dados
                updateDataView(data);
            } catch (error) {
                console.error('Erro ao carregar dados:', error);
            }
        }
        
        // Função para atualizar visualização de dados
        function updateDataView(data) {
            const dataContainer = document.getElementById('dataContainer');
            if (!dataContainer) return;
            
            if (data.length === 0) {
                dataContainer.innerHTML = '<p class="text-center text-muted">Nenhum dado processado ainda.</p>';
                return;
            }
            
            // Criar tabela de dados
            const table = document.createElement('table');
            table.className = 'table table-striped table-hover';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Estado</th>
                        <th>Cargo</th>
                        <th>Carga Horária</th>
                        <th>Piso Salarial</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(item => `
                        <tr>
                            <td>${item.estado}</td>
                            <td>${item.cargo}</td>
                            <td>${item.carga_horaria}</td>
                            <td>R$ ${item.piso_salarial.toFixed(2)}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary" onclick="editarDado(${item.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="excluirDado(${item.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            `;
            
            dataContainer.innerHTML = '';
            dataContainer.appendChild(table);
        }
    }
});

// Gerenciador de Notificações
const NotificationManager = {
    show(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this._getIcon(type)} me-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Trigger reflow para iniciar animação
        notification.offsetHeight;
        notification.classList.add('show');
        
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, duration);
    },
    
    _getIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            error: 'fa-times-circle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }
};

// Função para mostrar estado de processamento
function showProcessingState(element, isProcessing = true) {
    if (isProcessing) {
        element.classList.add('processing');
        if (!element.querySelector('.loading-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay';
            overlay.innerHTML = '<div class="loading-spinner"></div>';
            element.appendChild(overlay);
        }
    } else {
        element.classList.remove('processing');
        const overlay = element.querySelector('.loading-overlay');
        if (overlay) overlay.remove();
    }
}

// Função para processar arquivos
async function processarArquivo(id) {
    const card = document.querySelector(`#arquivo-${id}`);
    if (!card) return;
    
    try {
        showProcessingState(card, true);
        
        const response = await fetch(`/api/arquivos/${id}/processar`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            NotificationManager.show('Arquivo processado com sucesso!', 'success');
            await atualizarListaArquivos();
        } else {
            throw new Error(data.message || 'Erro ao processar arquivo');
        }
    } catch (error) {
        NotificationManager.show(error.message, 'error');
    } finally {
        showProcessingState(card, false);
    }
}

// Função para limpar banco de dados
async function limparBancoDados() {
    if (!confirm('Tem certeza que deseja limpar o banco de dados? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    const container = document.querySelector('.main-content');
    
    try {
        showProcessingState(container, true);
        
        const response = await fetch('/api/admin/clear-database', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ confirmar: true })
        });
        
        const data = await response.json();
        
        if (data.success) {
            NotificationManager.show('Banco de dados limpo com sucesso! Backup criado em: ' + data.backup, 'success');
            await atualizarListaArquivos();
        } else {
            throw new Error(data.message || 'Erro ao limpar banco de dados');
        }
    } catch (error) {
        NotificationManager.show(error.message, 'error');
    } finally {
        showProcessingState(container, false);
    }
}

// Funções de atualização da interface
async function atualizarListaArquivos() {
    const container = document.querySelector('#lista-arquivos');
    if (!container) return;
    
    try {
        showProcessingState(container, true);
        
        const response = await fetch('/api/arquivos');
        const arquivos = await response.json();
        
        container.innerHTML = arquivos.map(arquivo => `
            <div id="arquivo-${arquivo.id}" class="card mb-3 fade-in">
                <div class="card-body">
                    <h5 class="card-title">${arquivo.nome}</h5>
                    <p class="card-text">
                        <span class="badge ${arquivo.processado ? 'bg-success' : 'bg-warning'}">
                            ${arquivo.processado ? 'Processado' : 'Pendente'}
                        </span>
                    </p>
                    <button onclick="processarArquivo(${arquivo.id})" 
                            class="btn btn-primary"
                            ${arquivo.processado ? 'disabled' : ''}>
                        Processar
                    </button>
                </div>
            </div>
        `).join('');
    } catch (error) {
        NotificationManager.show('Erro ao atualizar lista de arquivos', 'error');
    } finally {
        showProcessingState(container, false);
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar lista de arquivos
    atualizarListaArquivos();
    
    // Observar mudanças de tema
    document.addEventListener('themeChanged', () => {
        // Atualizar elementos que precisam de ajuste com o novo tema
        document.querySelectorAll('.notification').forEach(notification => {
            notification.style.backgroundColor = 'var(--card-bg)';
            notification.style.borderColor = 'var(--border-color)';
        });
    });
});
