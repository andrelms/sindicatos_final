"""
Configuração para implantação do site
"""
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração para produção
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chave_secreta_temporaria')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///sindicatos.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'csv'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro')
    
    # Configurações de desenvolvimento para inicialização mais rápida
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = False  # Desativa logs SQL
    TEMPLATES_AUTO_RELOAD = True
    SEND_FILE_MAX_AGE_DEFAULT = 0
    
    # Lazy loading para componentes pesados
    LAZY_LOADING = True
