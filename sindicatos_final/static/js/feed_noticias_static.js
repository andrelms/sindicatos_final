// Feed de notícias estático para o Sistema de Automação de Sindicatos

document.addEventListener('DOMContentLoaded', function() {
    // Elementos do feed de notícias
    const newsContainer = document.getElementById('newsContainer');
    const newsFilter = document.getElementById('newsFilter');
    const newsSearch = document.getElementById('newsSearch');
    const newsSearchBtn = document.getElementById('newsSearchBtn');
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    
    // Carregar notícias
    function loadNews(filter = 'all', search = '') {
        // Limpar container
        if (newsContainer) {
            newsContainer.innerHTML = '';
            
            // Filtrar notícias
            let filteredNews = mockNews;
            
            if (filter !== 'all') {
                filteredNews = filteredNews.filter(news => news.state === filter);
            }
            
            if (search) {
                const searchLower = search.toLowerCase();
                filteredNews = filteredNews.filter(news => 
                    news.title.toLowerCase().includes(searchLower) || 
                    news.content.toLowerCase().includes(searchLower)
                );
            }
            
            // Exibir mensagem se não houver notícias
            if (filteredNews.length === 0) {
                newsContainer.innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        Nenhuma notícia encontrada com os filtros selecionados.
                    </div>
                `;
                return;
            }
            
            // Adicionar notícias ao container
            filteredNews.forEach(news => {
                const newsCard = document.createElement('div');
                newsCard.className = 'col-md-6 col-lg-4';
                
                newsCard.innerHTML = `
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">${news.title}</h5>
                            <p class="card-text">${news.content}</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">${news.date}</small>
                                <span class="badge bg-primary">${news.state}</span>
                            </div>
                        </div>
                        <div class="card-footer bg-transparent">
                            <small class="text-muted">Fonte: ${news.source}</small>
                        </div>
                    </div>
                `;
                
                newsContainer.appendChild(newsCard);
            });
        }
    }
    
    // Inicializar feed de notícias na página inicial
    if (window.location.pathname.includes('index.html') || window.location.pathname === '/' || window.location.pathname === '') {
        const homeNewsContainer = document.getElementById('newsContainer');
        if (homeNewsContainer) {
            // Mostrar apenas 3 notícias na página inicial
            homeNewsContainer.innerHTML = '';
            
            for (let i = 0; i < Math.min(3, mockNews.length); i++) {
                const news = mockNews[i];
                const newsCard = document.createElement('div');
                newsCard.className = 'col-md-4';
                
                newsCard.innerHTML = `
                    <div class="card h-100">
                        <div class="card-body">
                            <h5 class="card-title">${news.title}</h5>
                            <p class="card-text">${news.content.substring(0, 100)}...</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <small class="text-muted">${news.date}</small>
                                <span class="badge bg-primary">${news.state}</span>
                            </div>
                        </div>
                        <div class="card-footer bg-transparent">
                            <a href="feed-noticias.html" class="btn btn-sm btn-outline-primary">Ler mais</a>
                        </div>
                    </div>
                `;
                
                homeNewsContainer.appendChild(newsCard);
            }
        }
    }
    
    // Inicializar feed de notícias na página de feed
    if (window.location.pathname.includes('feed-noticias.html')) {
        // Carregar todas as notícias inicialmente
        loadNews();
        
        // Event listeners para filtros
        if (newsFilter) {
            newsFilter.addEventListener('change', function() {
                loadNews(this.value, newsSearch ? newsSearch.value : '');
            });
        }
        
        if (newsSearchBtn) {
            newsSearchBtn.addEventListener('click', function() {
                loadNews(newsFilter ? newsFilter.value : 'all', newsSearch.value);
            });
        }
        
        if (newsSearch) {
            newsSearch.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    loadNews(newsFilter ? newsFilter.value : 'all', this.value);
                }
            });
        }
        
        // Event listener para botão "Carregar Mais"
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', function() {
                // Simular carregamento de mais notícias
                this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Carregando...';
                
                setTimeout(() => {
                    this.innerHTML = '<i class="fas fa-sync-alt me-1"></i>Carregar Mais';
                    
                    // Exibir mensagem de que não há mais notícias
                    const alert = document.createElement('div');
                    alert.className = 'col-12 mt-3';
                    alert.innerHTML = `
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            Não há mais notícias para carregar.
                        </div>
                    `;
                    
                    newsContainer.appendChild(alert);
                    
                    // Desabilitar botão
                    this.disabled = true;
                }, 1500);
            });
        }
    }
});
