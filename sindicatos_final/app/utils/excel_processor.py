"""
Utilitário para processamento de arquivos Excel
"""

def process_excel_file_with_images(file_path):
    """
    Processa um arquivo Excel que pode conter imagens
    
    Args:
        file_path: Caminho para o arquivo Excel
        
    Returns:
        dict: Dicionário com dados extraídos
    """
    try:
        import pandas as pd
        
        # Carrega o arquivo Excel
        df = pd.read_excel(file_path)
        
        # Processamento simples - apenas retorna os dados tabulares
        # Obs: Para extração de imagens seria necessário usar openpyxl ou outras bibliotecas
        
        return {
            'status': 'success',
            'data': df,
            'message': 'Arquivo processado com sucesso',
            'sheets': 1,
            'rows': len(df)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'message': f'Erro ao processar arquivo: {str(e)}',
            'sheets': 0,
            'rows': 0
        } 