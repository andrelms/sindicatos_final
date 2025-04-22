// Mock data para o Sistema de Automação de Sindicatos

// Dados de notícias para o feed
const mockNews = [
    {
        id: 1,
        title: "SINDPD-SP anuncia nova convenção coletiva para 2025",
        content: "O Sindicato dos Trabalhadores em Processamento de Dados de São Paulo (SINDPD-SP) anunciou hoje a nova convenção coletiva para o ano de 2025, com reajuste salarial de 7,5% e novos benefícios.",
        date: "15/03/2025",
        source: "Site Oficial SINDPD-SP",
        state: "SP",
        image: "static/img/news1.jpg",
        url: "#"
    },
    {
        id: 2,
        title: "Sindicato dos Metalúrgicos do ABC fecha acordo com montadoras",
        content: "O Sindicato dos Metalúrgicos do ABC fechou acordo com as principais montadoras da região, garantindo estabilidade no emprego e reajuste acima da inflação para os trabalhadores.",
        date: "10/03/2025",
        source: "Twitter Oficial @MetalurgicosABC",
        state: "SP",
        image: "static/img/news2.jpg",
        url: "#"
    },
    {
        id: 3,
        title: "SINDPD-RJ lança programa de qualificação profissional",
        content: "O Sindicato dos Trabalhadores em Processamento de Dados do Rio de Janeiro (SINDPD-RJ) lançou um programa de qualificação profissional gratuito para seus associados, com foco em novas tecnologias.",
        date: "05/03/2025",
        source: "Site Oficial SINDPD-RJ",
        state: "RJ",
        image: "static/img/news3.jpg",
        url: "#"
    },
    {
        id: 4,
        title: "Sindicato dos Bancários de MG conquista home office permanente",
        content: "O Sindicato dos Bancários de Minas Gerais conseguiu aprovar em convenção coletiva o regime de home office permanente para os trabalhadores do setor, com auxílio mensal de R$ 180,00.",
        date: "28/02/2025",
        source: "Portal de Notícias G1",
        state: "MG",
        image: "static/img/news4.jpg",
        url: "#"
    },
    {
        id: 5,
        title: "SINDPD-RS negocia redução de jornada sem redução salarial",
        content: "O Sindicato dos Trabalhadores em Processamento de Dados do Rio Grande do Sul (SINDPD-RS) está em negociação para redução da jornada de trabalho de 44 para 40 horas semanais sem redução salarial.",
        date: "20/02/2025",
        source: "Twitter Oficial @SINDPDRS",
        state: "RS",
        image: "static/img/news5.jpg",
        url: "#"
    },
    {
        id: 6,
        title: "Sindicato dos Professores da Bahia conquista reajuste de 8,5%",
        content: "O Sindicato dos Professores da Bahia fechou acordo com escolas particulares garantindo reajuste salarial de 8,5% e melhoria nas condições de trabalho para o ensino híbrido.",
        date: "15/02/2025",
        source: "Jornal A Tarde",
        state: "BA",
        image: "static/img/news6.jpg",
        url: "#"
    }
];

// Dados de arquivos para a página de administração
const mockFiles = [
    {
        id: 1,
        name: "convenção_sindpd_sp_2025.pdf",
        type: "pdf",
        size: "2.34 MB",
        uploadDate: "15/03/2025, 10:30",
        path: "#"
    },
    {
        id: 2,
        name: "convenção_sindpd_rj_2025.pdf",
        type: "pdf",
        size: "2.00 MB",
        uploadDate: "20/03/2025, 14:45",
        path: "#"
    },
    {
        id: 3,
        name: "base_sindicatos_2025.xlsx",
        type: "excel",
        size: "1024 KB",
        uploadDate: "01/04/2025, 09:15",
        path: "#"
    },
    {
        id: 4,
        name: "pisos_salariais_ti_2025.xlsx",
        type: "excel",
        size: "768 KB",
        uploadDate: "05/04/2025, 16:20",
        path: "#"
    },
    {
        id: 5,
        name: "benefícios_comparativo_2025.xlsx",
        type: "excel",
        size: "512 KB",
        uploadDate: "10/04/2025, 11:00",
        path: "#"
    }
];

// Dados de logs para a página de administração
const mockLogs = {
    app: "2025-04-19 10:00:12 [INFO] Sistema iniciado\n2025-04-19 10:01:05 [INFO] Usuário admin realizou login\n2025-04-19 10:05:23 [INFO] Arquivo 'convenção_sindpd_sp_2025.pdf' carregado\n2025-04-19 10:10:45 [INFO] Processamento de PDF iniciado\n2025-04-19 10:15:30 [INFO] Extração de dados concluída\n2025-04-19 10:20:15 [INFO] Dados salvos no banco de dados\n2025-04-19 10:25:40 [WARNING] Tentativa de acesso não autorizado à página de administração\n2025-04-19 10:30:22 [INFO] Backup automático iniciado\n2025-04-19 10:35:10 [INFO] Backup concluído com sucesso",
    backend: "2025-04-19 10:00:00 [INFO] Serviço backend iniciado na porta 5000\n2025-04-19 10:01:00 [INFO] Conexão com banco de dados estabelecida\n2025-04-19 10:05:25 [INFO] Requisição POST /api/upload recebida\n2025-04-19 10:05:30 [INFO] Arquivo salvo em /uploads/convenção_sindpd_sp_2025.pdf\n2025-04-19 10:10:50 [INFO] Requisição POST /api/process recebida\n2025-04-19 10:15:35 [INFO] Processamento concluído com sucesso\n2025-04-19 10:20:20 [INFO] Requisição POST /api/save recebida\n2025-04-19 10:20:25 [INFO] Dados salvos com sucesso\n2025-04-19 10:25:45 [WARNING] Requisição não autorizada para /api/admin",
    pdf: "2025-04-19 10:10:45 [INFO] Iniciando processamento do arquivo 'convenção_sindpd_sp_2025.pdf'\n2025-04-19 10:11:00 [INFO] Extraindo texto do PDF\n2025-04-19 10:12:30 [INFO] Texto extraído com sucesso\n2025-04-19 10:12:35 [INFO] Identificando seções do documento\n2025-04-19 10:13:40 [INFO] Seções identificadas: 42\n2025-04-19 10:13:45 [INFO] Enviando texto para análise com Gemini\n2025-04-19 10:14:50 [INFO] Resposta recebida do Gemini\n2025-04-19 10:15:00 [INFO] Estruturando dados extraídos\n2025-04-19 10:15:30 [INFO] Processamento concluído com sucesso",
    twitter: "2025-04-19 09:00:00 [INFO] Serviço de monitoramento do Twitter iniciado\n2025-04-19 09:15:00 [INFO] Buscando tweets dos sindicatos cadastrados\n2025-04-19 09:15:30 [INFO] 18 perfis de sindicatos encontrados na base\n2025-04-19 09:16:00 [INFO] Iniciando coleta de tweets\n2025-04-19 09:20:45 [INFO] 87 tweets coletados\n2025-04-19 09:21:00 [INFO] Filtrando tweets relevantes\n2025-04-19 09:22:30 [INFO] 42 tweets relevantes identificados\n2025-04-19 09:23:00 [INFO] Salvando tweets no banco de dados\n2025-04-19 09:25:15 [INFO] Tweets salvos com sucesso",
    chat: "2025-04-19 11:00:10 [INFO] Sessão de chat iniciada pelo usuário\n2025-04-19 11:00:15 [INFO] Pergunta recebida: 'Qual o piso salarial para analistas de sistemas em SP?'\n2025-04-19 11:00:20 [INFO] Consultando base de dados\n2025-04-19 11:00:25 [INFO] Enviando consulta para o Gemini\n2025-04-19 11:00:35 [INFO] Resposta recebida do Gemini\n2025-04-19 11:00:40 [INFO] Resposta enviada ao usuário\n2025-04-19 11:01:30 [INFO] Pergunta recebida: 'E no Rio de Janeiro?'\n2025-04-19 11:01:35 [INFO] Consultando base de dados com contexto da conversa\n2025-04-19 11:01:45 [INFO] Resposta enviada ao usuário"
};
