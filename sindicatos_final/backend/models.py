from backend import db
from datetime import datetime

# Modelo para Sindicato
class Sindicato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    sigla = db.Column(db.String(50))
    estado = db.Column(db.String(2))
    cidade = db.Column(db.String(100))
    categoria = db.Column(db.String(100))
    site = db.Column(db.String(255))
    email = db.Column(db.String(255))
    telefone = db.Column(db.String(50))
    twitter = db.Column(db.String(255))
    cnpj = db.Column(db.String(18))
    data_cadastro = db.Column(db.DateTime, default=datetime.now)
    principal_cargo = db.Column(db.String(100))
    piso_salarial = db.Column(db.Float)
    carga_horaria = db.Column(db.Integer)
    
    # Relacionamentos
    convencoes = db.relationship('Convencao', backref='sindicato', lazy=True)
    noticias = db.relationship('Noticia', backref='sindicato', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'sigla': self.sigla,
            'estado': self.estado,
            'cidade': self.cidade,
            'categoria': self.categoria,
            'site': self.site,
            'email': self.email,
            'telefone': self.telefone,
            'twitter': self.twitter,
            'cnpj': self.cnpj,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'principal_cargo': self.principal_cargo,
            'piso_salarial': self.piso_salarial,
            'carga_horaria': self.carga_horaria
        }

# Modelo para Convenção Coletiva
class Convencao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    ano_vigencia = db.Column(db.Integer, nullable=False)
    data_assinatura = db.Column(db.Date, nullable=True)
    arquivo_path = db.Column(db.String(255), nullable=True)
    processado = db.Column(db.Boolean, default=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira
    sindicato_id = db.Column(db.Integer, db.ForeignKey('sindicato.id'), nullable=False)
    
    # Relacionamentos
    clausulas = db.relationship('Clausula', backref='convencao', lazy=True)
    
    def __repr__(self):
        return f'<Convencao {self.titulo} - {self.ano_vigencia}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'ano_vigencia': self.ano_vigencia,
            'data_assinatura': self.data_assinatura.strftime('%d/%m/%Y') if self.data_assinatura else None,
            'arquivo_path': self.arquivo_path,
            'processado': self.processado,
            'data_upload': self.data_upload.strftime('%d/%m/%Y %H:%M'),
            'sindicato_id': self.sindicato_id
        }

# Modelo para Cláusula
class Clausula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), nullable=True)
    titulo = db.Column(db.String(200), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(100), nullable=True)
    pagina_pdf = db.Column(db.Integer, nullable=True)
    
    # Chave estrangeira
    convencao_id = db.Column(db.Integer, db.ForeignKey('convencao.id'), nullable=False)
    
    def __repr__(self):
        return f'<Clausula {self.numero} - {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'titulo': self.titulo,
            'texto': self.texto,
            'categoria': self.categoria,
            'pagina_pdf': self.pagina_pdf,
            'convencao_id': self.convencao_id
        }

# Modelo para Notícia
class Noticia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    fonte = db.Column(db.String(100), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    data_publicacao = db.Column(db.DateTime, nullable=True)
    data_coleta = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira
    sindicato_id = db.Column(db.Integer, db.ForeignKey('sindicato.id'), nullable=True)
    
    def __repr__(self):
        return f'<Noticia {self.titulo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'conteudo': self.conteudo,
            'fonte': self.fonte,
            'url': self.url,
            'data_publicacao': self.data_publicacao.strftime('%d/%m/%Y %H:%M') if self.data_publicacao else None,
            'data_coleta': self.data_coleta.strftime('%d/%m/%Y %H:%M'),
            'sindicato_id': self.sindicato_id
        }

# Modelo para Arquivo
class Arquivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # pdf, excel, etc.
    caminho = db.Column(db.String(255), nullable=False)
    tamanho = db.Column(db.Integer, nullable=False)  # tamanho em bytes
    processado = db.Column(db.Boolean, default=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Arquivo {self.nome}>'
    
    def to_dict(self):
        # Formatar tamanho para exibição
        if self.tamanho < 1024:
            tamanho_formatado = f"{self.tamanho} B"
        elif self.tamanho < 1024 * 1024:
            tamanho_formatado = f"{self.tamanho / 1024:.1f} KB"
        else:
            tamanho_formatado = f"{self.tamanho / (1024 * 1024):.1f} MB"
            
        return {
            'id': self.id,
            'nome': self.nome,
            'tipo': self.tipo,
            'caminho': self.caminho,
            'tamanho': self.tamanho,
            'tamanho_formatado': tamanho_formatado,
            'processado': self.processado,
            'data_upload': self.data_upload.strftime('%d/%m/%Y %H:%M')
        }

# Modelo para Log
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # app, gemini, pdf, web, db
    nivel = db.Column(db.String(10), nullable=False)  # INFO, WARNING, ERROR
    mensagem = db.Column(db.Text, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Log {self.tipo} {self.nivel} {self.data}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'nivel': self.nivel,
            'mensagem': self.mensagem,
            'data': self.data.strftime('%Y-%m-%d %H:%M:%S')
        }

# Modelo para Processamento
class Processamento(db.Model):
    __tablename__ = 'processamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    arquivo_id = db.Column(db.Integer, db.ForeignKey('arquivo.id'))
    data_processamento = db.Column(db.DateTime, default=datetime.utcnow)
    tempo_processamento = db.Column(db.Float)  # tempo em milissegundos
    status = db.Column(db.String(20))  # sucesso, erro, etc
    detalhes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'arquivo_id': self.arquivo_id,
            'data_processamento': self.data_processamento.isoformat(),
            'tempo_processamento': self.tempo_processamento,
            'status': self.status,
            'detalhes': self.detalhes
        }
