"""
Utilitário para geração de painéis de visualização de dados
"""

def gerar_painel(dados, tipo='tabela'):
    """
    Gera HTML para visualização de dados
    
    Args:
        dados: Dados a serem exibidos (dict, DataFrame, etc)
        tipo: Tipo de visualização (tabela, grafico, texto)
        
    Returns:
        String contendo HTML da visualização
    """
    if tipo == 'tabela':
        try:
            # Se for um DataFrame do pandas
            if hasattr(dados, 'to_html'):
                return dados.to_html(classes='table table-striped table-hover', 
                                   border=0, index=False)
            
            # Se for um dicionário ou lista, tenta criar uma tabela simples
            html = "<table class='table table-striped table-hover'>"
            
            # Tentar encontrar cabeçalhos se for lista de dicionários
            if isinstance(dados, list) and len(dados) > 0 and isinstance(dados[0], dict):
                headers = dados[0].keys()
                html += "<thead><tr>"
                for header in headers:
                    html += f"<th>{header}</th>"
                html += "</tr></thead>"
                
                html += "<tbody>"
                for item in dados:
                    html += "<tr>"
                    for value in item.values():
                        html += f"<td>{value}</td>"
                    html += "</tr>"
                html += "</tbody>"
            else:
                # Tabela genérica para outros formatos
                html += "<tbody>"
                html += f"<tr><td>{dados}</td></tr>"
                html += "</tbody>"
                
            html += "</table>"
            return html
        except Exception as e:
            return f"<div class='alert alert-danger'>Erro ao gerar tabela: {str(e)}</div>"
            
    elif tipo == 'texto':
        return f"<div class='card'><div class='card-body'>{dados}</div></div>"
        
    else:
        return f"<div class='alert alert-warning'>Tipo de visualização '{tipo}' não implementado</div>" 