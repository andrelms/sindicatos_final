document.addEventListener('DOMContentLoaded', function() {
    // Referências aos elementos da UI
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('fileInput');
    const fileTable = document.getElementById('fileTable');
    const fileTableBody = document.getElementById('fileTableBody');
    const uploadProgress = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const uploadStatus = document.getElementById('uploadStatus');
    const themeToggle = document.getElementById('theme-toggle');
    
    // Inicializar o tema com base na preferência do usuário salva
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', currentTheme);
    updateThemeIcon(currentTheme);
    
    // Event listeners para o sistema de upload de arquivos
    if (dropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });
        
        dropArea.addEventListener('drop', handleDrop, false);
        
        if (fileInput) {
            fileInput.addEventListener('change', handleFiles, false);
        }
    }
    
    // Event listener para o botão de alternar tema
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            updateThemeIcon(newTheme);
        });
    }
    
    // Carregar a lista de arquivos se estivermos na página de arquivos
    if (fileTable) {
        loadFiles();
    }
    
    // Funções para o sistema de upload de arquivos
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        dropArea.classList.add('highlight');
    }
    
    function unhighlight() {
        dropArea.classList.remove('highlight');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
    
    function handleFiles(e) {
        let files;
        if (e.target && e.target.files) {
            files = e.target.files;
        } else {
            files = e;
        }
        
        uploadFiles(files);
    }
    
    function uploadFiles(files) {
        // Mostrar a barra de progresso
        uploadProgress.classList.remove('d-none');
        progressBar.style.width = '0%';
        progressBar.textContent = '0%';
        uploadStatus.textContent = 'Iniciando upload...';
        
        const formData = new FormData();
        
        // Adicionar todos os arquivos ao FormData
        for (let i = 0; i < files.length; i++) {
            formData.append('files[]', files[i]);
        }
        
        // Realizar o upload via fetch com acompanhamento de progresso
        const xhr = new XMLHttpRequest();
        
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percentComplete + '%';
                progressBar.textContent = percentComplete + '%';
                uploadStatus.textContent = `Enviando... ${formatBytes(e.loaded)} de ${formatBytes(e.total)}`;
            }
        });
        
        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                if (response.success) {
                    progressBar.classList.remove('bg-primary');
                    progressBar.classList.add('bg-success');
                    uploadStatus.textContent = 'Upload concluído com sucesso!';
                    
                    // Adicionar notificação de sucesso
                    showNotification('Upload concluído com sucesso!', 'success');
                    
                    // Atualizar a lista de arquivos
                    loadFiles();
                    
                    // Esconder a barra de progresso após 3 segundos
                    setTimeout(function() {
                        uploadProgress.classList.add('d-none');
                    }, 3000);
                } else {
                    handleUploadError(response.message || 'Erro ao fazer upload dos arquivos.');
                }
            } else {
                handleUploadError('Erro ao fazer upload: ' + xhr.statusText);
            }
        });
        
        xhr.addEventListener('error', function() {
            handleUploadError('Erro na conexão ao fazer upload.');
        });
        
        xhr.addEventListener('abort', function() {
            uploadStatus.textContent = 'Upload cancelado.';
        });
        
        xhr.open('POST', '/upload_files');
        xhr.send(formData);
    }
    
    function handleUploadError(message) {
        progressBar.classList.remove('bg-primary');
        progressBar.classList.add('bg-danger');
        uploadStatus.textContent = message;
        showNotification(message, 'error');
    }
    
    // Funções utilitárias
    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        const options = { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return date.toLocaleDateString('pt-BR', options);
    }
    
    function loadFiles() {
        if (!fileTableBody) return;
        
        fetch('/api/files')
            .then(response => response.json())
            .then(data => {
                fileTableBody.innerHTML = '';
                
                if (data.files && data.files.length > 0) {
                    data.files.forEach(file => {
                        // Determinar o tipo de arquivo
                        let fileTypeIcon = 'fa-file';
                        let fileType = 'Arquivo';
                        let processBtn = '';
                        
                        if (file.filename.toLowerCase().endsWith('.pdf')) {
                            fileTypeIcon = 'fa-file-pdf';
                            fileType = 'PDF';
                            processBtn = `<button class="btn btn-sm btn-outline-primary process-pdf" data-id="${file.id}" data-filename="${file.filename}">
                                <i class="fas fa-cogs"></i> Processar
                            </button>`;
                        } else if (file.filename.toLowerCase().endsWith('.xlsx') || file.filename.toLowerCase().endsWith('.xls')) {
                            fileTypeIcon = 'fa-file-excel';
                            fileType = 'Excel';
                            processBtn = `<button class="btn btn-sm btn-outline-primary process-excel" data-id="${file.id}" data-filename="${file.filename}">
                                <i class="fas fa-cogs"></i> Processar
                            </button>`;
                        } else if (file.filename.toLowerCase().endsWith('.csv')) {
                            fileTypeIcon = 'fa-file-csv';
                            fileType = 'CSV';
                        } else if (file.filename.toLowerCase().endsWith('.doc') || file.filename.toLowerCase().endsWith('.docx')) {
                            fileTypeIcon = 'fa-file-word';
                            fileType = 'Word';
                        }
                        
                        // Status do processamento
                        let statusBadge = '';
                        if (file.status === 'processed') {
                            statusBadge = '<span class="badge bg-success">Processado</span>';
                        } else if (file.status === 'processing') {
                            statusBadge = '<span class="badge bg-warning">Processando</span>';
                        } else if (file.status === 'error') {
                            statusBadge = '<span class="badge bg-danger">Erro</span>';
                        } else {
                            statusBadge = '<span class="badge bg-secondary">Pendente</span>';
                        }
                        
                        // Botões de ação
                        const viewBtn = `<a href="/view_file/${file.id}" class="btn btn-sm btn-outline-info">
                            <i class="fas fa-eye"></i> Visualizar
                        </a>`;
                        
                        const downloadBtn = `<a href="/download_file/${file.id}" class="btn btn-sm btn-outline-success">
                            <i class="fas fa-download"></i> Download
                        </a>`;
                        
                        const deleteBtn = `<button class="btn btn-sm btn-outline-danger delete-file" data-id="${file.id}" data-filename="${file.filename}">
                            <i class="fas fa-trash"></i> Excluir
                        </button>`;
                        
                        // Adicionar linha na tabela
                        const row = document.createElement('tr');
                        row.classList.add('file-row');
                        row.setAttribute('data-id', file.id);
                        
                        if (file.status === 'processing') {
                            row.classList.add('processing');
                        }
                        
                        row.innerHTML = `
                            <td class="text-center"><i class="fas ${fileTypeIcon} fa-2x text-primary"></i></td>
                            <td>
                                <div class="fw-bold">${file.filename}</div>
                                <div class="small text-muted">${fileType} - ${formatBytes(file.size)}</div>
                            </td>
                            <td class="text-center">${statusBadge}</td>
                            <td>${formatDate(file.upload_date)}</td>
                            <td>
                                <div class="d-flex gap-1">
                                    ${viewBtn}
                                    ${downloadBtn}
                                    ${file.status !== 'processing' ? processBtn : ''}
                                    ${file.status !== 'processing' ? deleteBtn : ''}
                                </div>
                            </td>
                        `;
                        
                        fileTableBody.appendChild(row);
                    });
                    
                    // Event listeners para os botões de ação
                    document.querySelectorAll('.delete-file').forEach(button => {
                        button.addEventListener('click', handleDeleteFile);
                    });
                    
                    document.querySelectorAll('.process-pdf').forEach(button => {
                        button.addEventListener('click', handleProcessPDF);
                    });
                    
                    document.querySelectorAll('.process-excel').forEach(button => {
                        button.addEventListener('click', handleProcessExcel);
                    });
                } else {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td colspan="5" class="text-center py-4">
                            <i class="fas fa-folder-open fa-3x mb-3 text-muted"></i>
                            <p class="mb-0">Nenhum arquivo encontrado. Faça upload de arquivos para começar.</p>
                        </td>
                    `;
                    fileTableBody.appendChild(row);
                }
            })
            .catch(error => {
                console.error('Erro ao carregar arquivos:', error);
                showNotification('Erro ao carregar a lista de arquivos.', 'error');
            });
    }
    
    function handleDeleteFile() {
        const fileId = this.getAttribute('data-id');
        const filename = this.getAttribute('data-filename');
        
        if (confirm(`Tem certeza que deseja excluir o arquivo "${filename}"?`)) {
            fetch(`/api/files/${fileId}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification(`Arquivo "${filename}" excluído com sucesso.`, 'success');
                    loadFiles();
                } else {
                    showNotification(data.message || 'Erro ao excluir o arquivo.', 'error');
                }
            })
            .catch(error => {
                console.error('Erro ao excluir arquivo:', error);
                showNotification('Erro ao excluir o arquivo.', 'error');
            });
        }
    }
    
    function handleProcessPDF() {
        const fileId = this.getAttribute('data-id');
        const filename = this.getAttribute('data-filename');
        
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
        
        // Atualizar aparência da linha
        const row = document.querySelector(`.file-row[data-id="${fileId}"]`);
        row.classList.add('processing');
        
        // Atualizar o badge de status
        const statusCell = row.querySelector('td:nth-child(3)');
        statusCell.innerHTML = '<span class="badge bg-warning">Processando</span>';
        
        // Remover botões de ação temporariamente
        const actionsCell = row.querySelector('td:last-child');
        const actionsHtml = actionsCell.innerHTML;
        actionsCell.innerHTML = '<div class="d-flex gap-1"><button class="btn btn-sm btn-outline-secondary" disabled><i class="fas fa-spinner fa-spin"></i> Processando...</button></div>';
        
        fetch(`/api/process_pdf/${fileId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`Arquivo "${filename}" processado com sucesso.`, 'success');
            } else {
                showNotification(data.message || 'Erro ao processar o arquivo.', 'error');
            }
            loadFiles();
        })
        .catch(error => {
            console.error('Erro ao processar PDF:', error);
            showNotification('Erro ao processar o arquivo.', 'error');
            loadFiles();
        });
    }
    
    function handleProcessExcel() {
        const fileId = this.getAttribute('data-id');
        const filename = this.getAttribute('data-filename');
        
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
        
        // Atualizar aparência da linha
        const row = document.querySelector(`.file-row[data-id="${fileId}"]`);
        row.classList.add('processing');
        
        // Atualizar o badge de status
        const statusCell = row.querySelector('td:nth-child(3)');
        statusCell.innerHTML = '<span class="badge bg-warning">Processando</span>';
        
        // Remover botões de ação temporariamente
        const actionsCell = row.querySelector('td:last-child');
        const actionsHtml = actionsCell.innerHTML;
        actionsCell.innerHTML = '<div class="d-flex gap-1"><button class="btn btn-sm btn-outline-secondary" disabled><i class="fas fa-spinner fa-spin"></i> Processando...</button></div>';
        
        fetch(`/api/process_excel/${fileId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(`Arquivo "${filename}" processado com sucesso.`, 'success');
            } else {
                showNotification(data.message || 'Erro ao processar o arquivo.', 'error');
            }
            loadFiles();
        })
        .catch(error => {
            console.error('Erro ao processar Excel:', error);
            showNotification('Erro ao processar o arquivo.', 'error');
            loadFiles();
        });
    }

    // Função para mostrar notificações
    function showNotification(message, type = 'info') {
        // Verifica se o container de notificações existe, senão cria
        let notificationContainer = document.querySelector('.notification-container');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.className = 'notification-container';
            document.body.appendChild(notificationContainer);
        }
        
        // Criar elemento de notificação
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        // Ícone baseado no tipo
        let icon = 'info-circle';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'exclamation-circle';
        if (type === 'warning') icon = 'exclamation-triangle';
        
        notification.innerHTML = `
            <div class="notification-icon">
                <i class="fas fa-${icon}"></i>
            </div>
            <div class="notification-message">${message}</div>
        `;
        
        // Adicionar ao container
        notificationContainer.appendChild(notification);
        
        // Exibir com animação
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Remover após 5 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 5000);
    }
    
    // Função para atualizar o ícone do botão tema
    function updateThemeIcon(theme) {
        if (!themeToggle) return;
        
        const iconElement = themeToggle.querySelector('i');
        if (iconElement) {
            if (theme === 'dark') {
                iconElement.classList.remove('fa-moon');
                iconElement.classList.add('fa-sun');
            } else {
                iconElement.classList.remove('fa-sun');
                iconElement.classList.add('fa-moon');
            }
        }
    }
}); 