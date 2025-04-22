/**
 * Gerenciador de tema para o Sistema de Automação de Sindicatos
 */

// Função para alternar entre temas claro e escuro
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    // Atualizar atributo no body
    body.setAttribute('data-theme', newTheme);
    
    // Atualizar classes para compatibilidade
    if (newTheme === 'dark') {
        body.classList.remove('light-theme');
        body.classList.add('dark-theme');
    } else {
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
    }
    
    // Atualizar ícone do botão de tema
    const themeToggleIcon = document.querySelector('.theme-toggle i');
    if (themeToggleIcon) {
        if (newTheme === 'dark') {
            themeToggleIcon.classList.remove('fa-moon');
            themeToggleIcon.classList.add('fa-sun');
        } else {
            themeToggleIcon.classList.remove('fa-sun');
            themeToggleIcon.classList.add('fa-moon');
        }
    }
    
    // Salvar preferência no localStorage
    localStorage.setItem('theme', newTheme);
    
    // Disparar evento personalizado para outros componentes
    const event = new CustomEvent('themeChanged', { detail: { theme: newTheme } });
    document.dispatchEvent(event);
}

// Carregar tema salvo ou usar o padrão do sistema
function loadSavedTheme() {
    const savedTheme = localStorage.getItem('theme');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Usar tema salvo ou preferência do sistema
    const themeToApply = savedTheme || (prefersDarkScheme ? 'dark' : 'light');
    
    // Aplicar tema
    document.body.setAttribute('data-theme', themeToApply);
    
    // Atualizar classes para compatibilidade
    if (themeToApply === 'dark') {
        document.body.classList.remove('light-theme');
        document.body.classList.add('dark-theme');
    } else {
        document.body.classList.remove('dark-theme');
        document.body.classList.add('light-theme');
    }
    
    // Atualizar ícone do botão de tema
    const themeToggleIcon = document.querySelector('.theme-toggle i');
    if (themeToggleIcon) {
        if (themeToApply === 'dark') {
            themeToggleIcon.classList.remove('fa-moon');
            themeToggleIcon.classList.add('fa-sun');
        } else {
            themeToggleIcon.classList.remove('fa-sun');
            themeToggleIcon.classList.add('fa-moon');
        }
    }
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Carregar tema salvo
    loadSavedTheme();
    
    // Configurar botão de alternar tema
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Configurar transições de abas suaves
    const navLinks = document.querySelectorAll('.nav-link[data-tab]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remover classe active de todos os links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Adicionar classe active ao link clicado
            this.classList.add('active');
            
            // Aplicar transição suave
            const tabPanes = document.querySelectorAll('.tab-pane');
            tabPanes.forEach(pane => {
                pane.classList.add('content-transition');
                pane.style.opacity = '0';
                
                setTimeout(() => {
                    pane.classList.remove('show', 'active');
                }, 300);
            });
            
            // Mostrar a aba correspondente com transição
            const tabId = this.getAttribute('data-tab');
            const tabPane = document.getElementById(tabId);
            
            if (tabPane) {
                setTimeout(() => {
                    tabPane.classList.add('show', 'active');
                    
                    setTimeout(() => {
                        tabPane.style.opacity = '1';
                    }, 50);
                }, 350);
            }
        });
    });
});

// Gerenciar chat RAG
document.addEventListener('DOMContentLoaded', function() {
    const ragChatButton = document.getElementById('rag-chat-button');
    const chatPopup = document.getElementById('chat-popup');
    const closeChat = document.getElementById('close-chat');
    
    if (ragChatButton && chatPopup) {
        ragChatButton.addEventListener('click', function() {
            chatPopup.style.display = chatPopup.style.display === 'flex' ? 'none' : 'flex';
            
            // Adicionar animação ao abrir
            if (chatPopup.style.display === 'flex') {
                chatPopup.style.opacity = '0';
                setTimeout(() => {
                    chatPopup.style.opacity = '1';
                }, 50);
            }
        });
    }
    
    if (closeChat && chatPopup) {
        closeChat.addEventListener('click', function() {
            chatPopup.style.opacity = '0';
            setTimeout(() => {
                chatPopup.style.display = 'none';
            }, 300);
        });
    }
    
    // Simulação de envio de mensagem
    const sendMessage = document.getElementById('send-message');
    const chatInput = document.getElementById('chat-input-field');
    const chatMessages = document.getElementById('chat-messages');
    
    if (sendMessage && chatInput && chatMessages) {
        sendMessage.addEventListener('click', function() {
            if (chatInput.value.trim() === '') return;
            
            // Adicionar mensagem do usuário
            const userMessage = document.createElement('div');
            userMessage.className = 'message user';
            userMessage.innerHTML = `<div class="message-content">${chatInput.value}</div>`;
            chatMessages.appendChild(userMessage);
            
            // Simular resposta do bot após 1 segundo
            setTimeout(() => {
                const botMessage = document.createElement('div');
                botMessage.className = 'message bot';
                botMessage.innerHTML = `<div class="message-content">
                    Esta é uma resposta simulada. Em um ambiente real, o sistema RAG buscaria informações relevantes nos documentos indexados para responder à sua pergunta.
                    <br><br>
                    <small class="text-muted">Fonte: Simulação de demonstração</small>
                </div>`;
                chatMessages.appendChild(botMessage);
                
                // Rolar para o final da conversa
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }, 1000);
            
            // Limpar campo de entrada
            chatInput.value = '';
            
            // Rolar para o final da conversa
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });
        
        // Permitir envio com Enter
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage.click();
            }
        });
    }
});
