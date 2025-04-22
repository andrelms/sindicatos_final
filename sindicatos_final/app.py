"""
Arquivo de inicialização da aplicação para implantação
"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os

# Inicializar SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuração básica
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sindicatos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Garantir que diretórios existem
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('instance', exist_ok=True)
    
    # Inicializar banco de dados
    db.init_app(app)
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
    
    # Registrar blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
