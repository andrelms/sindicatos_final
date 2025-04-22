from flask_sqlalchemy import SQLAlchemy

# Inicialização do banco de dados
db = SQLAlchemy()

# Arquivo __init__.py para tornar o diretório backend um pacote Python
# Isso permite importações como "from backend.models import X"
