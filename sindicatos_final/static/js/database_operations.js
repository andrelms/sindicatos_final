// Funcionalidades para operações de banco de dados
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se o widget de chat está presente
    const chatWidget = document.getElementById('chatWidget');
    
    if (chatWidget) {
        // Garantir que o widget de chat esteja presente em todas as páginas
        setupChatWidget();
    }
    
    // Função para configurar o widget de chat
    function setupChatWidget() {
        const chatButton = document.getElementById('chatButton');
        const chatPopup = document.getElementById('chatPopup');
        const chatClose = document.getElementById('chatClose');
        
        // Verificar se os elementos existem
        if (!chatButton || !chatPopup || !chatClose) return;
        
        // Abrir/fechar o chat
        chatButton.addEventListener('click', function() {
            chatPopup.classList.toggle('active');
        });
        
        chatClose.addEventListener('click', function() {
            chatPopup.classList.remove('active');
        });
        
        // Adicionar estilos específicos para garantir que o widget esteja presente em todas as páginas
        const style = document.createElement('style');
        style.textContent = `
            .chat-widget {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
            }
            
            .chat-button {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background-color: #3498db;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.5rem;
                cursor: pointer;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s ease;
            }
            
            .chat-button:hover {
                transform: scale(1.1);
            }
            
            .chat-popup {
                position: absolute;
                bottom: 80px;
                right: 0;
                width: 350px;
                height: 500px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 5px 25px rgba(0, 0, 0, 0.15);
                display: none;
                flex-direction: column;
                overflow: hidden;
            }
            
            .chat-popup.active {
                display: flex;
            }
            
            .chat-header {
                background-color: #3498db;
                color: white;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .chat-header h5 {
                margin: 0;
                font-weight: 600;
            }
            
            .chat-messages {
                flex: 1;
                padding: 15px;
                overflow-y: auto;
            }
            
            .chat-input {
                display: flex;
                border-top: 1px solid #eee;
                padding: 10px;
            }
            
            .chat-input input {
                flex: 1;
                border: 1px solid #ddd;
                border-radius: 20px;
                padding: 8px 15px;
                outline: none;
            }
            
            .chat-input button {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                margin-left: 10px;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            
            .chat-input button:hover {
                background-color: #2980b9;
            }
            
            .message {
                margin-bottom: 15px;
                display: flex;
                flex-direction: column;
            }
            
            .message.user {
                align-items: flex-end;
            }
            
            .message.bot {
                align-items: flex-start;
            }
            
            .message-content {
                padding: 10px 15px;
                border-radius: 18px;
                max-width: 80%;
                word-wrap: break-word;
            }
            
            .message.user .message-content {
                background-color: #3498db;
                color: white;
                border-bottom-right-radius: 5px;
            }
            
            .message.bot .message-content {
                background-color: #f1f1f1;
                color: #333;
                border-bottom-left-radius: 5px;
            }
        `;
        
        document.head.appendChild(style);
    }
});
