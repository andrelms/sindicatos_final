"""
Pacote principal da aplicação.
"""
import os
from flask import Flask, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, AnonymousUserMixin
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from app.config import Config
# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicializa as extensões
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

# Classe de usuário padrão que será usada em toda a aplicação
class AutoUser(AnonymousUserMixin):
    is_authenticated = True
    is_active = True
    is_anonymous = False
    id = 1
    username = 'admin'
    email = 'admin@exemplo.com'
    nome = 'Administrador'
    
    def get_id(self):
        return str(self.id)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Desativa redirecionamento para login
    login_manager.login_view = None
    
    # Define o handler de usuário anônimo para usar nosso usuário automático
    login_manager.anonymous_user = AutoUser

    @login_manager.user_loader
    def load_user(id):
        # Sempre retorna o usuário automático
        return AutoUser()

    # Antes de cada requisição, definir usuário padrão
    @app.before_request
    def before_request():
        g.user = AutoUser()

    # Registra blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    # Criar o banco de dados
    with app.app_context():
        db.create_all()

    # Desabilita CSRF apenas para rotas específicas da API
    csrf.exempt(api_bp)

    return app 