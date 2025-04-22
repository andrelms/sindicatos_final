"""
Configurações da aplicação.
"""
import os

class Config:
    """Configuração base"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chave_dev_temporaria')
    
    # Configuração de uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'xlsx', 'csv', 'jpg', 'jpeg', 'png'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    
    # Configuração do banco de dados
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 