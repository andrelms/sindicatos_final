"""
Arquivo WSGI para implantação em produção
"""
import os
import sys

# Adicionar diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar a aplicação Flask
from app import create_app

# Criar a aplicação
application = create_app()

# Para execução com Gunicorn
app = application

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
