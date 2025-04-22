"""
Rotas para o backend da aplicação
"""
import os
import json
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from backend.models import db, Sindicato, Convencao, Clausula, Noticia, Arquivo, Log
from backend.gemini_integration import GeminiAPI
from backend.pdf_processor import PDFProcessor, ExcelProcessor, FileManager
from backend.twitter_news_tracker import TwitterNewsTracker
from backend.union_data_collector import UnionDataCollector

# Criar blueprint
bp = Blueprint('api', __name__, url_prefix='/api')

# Instanciar classes auxiliares
gemini_api = GeminiAPI()
pdf_processor = PDFProcessor()
excel_processor = ExcelProcessor()
file_manager = FileManager()
twitter_tracker = TwitterNewsTracker()
union_collector = UnionDataCollector()

@bp.route('/test-gemini', methods=['GET'])
def test_gemini():
    """Testa a conexão com a API do Gemini"""
    result = gemini_api.test_connection()
    return jsonify(result)

@bp.route('/process-pdf', methods=['POST'])
def process_pdf():
    """Processa um arquivo PDF"""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Nenhum arquivo enviado"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "Nenhum arquivo selecionado"})
    
    # Verificar extensão
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"success": False, "message": "Arquivo deve ser PDF"})
    
    # Salvar o arquivo
    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # Processar o PDF
    result = pdf_processor.process_pdf(file_path)
    
    # Registrar no banco de dados
    log = Log(
        tipo="pdf",
        nivel="INFO",
        mensagem=f"Arquivo {filename} processado: {len(result.get('pages', []))} páginas"
    )
    db.session.add(log)
    
    arquivo = Arquivo(
        nome=filename,
        caminho=file_path,
        tipo="pdf",
        tamanho=os.path.getsize(file_path),
        status="processado"
    )
    db.session.add(arquivo)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erro ao salvar no banco: {str(e)}"})
    
    return jsonify({
        "success": True,
        "message": "PDF processado com sucesso",
        "file_id": arquivo.id,
        "pages": len(result.get('pages', [])),
        "text_length": len(result.get('text', '')),
        "filename": filename
    })

@bp.route('/process-excel', methods=['POST'])
def process_excel():
    """Processa um arquivo Excel"""
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "Nenhum arquivo enviado"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "Nenhum arquivo selecionado"})
    
    # Verificar extensão
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({"success": False, "message": "Arquivo deve ser Excel (.xlsx ou .xls)"})
    
    # Salvar o arquivo
    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # Processar o Excel
    result = excel_processor.process_excel(file_path)
    
    # Registrar no banco de dados
    log = Log(
        tipo="excel",
        nivel="INFO",
        mensagem=f"Arquivo {filename} processado: {result.get('rows', 0)} linhas"
    )
    db.session.add(log)
    
    arquivo = Arquivo(
        nome=filename,
        caminho=file_path,
        tipo="excel",
        tamanho=os.path.getsize(file_path),
        status="processado"
    )
    db.session.add(arquivo)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erro ao salvar no banco: {str(e)}"})
    
    return jsonify({
        "success": True,
        "message": "Excel processado com sucesso",
        "file_id": arquivo.id,
        "sheets": result.get('sheets', 1),
        "rows": result.get('rows', 0),
        "filename": filename
    })

@bp.route('/sindicatos', methods=['GET'])
def get_sindicatos():
    """Retorna lista de sindicatos"""
    sindicatos = Sindicato.query.all()
    return jsonify({
        "success": True,
        "sindicatos": [s.to_dict() for s in sindicatos],
        "total": len(sindicatos)
    })

@bp.route('/sindicatos/<int:id>', methods=['GET'])
def get_sindicato(id):
    """Retorna detalhes de um sindicato"""
    sindicato = Sindicato.query.get_or_404(id)
    return jsonify({
        "success": True,
        "sindicato": sindicato.to_dict()
    })

@bp.route('/sindicatos', methods=['POST'])
def create_sindicato():
    """Cria um novo sindicato"""
    data = request.json
    
    if not data or not data.get('nome'):
        return jsonify({"success": False, "message": "Nome do sindicato é obrigatório"})
    
    sindicato = Sindicato(
        nome=data.get('nome'),
        sigla=data.get('sigla', ''),
        estado=data.get('estado', ''),
        cidade=data.get('cidade', ''),
        site=data.get('site', ''),
        email=data.get('email', ''),
        telefone=data.get('telefone', ''),
        twitter=data.get('twitter', '')
    )
    
    db.session.add(sindicato)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erro ao criar sindicato: {str(e)}"})
    
    return jsonify({
        "success": True,
        "message": "Sindicato criado com sucesso",
        "sindicato": sindicato.to_dict()
    })

@bp.route('/sindicatos/<int:id>', methods=['PUT'])
def update_sindicato(id):
    """Atualiza um sindicato"""
    sindicato = Sindicato.query.get_or_404(id)
    data = request.json
    
    if not data:
        return jsonify({"success": False, "message": "Dados não fornecidos"})
    
    # Atualizar campos
    if 'nome' in data:
        sindicato.nome = data['nome']
    if 'sigla' in data:
        sindicato.sigla = data['sigla']
    if 'estado' in data:
        sindicato.estado = data['estado']
    if 'cidade' in data:
        sindicato.cidade = data['cidade']
    if 'site' in data:
        sindicato.site = data['site']
    if 'email' in data:
        sindicato.email = data['email']
    if 'telefone' in data:
        sindicato.telefone = data['telefone']
    if 'twitter' in data:
        sindicato.twitter = data['twitter']
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erro ao atualizar sindicato: {str(e)}"})
    
    return jsonify({
        "success": True,
        "message": "Sindicato atualizado com sucesso",
        "sindicato": sindicato.to_dict()
    })

@bp.route('/sindicatos/<int:id>', methods=['DELETE'])
def delete_sindicato(id):
    """Remove um sindicato"""
    sindicato = Sindicato.query.get_or_404(id)
    
    try:
        db.session.delete(sindicato)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erro ao remover sindicato: {str(e)}"})
    
    return jsonify({
        "success": True,
        "message": "Sindicato removido com sucesso"
    })

@bp.route('/convencoes', methods=['GET'])
def get_convencoes():
    """Retorna lista de convenções coletivas"""
    convencoes = Convencao.query.all()
    return jsonify({
        "success": True,
        "convencoes": [c.to_dict() for c in convencoes],
        "total": len(convencoes)
    })

@bp.route('/convencoes/<int:id>', methods=['GET'])
def get_convencao(id):
    """Retorna detalhes de uma convenção coletiva"""
    convencao = Convencao.query.get_or_404(id)
    return jsonify({
        "success": True,
        "convencao": convencao.to_dict()
    })

@bp.route('/noticias', methods=['GET'])
def get_noticias():
    """Retorna lista de notícias"""
    noticias = Noticia.query.order_by(Noticia.data_publicacao.desc()).all()
    return jsonify({
        "success": True,
        "noticias": [n.to_dict() for n in noticias],
        "total": len(noticias)
    })

@bp.route('/noticias/sindicato/<int:sindicato_id>', methods=['GET'])
def get_noticias_sindicato(sindicato_id):
    """Retorna notícias de um sindicato específico"""
    noticias = Noticia.query.filter_by(sindicato_id=sindicato_id).order_by(Noticia.data_publicacao.desc()).all()
    return jsonify({
        "success": True,
        "noticias": [n.to_dict() for n in noticias],
        "total": len(noticias)
    })

@bp.route('/noticias/busca', methods=['GET'])
def search_noticias():
    """Busca notícias por palavra-chave"""
    keyword = request.args.get('q', '')
    if not keyword:
        return jsonify({"success": False, "message": "Palavra-chave não fornecida"})
    
    noticias = Noticia.query.filter(
        (Noticia.titulo.ilike(f'%{keyword}%')) | 
        (Noticia.conteudo.ilike(f'%{keyword}%'))
    ).order_by(Noticia.data_publicacao.desc()).all()
    
    return jsonify({
        "success": True,
        "keyword": keyword,
        "noticias": [n.to_dict() for n in noticias],
        "total": len(noticias)
    })

@bp.route('/twitter/noticias', methods=['GET'])
def get_twitter_news():
    """Obtém notícias do Twitter/X"""
    sindicato_id = request.args.get('sindicato_id')
    
    if sindicato_id:
        try:
            sindicato_id = int(sindicato_id)
            result = twitter_tracker.get_union_news(sindicato_id)
        except ValueError:
            return jsonify({"success": False, "message": "ID de sindicato inválido"})
    else:
        result = twitter_tracker.get_union_news()
    
    # Salvar notícias no banco de dados
    if result.get("success", False):
        twitter_tracker.save_news_to_database(result)
    
    return jsonify(result)

@bp.route('/twitter/busca', methods=['GET'])
def search_twitter():
    """Busca notícias no Twitter/X por palavra-chave"""
    keyword = request.args.get('q', '')
    if not keyword:
        return jsonify({"success": False, "message": "Palavra-chave não fornecida"})
    
    result = twitter_tracker.search_news_by_keyword(keyword)
    return jsonify(result)

@bp.route('/automacao/coletar', methods=['POST'])
def collect_union_data():
    """Inicia coleta automatizada de dados de sindicatos"""
    data = request.json or {}
    sindicato_id = data.get('sindicato_id')
    
    if sindicato_id:
        try:
            sindicato_id = int(sindicato_id)
            result = union_collector.collect_data_for_union(sindicato_id)
        except ValueError:
            return jsonify({"success": False, "message": "ID de sindicato inválido"})
    else:
        result = union_collector.collect_data_for_union()
    
    return jsonify(result)

@bp.route('/logs', methods=['GET'])
def get_logs():
    """Retorna logs do sistema"""
    tipo = request.args.get('tipo')
    nivel = request.args.get('nivel')
    limit = request.args.get('limit', 100, type=int)
    
    query = Log.query
    
    if tipo:
        query = query.filter_by(tipo=tipo)
    if nivel:
        query = query.filter_by(nivel=nivel)
    
    logs = query.order_by(Log.data.desc()).limit(limit).all()
    
    return jsonify({
        "success": True,
        "logs": [log.to_dict() for log in logs],
        "total": len(logs)
    })

@bp.route('/arquivos', methods=['GET'])
def get_arquivos():
    """Retorna lista de arquivos"""
    arquivos = Arquivo.query.order_by(Arquivo.data_upload.desc()).all()
    return jsonify({
        "success": True,
        "arquivos": [a.to_dict() for a in arquivos],
        "total": len(arquivos)
    })

@bp.route('/arquivos/<int:id>', methods=['GET'])
def get_arquivo(id):
    """Retorna detalhes de um arquivo"""
    arquivo = Arquivo.query.get_or_404(id)
    return jsonify({
        "success": True,
        "arquivo": arquivo.to_dict()
    })

@bp.route('/arquivos/<int:id>/download', methods=['GET'])
def download_arquivo(id):
    """Faz download de um arquivo"""
    arquivo = Arquivo.query.get_or_404(id)
    
    # Verificar se o arquivo existe
    if not os.path.exists(arquivo.caminho):
        return jsonify({"success": False, "message": "Arquivo não encontrado no servidor"})
    
    # Registrar log de download
    log = Log(
        tipo="download",
        nivel="INFO",
        mensagem=f"Download do arquivo {arquivo.nome} (ID: {arquivo.id})"
    )
    db.session.add(log)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    # Retornar o arquivo
    directory = os.path.dirname(arquivo.caminho)
    filename = os.path.basename(arquivo.caminho)
    return send_from_directory(directory, filename, as_attachment=True)

@bp.route('/chat/query', methods=['POST'])
def chat_query():
    """Processa uma consulta para o chat"""
    data = request.json
    
    if not data or not data.get('query'):
        return jsonify({"success": False, "message": "Consulta não fornecida"})
    
    query = data.get('query')
    context = data.get('context', '')
    
    # Registrar log da consulta
    log = Log(
        tipo="chat",
        nivel="INFO",
        mensagem=f"Consulta: {query[:100]}..."
    )
    db.session.add(log)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    # Processar a consulta com o Gemini
    response = gemini_api.generate_text(
        f"Contexto: {context}\n\nConsulta: {query}\n\nResponda apenas com base no contexto fornecido."
    )
    
    return jsonify({
        "success": True,
        "query": query,
        "response": response
    })

@bp.route('/estatisticas', methods=['GET'])
def get_estatisticas():
    """Retorna estatísticas gerais do sistema"""
    total_sindicatos = Sindicato.query.count()
    total_convencoes = Convencao.query.count()
    total_noticias = Noticia.query.count()
    total_arquivos = Arquivo.query.count()
    
    # Convenções por estado
    convencoes_por_estado = db.session.query(
        Sindicato.estado, 
        db.func.count(Convencao.id)
    ).join(Convencao).group_by(Sindicato.estado).all()
    
    # Convenções por ano
    convencoes_por_ano = db.session.query(
        Convencao.ano, 
        db.func.count(Convencao.id)
    ).group_by(Convencao.ano).all()
    
    return jsonify({
        "success": True,
        "estatisticas": {
            "total_sindicatos": total_sindicatos,
            "total_convencoes": total_convencoes,
            "total_noticias": total_noticias,
            "total_arquivos": total_arquivos,
            "convencoes_por_estado": dict(convencoes_por_estado),
            "convencoes_por_ano": dict(convencoes_por_ano)
        }
    })
