"""
Rotas principais da aplicação.
"""
import pandas as pd
from flask import render_template, redirect, url_for, flash, request, current_app, jsonify, session
from app.routes import main_bp
from app.models import Arquivo, Processamento, Resultado
from app import db
import os
from werkzeug.utils import secure_filename
from app.utils.painel_visualizacao import gerar_painel
from app.utils.excel_processor import process_excel_file_with_images
from datetime import datetime

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
def dashboard():
    """Dashboard principal"""
    # Obter estatísticas de processamento
    total_arquivos = Arquivo.query.count()
    processados = Arquivo.query.filter_by(processado=True).count()
    em_processamento = Processamento.query.filter_by(status='em_progresso').count()
    
    return render_template('dashboard.html', 
                          total_arquivos=total_arquivos,
                          processados=processados,
                          em_processamento=em_processamento)

@main_bp.route('/arquivos')
def arquivos():
    """Página de gestão de arquivos"""
    return render_template('arquivos.html')

@main_bp.route('/visualizacao/<int:resultado_id>')
def visualizacao(resultado_id):
    """Visualização de resultados processados"""
    resultado = Resultado.query.get_or_404(resultado_id)
    
    # Carregar HTML gerado ou gerar se não existir
    if resultado.html_content:
        html_content = resultado.html_content
    else:
        html_content = "<p>Conteúdo não disponível</p>"
    
    return render_template('visualizacao.html', 
                          resultado=resultado,
                          html_content=html_content)

@main_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """Página de upload de arquivos"""
    if request.method == 'POST':
        # Verificar se há arquivo na requisição
        if 'file' not in request.files:
            flash('Nenhum arquivo enviado', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        # Verificar extensão
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            flash(f'Tipo de arquivo não permitido. Apenas: {", ".join(allowed_extensions)}', 'error')
            return redirect(request.url)
        
        # Salvar o arquivo
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Criar registro no banco de dados
        # Usamos 1 como user_id padrão (admin)
        arquivo = Arquivo(
            nome=filename,
            caminho=file_path,
            user_id=1,
            processado=False
        )
        
        db.session.add(arquivo)
        db.session.commit()
        
        flash(f'Arquivo {filename} enviado com sucesso!', 'success')
        return redirect(url_for('main.arquivos'))
    
    return render_template('upload.html') 