// Funcionalidades para o feed de notícias e monitoramento
document.addEventListener('DOMContentLoaded', function() {
    // Verificar se estamos na página de feed de notícias
    const isNewsFeedPage = window.location.pathname.includes('/feed-noticias');
    
    if (isNewsFeedPage) {
        // Elementos do feed de notícias
        const newsContainer = document.getElementById('newsContainer');
        const newsFilter = document.getElementById('newsFilter');
        const newsSearch = document.getElementById('newsSearch');
        const newsSearchBtn = document.getElementById('newsSearchBtn');
        const loadMoreBtn = document.getElementById('loadMoreBtn');
        
        // Estado do feed
        let currentFilter = 'all';
        let currentPage = 1;
        const itemsPerPage = 10;
        let hasMoreItems = true;
        
        // Carregar feed inicial
        loadNewsFeed();
        
        // Filtrar notícias por estado
        if (newsFilter) {
            newsFilter.addEventListener('change', function() {
                currentFilter = this.value;
                currentPage = 1;
                hasMoreItems = true;
                
                // Limpar feed atual
                newsContainer.innerHTML = '';
                
                // Mostrar indicador de carregamento
                showLoadingIndicator();
                
                // Carregar feed filtrado
                loadNewsFeed();
            });
        }
        
        // Buscar notícias
        if (newsSearchBtn) {
            newsSearchBtn.addEventListener('click', searchNews);
        }
        
        if (newsSearch) {
            newsSearch.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchNews();
                }
            });
        }
        
        // Carregar mais notícias
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', function() {
                currentPage++;
                loadNewsFeed();
            });
        }
        
        // Função para carregar o feed de notícias
        function loadNewsFeed() {
            // Construir URL da API
            let apiUrl = `/api/news/feed?page=${currentPage}&limit=${itemsPerPage}`;
            
            if (currentFilter !== 'all') {
                apiUrl += `&estado=${currentFilter}`;
            }
            
            // Fazer requisição à API
            fetch(apiUrl)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro ao carregar feed de notícias');
                    }
                    return response.json();
                })
                .then(data => {
                    // Remover indicador de carregamento
                    removeLoadingIndicator();
                    
                    // Verificar se há mais itens para carregar
                    if (data.news.length < itemsPerPage) {
                        hasMoreItems = false;
                        if (loadMoreBtn) {
                            loadMoreBtn.style.display = 'none';
                        }
                    } else {
                        if (loadMoreBtn) {
                            loadMoreBtn.style.display = 'block';
                        }
                    }
                    
                    // Renderizar notícias
                    renderNewsFeed(data.news);
                    
                    // Mostrar mensagem se não houver notícias
                    if (data.news.length === 0 && currentPage === 1) {
                        showNoNewsMessage();
                    }
                })
                .catch(error => {
                    // Remover indicador de carregamento
                    removeLoadingIndicator();
                    
                    // Mostrar mensagem de erro
                    showErrorMessage('Não foi possível carregar o feed de notícias. Por favor, tente novamente mais tarde.');
                    console.error('Erro:', error);
                });
        }
        
        // Função para buscar notícias
        function searchNews() {
            if (!newsSearch) return;
            
            const searchTerm = newsSearch.value.trim();
            if (searchTerm === '') return;
            
            // Limpar feed atual
            newsContainer.innerHTML = '';
            
            // Mostrar indicador de carregamento
            showLoadingIndicator();
            
            // Fazer requisição à API
            fetch(`/api/news/search?query=${encodeURIComponent(searchTerm)}&limit=20`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro ao buscar notícias');
                    }
                    return response.json();
                })
                .then(data => {
                    // Remover indicador de carregamento
                    removeLoadingIndicator();
                    
                    // Esconder botão de carregar mais
                    if (loadMoreBtn) {
                        loadMoreBtn.style.display = 'none';
                    }
                    
                    // Renderizar resultados
                    renderNewsFeed(data.results);
                    
                    // Mostrar mensagem se não houver resultados
                    if (data.results.length === 0) {
                        showNoResultsMessage(searchTerm);
                    }
                })
                .catch(error => {
                    // Remover indicador de carregamento
                    removeLoadingIndicator();
                    
                    // Mostrar mensagem de erro
                    showErrorMessage('Não foi possível realizar a busca. Por favor, tente novamente mais tarde.');
                    console.error('Erro:', error);
                });
        }
        
        // Função para renderizar o feed de notícias
        function renderNewsFeed(news) {
            news.forEach(item => {
                const newsCard = createNewsCard(item);
                newsContainer.appendChild(newsCard);
            });
        }
        
        // Função para criar um card de notícia
        function createNewsCard(item) {
            const card = document.createElement('div');
            card.classList.add('news-card');
            
            // Determinar ícone com base na fonte
            let sourceIcon = 'fa-newspaper';
            if (item.source.toLowerCase().includes('twitter') || item.source.toLowerCase().includes('x')) {
                sourceIcon = 'fa-twitter';
            } else if (item.source.toLowerCase().includes('site')) {
                sourceIcon = 'fa-globe';
            }
            
            // Formatar data
            const date = new Date(item.date);
            const formattedDate = date.toLocaleDateString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
            
            // Construir HTML do card
            card.innerHTML = `
                <div class="news-header">
                    <div class="news-source">
                        <i class="fas ${sourceIcon} me-2"></i>${item.source}
                    </div>
                    <div class="news-date">${formattedDate}</div>
                </div>
                <div class="news-content">
                    <h5>${item.title}</h5>
                    <p>${item.content}</p>
                    ${item.image ? `<img src="${item.image}" alt="${item.title}" class="img-fluid mt-2 rounded">` : ''}
                </div>
                <div class="news-footer">
                    <div class="news-tags">
                        ${item.tags ? item.tags.map(tag => `<span class="badge bg-light text-dark me-1">${tag}</span>`).join('') : ''}
                    </div>
                    ${item.url ? `<a href="${item.url}" target="_blank" class="btn btn-sm btn-outline-primary">Ver Original</a>` : ''}
                </div>
            `;
            
            return card;
        }
        
        // Função para mostrar indicador de carregamento
        function showLoadingIndicator() {
            const loadingIndicator = document.createElement('div');
            loadingIndicator.classList.add('loading-indicator', 'text-center', 'my-4');
            loadingIndicator.innerHTML = `
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-2">Carregando notícias...</p>
            `;
            
            newsContainer.appendChild(loadingIndicator);
        }
        
        // Função para remover indicador de carregamento
        function removeLoadingIndicator() {
            const loadingIndicator = document.querySelector('.loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
        }
        
        // Função para mostrar mensagem de nenhuma notícia
        function showNoNewsMessage() {
            const message = document.createElement('div');
            message.classList.add('alert', 'alert-info', 'text-center', 'my-4');
            message.innerHTML = `
                <i class="fas fa-info-circle me-2"></i>
                Não há notícias disponíveis no momento.
            `;
            
            newsContainer.appendChild(message);
        }
        
        // Função para mostrar mensagem de nenhum resultado
        function showNoResultsMessage(searchTerm) {
            const message = document.createElement('div');
            message.classList.add('alert', 'alert-info', 'text-center', 'my-4');
            message.innerHTML = `
                <i class="fas fa-search me-2"></i>
                Nenhum resultado encontrado para "${searchTerm}".
            `;
            
            newsContainer.appendChild(message);
        }
        
        // Função para mostrar mensagem de erro
        function showErrorMessage(errorText) {
            const message = document.createElement('div');
            message.classList.add('alert', 'alert-danger', 'text-center', 'my-4');
            message.innerHTML = `
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${errorText}
            `;
            
            newsContainer.appendChild(message);
        }
    }
    
    // Adicionar widget de notificações em todas as páginas
    setupNotificationsWidget();
    
    // Função para configurar o widget de notificações
    function setupNotificationsWidget() {
        // Verificar se o widget já existe
        if (document.getElementById('notificationsWidget')) {
            return;
        }
        
        // Criar widget
        const widget = document.createElement('div');
        widget.id = 'notificationsWidget';
        widget.classList.add('notifications-widget');
        
        // Adicionar botão de notificações
        const button = document.createElement('div');
        button.classList.add('notifications-button');
        button.innerHTML = `
            <i class="fas fa-bell"></i>
            <span class="notifications-badge" id="notificationsBadge">0</span>
        `;
        
        // Adicionar popup de notificações
        const popup = document.createElement('div');
        popup.classList.add('notifications-popup');
        popup.innerHTML = `
            <div class="notifications-header">
                <h5><i class="fas fa-bell me-2"></i>Notificações</h5>
                <button class="btn-close" id="notificationsClose"></button>
            </div>
            <div class="notifications-list" id="notificationsList">
                <div class="text-center py-4 text-muted">
                    <i class="fas fa-check-circle fa-2x mb-2"></i>
                    <p>Você está em dia com todas as notificações.</p>
                </div>
            </div>
        `;
        
        // Adicionar ao widget
        widget.appendChild(button);
        widget.appendChild(popup);
        
        // Adicionar ao body
        document.body.appendChild(widget);
        
        // Adicionar estilos
        const style = document.createElement('style');
        style.textContent = `
            .notifications-widget {
                position: fixed;
                bottom: 20px;
                left: 20px;
                z-index: 1000;
            }
            
            .notifications-button {
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
                position: relative;
            }
            
            .notifications-button:hover {
                transform: scale(1.1);
            }
            
            .notifications-badge {
                position: absolute;
                top: -5px;
                right: -5px;
                background-color: #e74c3c;
                color: white;
                border-radius: 50%;
                width: 22px;
                height: 22px;
                font-size: 0.8rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
            }
            
            .notifications-popup {
                position: absolute;
                bottom: 80px;
                left: 0;
                width: 350px;
                height: 400px;
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 5px 25px rgba(0, 0, 0, 0.15);
                display: none;
                flex-direction: column;
                overflow: hidden;
            }
            
            .notifications-popup.active {
                display: flex;
            }
            
            .notifications-header {
                background-color: #3498db;
                color: white;
                padding: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .notifications-header h5 {
                margin: 0;
                font-weight: 600;
            }
            
            .notifications-list {
                flex: 1;
                padding: 0;
                overflow-y: auto;
            }
            
            .notification-item {
                padding: 15px;
                border-bottom: 1px solid #eee;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            
            .notification-item:hover {
                background-color: #f8f9fa;
            }
            
            .notification-item.unread {
                background-color: #f0f7ff;
            }
            
            .notification-title {
                font-weight: 600;
                margin-bottom: 5px;
            }
            
            .notification-content {
                color: #666;
                font-size: 0.9rem;
                margin-bottom: 5px;
            }
            
            .notification-time {
                color: #999;
                font-size: 0.8rem;
                text-align: right;
            }
        `;
        
        document.head.appendChild(style);
        
        // Adicionar eventos
        button.addEventListener('click', function() {
            popup.classList.toggle('active');
        });
        
        const closeButton = document.getElementById('notificationsClose');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                popup.classList.remove('active');
            });
        }
        
        // Carregar notificações
        loadNotifications();
        
        // Verificar novas notificações a cada 5 minutos
        setInterval(loadNotifications, 5 * 60 * 1000);
    }
    
    // Função para carregar notificações
    function loadNotifications() {
        // Simular notificações para demonstração
        // Em um ambiente real, isso seria uma chamada à API
        setTimeout(() => {
            const notifications = [
                {
                    id: 1,
                    title: 'Nova convenção coletiva',
                    content: 'Uma nova convenção coletiva do SINDPD-SP foi encontrada.',
                    time: '10 minutos atrás',
                    unread: true
                },
                {
                    id: 2,
                    title: 'Atualização de dados',
                    content: 'Os dados do sindicato SINDPD-RJ foram atualizados automaticamente.',
                    time: '1 hora atrás',
                    unread: true
                },
                {
                    id: 3,
                    title: 'Processamento concluído',
                    content: 'O processamento do arquivo "convenções_2025.xlsx" foi concluído com sucesso.',
                    time: 'Ontem',
                    unread: false
                }
            ];
            
            updateNotifications(notifications);
        }, 1000);
    }
    
    // Função para atualizar notificações
    function updateNotifications(notifications) {
        const badge = document.getElementById('notificationsBadge');
        const list = document.getElementById('notificationsList');
        
        if (!badge || !list) return;
        
        // Contar notificações não lidas
        const unreadCount = notifications.filter(n => n.unread).length;
        
        // Atualizar badge
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'flex' : 'none';
        
        // Limpar lista
        list.innerHTML = '';
        
        // Adicionar notificações à lista
        if (notifications.length === 0) {
            list.innerHTML = `
                <div class="text-center py-4 text-muted">
                    <i class="fas fa-check-circle fa-2x mb-2"></i>
                    <p>Você está em dia com todas as notificações.</p>
                </div>
            `;
        } else {
            notifications.forEach(notification => {
                const item = document.createElement('div');
                item.classList.add('notification-item');
                if (notification.unread) {
                    item.classList.add('unread');
                }
                
                item.innerHTML = `
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-content">${notification.content}</div>
                    <div class="notification-time">${notification.time}</div>
                `;
                
                // Marcar como lida ao clicar
                item.addEventListener('click', function() {
                    item.classList.remove('unread');
                    notification.unread = false;
                    
                    // Atualizar badge
                    const newUnreadCount = notifications.filter(n => n.unread).length;
                    badge.textContent = newUnreadCount;
                    badge.style.display = newUnreadCount > 0 ? 'flex' : 'none';
                });
                
                list.appendChild(item);
            });
        }
    }
});
