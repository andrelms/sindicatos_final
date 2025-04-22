// Script para controle de tema claro/escuro

// Função para alternar entre temas claro e escuro
function toggleTheme() {
    const body = document.body;
    const currentTheme = body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Adicionar classe de transição
    body.classList.add('theme-transition');
    
    // Atualizar o tema no body
    body.setAttribute('data-theme', newTheme);
    
    // Atualizar o ícone do botão com animação
    const themeToggle = document.querySelector('.theme-toggle i');
    if (themeToggle) {
        themeToggle.style.transform = 'rotate(180deg)';
        setTimeout(() => {
            themeToggle.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
            themeToggle.style.transform = 'rotate(0)';
        }, 200);
    }
    
    // Salvar preferência no localStorage
    localStorage.setItem('theme', newTheme);
    
    // Remover classe de transição após a animação
    setTimeout(() => {
        body.classList.remove('theme-transition');
    }, 300);
}

// Função para definir o tema como claro
function aplicarTemaClaro() {
    // Verifica se o corpo do documento está disponível
    if (document.body) {
        // Remove a classe dark-theme se existir
        document.body.classList.remove('dark-theme');
        // Define o atributo data-theme como light
        document.body.setAttribute('data-theme', 'light');
        
        // Atualiza o ícone para lua (indicando que pode mudar para escuro)
        const themeToggle = document.querySelector('.theme-toggle i');
        if (themeToggle) {
            themeToggle.className = 'fas fa-moon';
        }
        
        // Salva a preferência no localStorage
        localStorage.setItem('theme', 'light');
        
        console.log('Tema claro aplicado com sucesso!');
    }
}

// Carregar tema salvo ao iniciar (ou aplicar o tema claro forçadamente)
document.addEventListener('DOMContentLoaded', function() {
    // Executa a função para aplicar o tema claro imediatamente
    aplicarTemaClaro();
    
    // Também executa após um curto intervalo para garantir que todos os elementos foram carregados
    setTimeout(aplicarTemaClaro, 100);
}); 