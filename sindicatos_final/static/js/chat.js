// Funcionalidades principais do chat inteligente
document.addEventListener('DOMContentLoaded', function() {
    // Elementos do chat
    const chatButton = document.getElementById('chatButton');
    const chatPopup = document.getElementById('chatPopup');
    const chatClose = document.getElementById('chatClose');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatMessages = document.getElementById('chatMessages');
    
    // Histórico de contexto para manter a conversa coerente
    let chatContext = {};
    
    // Abrir/fechar o chat
    chatButton.addEventListener('click', function() {
        chatPopup.classList.toggle('active');
        if (chatPopup.classList.contains('active')) {
            chatInput.focus();
        }
    });
    
    chatClose.addEventListener('click', function() {
        chatPopup.classList.remove('active');
    });
    
    // Enviar mensagem quando pressionar Enter
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Enviar mensagem quando clicar no botão
    chatSend.addEventListener('click', sendMessage);
    
    // Função para enviar mensagem
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message === '') return;
        
        // Adicionar mensagem do usuário ao chat
        addMessage(message, 'user');
        
        // Limpar input
        chatInput.value = '';
        
        // Mostrar indicador de digitação
        addTypingIndicator();
        
        // Enviar para a API e obter resposta
        processQuery(message);
    }
    
    // Adicionar mensagem ao chat
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        
        const messageContent = document.createElement('div');
        messageContent.classList.add('message-content');
        messageContent.textContent = message;
        
        messageElement.appendChild(messageContent);
        chatMessages.appendChild(messageElement);
        
        // Rolar para a última mensagem
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Adicionar indicador de digitação
    function addTypingIndicator() {
        const typingElement = document.createElement('div');
        typingElement.classList.add('message', 'bot', 'typing-indicator');
        
        const typingContent = document.createElement('div');
        typingContent.classList.add('message-content');
        typingContent.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
        
        typingElement.appendChild(typingContent);
        chatMessages.appendChild(typingElement);
        
        // Rolar para a última mensagem
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Remover indicador de digitação
    function removeTypingIndicator() {
        const typingIndicator = document.querySelector('.typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Processar consulta com a API
    function processQuery(query) {
        fetch('/api/chat/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                context: chatContext
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na comunicação com o servidor');
            }
            return response.json();
        })
        .then(data => {
            // Remover indicador de digitação
            removeTypingIndicator();
            
            // Adicionar resposta do bot
            addMessage(data.response, 'bot');
            
            // Atualizar contexto
            if (data.context) {
                chatContext = data.context;
            }
            
            // Se houver sugestões, mostrar
            if (data.suggestions && data.suggestions.length > 0) {
                setTimeout(() => {
                    addSuggestions(data.suggestions);
                }, 500);
            }
        })
        .catch(error => {
            // Remover indicador de digitação
            removeTypingIndicator();
            
            // Mostrar mensagem de erro
            addMessage('Desculpe, ocorreu um erro ao processar sua consulta. Por favor, tente novamente.', 'bot');
            console.error('Erro:', error);
        });
    }
    
    // Adicionar sugestões de perguntas
    function addSuggestions(suggestions) {
        const suggestionsElement = document.createElement('div');
        suggestionsElement.classList.add('message', 'bot');
        
        const suggestionsContent = document.createElement('div');
        suggestionsContent.classList.add('message-content', 'suggestions');
        
        const suggestionsText = document.createElement('p');
        suggestionsText.textContent = 'Você também pode perguntar:';
        suggestionsContent.appendChild(suggestionsText);
        
        const suggestionsList = document.createElement('div');
        suggestionsList.classList.add('suggestions-list');
        
        suggestions.forEach(suggestion => {
            const suggestionButton = document.createElement('button');
            suggestionButton.classList.add('suggestion-button');
            suggestionButton.textContent = suggestion;
            
            suggestionButton.addEventListener('click', function() {
                chatInput.value = suggestion;
                sendMessage();
            });
            
            suggestionsList.appendChild(suggestionButton);
        });
        
        suggestionsContent.appendChild(suggestionsList);
        suggestionsElement.appendChild(suggestionsContent);
        chatMessages.appendChild(suggestionsElement);
        
        // Rolar para a última mensagem
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Inicializar com uma mensagem de boas-vindas
    // (Já adicionada no HTML)
});

// Adicionar estilos CSS específicos para o indicador de digitação e sugestões
const style = document.createElement('style');
style.textContent = `
    .typing-indicator .message-content {
        padding: 10px 20px;
    }
    
    .typing-indicator .dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #888;
        margin-right: 4px;
        animation: typing 1.4s infinite both;
    }
    
    .typing-indicator .dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-indicator .dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    @keyframes typing {
        0% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0); }
    }
    
    .suggestions-list {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 8px;
    }
    
    .suggestion-button {
        background-color: rgba(52, 152, 219, 0.1);
        border: 1px solid rgba(52, 152, 219, 0.3);
        border-radius: 16px;
        padding: 6px 12px;
        font-size: 0.9rem;
        cursor: pointer;
        transition: background-color 0.2s;
    }
    
    .suggestion-button:hover {
        background-color: rgba(52, 152, 219, 0.2);
    }
`;

document.head.appendChild(style);
