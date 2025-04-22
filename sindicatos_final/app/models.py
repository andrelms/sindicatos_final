"""
Modelos de dados da aplicação.
"""
from app import db
from datetime import datetime
from flask_login import UserMixin

class Arquivo(db.Model):
    """Modelo para arquivos carregados"""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    caminho = db.Column(db.String(500), nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    processado = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, nullable=False)
    
    processamentos = db.relationship('Processamento', backref='arquivo', lazy=True)

class Processamento(db.Model):
    """Modelo para processamentos de arquivos"""
    id = db.Column(db.Integer, primary_key=True)
    arquivo_id = db.Column(db.Integer, db.ForeignKey('arquivo.id'), nullable=False)
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_fim = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pendente')  # pendente, em_progresso, concluido, erro
    mensagem = db.Column(db.Text, nullable=True)
    
    resultados = db.relationship('Resultado', backref='processamento', lazy=True)

class Resultado(db.Model):
    """Modelo para resultados de processamento"""
    id = db.Column(db.Integer, primary_key=True)
    processamento_id = db.Column(db.Integer, db.ForeignKey('processamento.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # tabela, texto, grafico
    titulo = db.Column(db.String(255), nullable=True)
    descricao = db.Column(db.Text, nullable=True)
    dados = db.Column(db.Text, nullable=True)  # JSON ou outro formato
    html_content = db.Column(db.Text, nullable=True)  # Conteúdo HTML gerado 