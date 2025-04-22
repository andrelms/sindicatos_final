# Documentação das Alterações no Projeto de Sindicatos

## Visão Geral
Este documento descreve as alterações realizadas no projeto de automação de sindicatos para melhorar sua consistência, funcionalidade e desempenho. As modificações foram feitas conforme solicitado, incluindo a limpeza de dados de exemplo, correção do tema dark/light, revisão visual e implementação de automação para coleta de dados.

## Alterações Realizadas

### 1. Limpeza de Dados
- Removidos todos os dados de exemplo do banco de dados
- Mantida a estrutura do banco para permitir o carregamento de novos dados
- Criado script `limpar_banco.py` para facilitar futuras limpezas

### 2. Correção do Tema Dark/Light
- Identificado problema de conflito entre duas implementações diferentes do tema
- Unificado o código de gerenciamento de tema no arquivo `theme.js`
- Removido código duplicado do template `base.html`
- Implementada solução que mantém consistência entre abas e sessões
- Corrigida a transição visual entre temas

### 3. Automação para Coleta de Dados
- Implementado novo módulo `union_data_collector.py` para automação de coleta
- Funcionalidades implementadas:
  - Busca automática de convenções coletivas nos sites dos sindicatos
  - Download e processamento de PDFs encontrados
  - Extração de informações estruturadas usando Gemini API
  - Armazenamento dos dados no banco de dados
  - Sistema de logs para rastreamento de operações

### 4. Sistema RAG Aprimorado
- Implementado sistema RAG (Retrieval Augmented Generation) completo
- Funcionalidades do sistema RAG:
  - Indexação de documentos (convenções e cláusulas)
  - Divisão de textos longos em chunks para melhor recuperação
  - Busca por similaridade usando TF-IDF e cosine similarity
  - Geração de respostas contextualizadas com o Gemini
  - Rastreabilidade das fontes de informação

### 5. Testes de Integração
- Criados scripts de teste para verificar a integração completa:
  - `test_integration.py`: testa a integração do backend
  - `test_ui.py`: testa a interface do usuário e responsividade

## Arquivos Modificados/Criados

### Arquivos Modificados:
- `static/js/theme.js`: Reescrito para corrigir problemas de tema
- `templates/base.html`: Removido código duplicado de tema
- `backend/routes.py`: Atualizado para incluir novas rotas de API

### Arquivos Criados:
- `backend/union_data_collector.py`: Implementação da automação de coleta
- `backend/rag_system.py`: Sistema RAG aprimorado
- `test_integration.py`: Testes de integração do backend
- `test_ui.py`: Testes da interface do usuário
- `limpar_banco.py`: Script para limpeza do banco de dados

## Instruções de Uso

### Automação de Coleta
Para iniciar a coleta automática de dados de sindicatos:
1. Certifique-se de que os sindicatos estão cadastrados no sistema com URLs válidos
2. Acesse a página de Automação no sistema
3. Clique em "Iniciar Coleta" para todos os sindicatos ou selecione um específico

### Sistema RAG
Para utilizar o sistema RAG:
1. Os documentos são indexados automaticamente quando carregados
2. Utilize a interface de chat para fazer perguntas sobre convenções coletivas
3. O sistema retornará respostas baseadas apenas nos documentos indexados
4. As fontes das informações serão exibidas para rastreabilidade

## Próximos Passos Recomendados
1. Implementar autenticação de usuários para maior segurança
2. Expandir a automação para mais fontes de dados
3. Melhorar a visualização de dados com gráficos interativos
4. Implementar alertas para novas convenções coletivas
5. Criar API pública para integração com outros sistemas
