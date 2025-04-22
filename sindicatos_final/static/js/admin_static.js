// Admin estático para o Sistema de Automação de Sindicatos

document.addEventListener('DOMContentLoaded', function() {
    // Elementos da página de administração
    const filesTableBody = document.getElementById('filesTableBody');
    const deleteAllFiles = document.getElementById('deleteAllFiles');
    const clearDatabase = document.getElementById('clearDatabase');
    const clearCaches = document.getElementById('clearCaches');
    const configForm = document.getElementById('configForm');
    const logContent = document.getElementById('logContent');
    const logType = document.getElementById('logType');
    const refreshLogs = document.getElementById('refreshLogs');
    const clearLogs = document.getElementById('clearLogs');
    const confirmAction = document.getElementById('confirmAction');
    
    // Carregar arquivos na tabela
    function loadFiles() {
        if (filesTableBody) {
            filesTableBody.innerHTML = '';
            
            mockFiles.forEach(file => {
                const row = document.createElement('tr');
                
                const fileIcon = file.type === 'pdf' ? 
                    '<i class="fas fa-file-pdf me-1"></i>PDF' : 
                    '<i class="fas fa-file-excel me-1"></i>Excel';
                
                row.innerHTML = `
                    <td>${file.name}</td>
                    <td>${fileIcon}</td>
                    <td>${file.size}</td>
                    <td>${file.uploadDate}</td>
                    <td>
                        <button class="btn btn-sm btn-info view-file" data-id="${file.id}">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-danger delete-file" data-id="${file.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                
                filesTableBody.appendChild(row);
            });
            
            // Adicionar event listeners para botões de ação
            const viewButtons = document.querySelectorAll('.view-file');
            const deleteButtons = document.querySelectorAll('.delete-file');
            
            viewButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const fileId = this.getAttribute('data-id');
                    alert(`Visualizando arquivo ID: ${fileId}`);
                });
            });
            
            deleteButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const fileId = this.getAttribute('data-id');
                    showConfirmationModal(
                        'Excluir Arquivo', 
                        `Tem certeza que deseja excluir este arquivo? Esta ação não pode ser desfeita.`,
                        () => deleteFile(fileId)
                    );
                });
            });
        }
    }
    
    // Carregar logs
    function loadLogs(type = 'app') {
        if (logContent) {
            logContent.textContent = mockLogs[type] || 'Nenhum log disponível para este tipo.';
        }
    }
    
    // Mostrar modal de confirmação
    function showConfirmationModal(title, message, callback) {
        const modal = new bootstrap.Modal(document.getElementById('confirmationModal'));
        const modalTitle = document.getElementById('confirmationModalTitle');
        const modalBody = document.getElementById('confirmationModalBody');
        
        modalTitle.textContent = title;
        modalBody.textContent = message;
        
        // Configurar callback para o botão de confirmação
        confirmAction.onclick = function() {
            callback();
            modal.hide();
        };
        
        modal.show();
    }
    
    // Funções de ação
    function deleteFile(fileId) {
        // Simular exclusão de arquivo
        setTimeout(() => {
            alert(`Arquivo ID: ${fileId} excluído com sucesso!`);
            // Recarregar lista de arquivos
            loadFiles();
        }, 500);
    }
    
    function deleteAllFilesAction() {
        // Simular exclusão de todos os arquivos
        setTimeout(() => {
            alert('Todos os arquivos foram excluídos com sucesso!');
            // Limpar lista de arquivos
            if (filesTableBody) {
                filesTableBody.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center">Nenhum arquivo encontrado.</td>
                    </tr>
                `;
            }
        }, 1000);
    }
    
    function clearDatabaseAction() {
        // Simular limpeza do banco de dados
        setTimeout(() => {
            alert('Base de dados excluída com sucesso!');
        }, 1500);
    }
    
    function clearCachesAction() {
        // Simular limpeza de caches
        setTimeout(() => {
            alert('Caches limpos com sucesso!');
        }, 1000);
    }
    
    // Event listeners
    if (deleteAllFiles) {
        deleteAllFiles.addEventListener('click', function() {
            showConfirmationModal(
                'Excluir Todos os Arquivos', 
                'Tem certeza que deseja excluir todos os arquivos? Esta ação não pode ser desfeita.',
                deleteAllFilesAction
            );
        });
    }
    
    if (clearDatabase) {
        clearDatabase.addEventListener('click', function() {
            showConfirmationModal(
                'Excluir Base de Dados', 
                'ATENÇÃO! Você está prestes a excluir TODA a base de dados. Esta ação é irreversível e removerá todos os dados, incluindo arquivos, resultados processados e caches. Tem certeza que deseja continuar?',
                clearDatabaseAction
            );
        });
    }
    
    if (clearCaches) {
        clearCaches.addEventListener('click', function() {
            showConfirmationModal(
                'Limpar Caches', 
                'Tem certeza que deseja limpar todos os caches do sistema? Esta ação não afetará os dados principais.',
                clearCachesAction
            );
        });
    }
    
    if (configForm) {
        configForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Configurações salvas com sucesso!');
        });
    }
    
    if (logType) {
        logType.addEventListener('change', function() {
            loadLogs(this.value);
        });
    }
    
    if (refreshLogs) {
        refreshLogs.addEventListener('click', function() {
            loadLogs(logType ? logType.value : 'app');
        });
    }
    
    if (clearLogs) {
        clearLogs.addEventListener('click', function() {
            showConfirmationModal(
                'Limpar Logs', 
                'Tem certeza que deseja limpar todos os logs? Esta ação não pode ser desfeita.',
                () => {
                    if (logContent) {
                        logContent.textContent = 'Logs limpos.';
                    }
                }
            );
        });
    }
    
    // Inicializar página
    if (window.location.pathname.includes('admin.html')) {
        // Carregar arquivos
        loadFiles();
        
        // Carregar logs
        loadLogs('app');
    }
});
