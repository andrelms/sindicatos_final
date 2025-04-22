// Chat estático para o Sistema de Automação de Sindicatos

document.addEventListener('DOMContentLoaded', function() {
    // Elementos do chat
    const chatButton = document.getElementById('chatButton');
    const chatPopup = document.getElementById('chatPopup');
    const chatClose = document.getElementById('chatClose');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');

    // Abrir/fechar chat
    chatButton.addEventListener('click', function() {
        chatPopup.style.display = chatPopup.style.display === 'flex' ? 'none' : 'flex';
    });

    chatClose.addEventListener('click', function() {
        chatPopup.style.display = 'none';
    });

    // Enviar mensagem
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            // Adicionar mensagem do usuário
            addMessage(message, 'user');
            
            // Limpar input
            chatInput.value = '';
            
            // Simular resposta do bot após um pequeno delay
            setTimeout(function() {
                const botResponse = getBotResponse(message);
                addMessage(botResponse, 'bot');
            }, 1000);
        }
    }

    // Adicionar mensagem ao chat
    function addMessage(message, sender) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.textContent = message;
        
        messageElement.appendChild(messageContent);
        chatMessages.appendChild(messageElement);
        
        // Scroll para a última mensagem
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Obter resposta simulada do bot
    function getBotResponse(message) {
        message = message.toLowerCase();
        
        if (message.includes('piso salarial') || message.includes('salário')) {
            return 'De acordo com a convenção coletiva de 2025, o piso salarial para Analistas Júnior em São Paulo é de R$ 2.450,00, para Analistas Pleno é de R$ 3.200,00 e para Analistas Sênior é de R$ 4.500,00.';
        }
        else if (message.includes('benefício') || message.includes('vale refeição')) {
            return 'Os benefícios previstos na convenção coletiva incluem vale refeição de R$ 30,00 por dia, auxílio home office de R$ 150,00 por mês, plano de saúde e vale transporte.';
        }
        else if (message.includes('férias') || message.includes('licença')) {
            return 'A convenção coletiva prevê 30 dias de férias com abono, licença maternidade de 180 dias e licença paternidade de 20 dias.';
        }
        else if (message.includes('jornada') || message.includes('horas')) {
            return 'A jornada de trabalho prevista é de 40 horas semanais, com hora extra remunerada em 75% nos dias úteis e 100% nos domingos e feriados.';
        }
        else if (message.includes('sindicato') || message.includes('sindpd')) {
            return 'Temos informações sobre diversos sindicatos, incluindo SINDPD-SP, SINDPD-RJ, SINDPD-MG, SINDPD-RS e outros. Qual sindicato específico você gostaria de saber mais?';
        }
        else if (message.includes('convenção') || message.includes('acordo coletivo')) {
            return 'As convenções coletivas são atualizadas anualmente. A mais recente é de 2025, com vigência a partir de janeiro. Posso fornecer detalhes específicos sobre cláusulas se você precisar.';
        }
        else if (message.includes('obrigado') || message.includes('valeu') || message.includes('agradeço')) {
            return 'Por nada! Estou aqui para ajudar. Se tiver mais alguma dúvida, é só perguntar.';
        }
        else if (message.includes('olá') || message.includes('oi') || message.includes('bom dia') || message.includes('boa tarde') || message.includes('boa noite')) {
            return 'Olá! Como posso ajudar você hoje com informações sobre convenções coletivas e sindicatos?';
        }
        else {
            return 'Não tenho informações específicas sobre isso. Posso ajudar com dúvidas sobre pisos salariais, benefícios, jornada de trabalho, férias e licenças previstas nas convenções coletivas. Como posso ajudar?';
        }
    }

    // Event listeners para enviar mensagem
    chatSend.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
});
