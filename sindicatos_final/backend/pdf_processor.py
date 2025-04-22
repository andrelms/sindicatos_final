import os
import shutil
import logging
from werkzeug.utils import secure_filename
from flask import current_app
import PyPDF2
import pandas as pd
from backend.gemini_integration import GeminiAPI
from backend.models import db, Sindicato, Convencao, Clausula, Arquivo, Log

class PDFProcessor:
    """Classe para processamento de arquivos PDF de convenções coletivas"""
    
    def __init__(self):
        self.gemini_api = GeminiAPI()
        self.allowed_mime_types = ['application/pdf']
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.output_folder = "processados"
        os.makedirs(self.output_folder, exist_ok=True)

    def validate_pdf(self, pdf_path):
        """Valida um arquivo PDF antes do processamento"""
        try:
            if not os.path.exists(pdf_path):
                raise ValueError("Arquivo não encontrado")
                
            # Verificar tamanho
            file_size = os.path.getsize(pdf_path)
            if file_size > self.max_file_size:
                raise ValueError(f"Arquivo muito grande. Máximo permitido: {self.max_file_size/1024/1024:.1f}MB")
                
            # Verificar se é um PDF válido
            try:
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    if len(reader.pages) == 0:
                        raise ValueError("PDF vazio ou inválido")
            except Exception as e:
                raise ValueError(f"PDF inválido: {str(e)}")
                
            return True
        except Exception as e:
            logging.error(f"Erro na validação do PDF: {str(e)}")
            return False
    
    def extract_text_from_pdf(self, pdf_path):
        """Extrai texto de um arquivo PDF com melhor tratamento de erros"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                
                for page_num in range(total_pages):
                    try:
                        page = reader.pages[page_num]
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
                        else:
                            logging.warning(f"Página {page_num + 1} vazia ou não extraível")
                    except Exception as e:
                        logging.error(f"Erro ao extrair texto da página {page_num + 1}: {str(e)}")
                        continue
            
            if not text.strip():
                raise ValueError("Nenhum texto extraído do PDF")
            
            return text
        except Exception as e:
            logging.error(f"Erro ao extrair texto do PDF: {str(e)}")
            raise
    
    def process_pdf(self, arquivo_id):
        """Processa um arquivo PDF com melhor tratamento de erros e validações"""
        try:
            arquivo = Arquivo.query.get(arquivo_id)
            if not arquivo:
                raise ValueError(f"Arquivo não encontrado: {arquivo_id}")

            if not self.validate_pdf(arquivo.caminho):
                raise ValueError("Arquivo PDF inválido")

            # Extrair texto do PDF
            pdf_text = self.extract_text_from_pdf(arquivo.caminho)
            if not pdf_text:
                raise ValueError("Nenhum texto extraído do PDF")

            # Processar com Gemini API
            analysis_results = self.gemini_api.analyze_pdf_content(pdf_text)
            if not analysis_results:
                raise ValueError("Falha na análise do conteúdo")

            # Salvar resultados no banco
            self.save_to_database(arquivo.caminho, analysis_results)

            # Atualizar status do arquivo
            arquivo.processado = True
            db.session.commit()

            return {"success": True, "message": "PDF processado com sucesso"}

        except Exception as e:
            db.session.rollback()
            logging.error(f"❌ Erro ao processar PDF: {str(e)}")
            return {"success": False, "message": f"Erro ao processar arquivo: {str(e)}"}

    def save_to_database(self, pdf_path, analysis_results):
        """Salva os resultados da análise no banco de dados"""
        try:
            # Criar ou atualizar sindicato
            nome_sindicato = analysis_results.get("sindicato", {}).get("nome")
            if not nome_sindicato:
                raise ValueError("Nome do sindicato não encontrado nos resultados")

            sindicato = Sindicato.query.filter_by(nome=nome_sindicato).first()
            if not sindicato:
                sindicato = Sindicato(
                    nome=nome_sindicato,
                    cnpj=analysis_results.get("sindicato", {}).get("cnpj", ""),
                    estado=analysis_results.get("sindicato", {}).get("estado", ""),
                    cidade=analysis_results.get("sindicato", {}).get("cidade", "")
                )
                db.session.add(sindicato)
                db.session.flush()

            # Criar convenção coletiva
            convencao = Convencao(
                sindicato_id=sindicato.id,
                titulo=analysis_results.get("titulo", ""),
                data_base=analysis_results.get("data_base", ""),
                vigencia_inicio=analysis_results.get("vigencia", {}).get("inicio", ""),
                vigencia_fim=analysis_results.get("vigencia", {}).get("fim", ""),
                arquivo_path=pdf_path
            )
            db.session.add(convencao)
            db.session.flush()

            # Salvar cláusulas
            for clausula_data in analysis_results.get("clausulas", []):
                clausula = Clausula(
                    convencao_id=convencao.id,
                    numero=clausula_data.get("numero", ""),
                    titulo=clausula_data.get("titulo", ""),
                    texto=clausula_data.get("texto", ""),
                    categoria=clausula_data.get("categoria", "GERAL")
                )
                db.session.add(clausula)

            db.session.commit()
            logging.info(f"Dados do PDF salvos com sucesso: {os.path.basename(pdf_path)}")

        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao salvar dados do PDF no banco: {str(e)}")
            raise


class ExcelProcessor:
    """Classe para processamento de arquivos Excel com dados de sindicatos"""
    
    def __init__(self):
        self.db = db
    
    def process_excel(self, arquivo_id):
        """Processa um arquivo Excel com dados de sindicatos"""
        try:
            # Obter informações do arquivo
            arquivo = Arquivo.query.get(arquivo_id)
            if not arquivo:
                raise ValueError(f"Arquivo ID {arquivo_id} não encontrado")
                
            excel_path = arquivo.caminho
            
            # Ler arquivo Excel
            df = pd.read_excel(excel_path)
            
            # Verificar colunas necessárias
            required_columns = ['SINDICATO', 'ESTADO']
            missing_columns = [col for col in required_columns if col.upper() not in [c.upper() for c in df.columns]]
            
            if missing_columns:
                self._log_error(f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}")
                return {
                    "success": False, 
                    "message": f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}"
                }
            
            # Normalizar nomes das colunas (transformar em uppercase para comparação case-insensitive)
            col_mapping = {}
            for col in df.columns:
                col_mapping[col.upper()] = col
            
            # Processar dados
            processed_data = []
            
            for _, row in df.iterrows():
                # Encontrar ou criar sindicato
                nome_sindicato = row[col_mapping.get('SINDICATO', 'SINDICATO')]
                if pd.isna(nome_sindicato) or not nome_sindicato:
                    continue
                
                # Dados básicos
                estado = row[col_mapping.get('ESTADO', 'ESTADO')] if 'ESTADO' in col_mapping else None
                
                # Buscar por colunas que contêm informações específicas
                cargo_cols = [col for col in df.columns if any(termo in col.upper() for termo in ['CARGO', 'FUNÇÃO', 'CBO'])]
                piso_cols = [col for col in df.columns if any(termo in col.upper() for termo in ['PISO', 'SALÁRIO', 'REMUNERAÇÃO'])]
                carga_cols = [col for col in df.columns if any(termo in col.upper() for termo in ['CARGA', 'HORÁRIA', 'JORNADA', 'HORAS'])]
                
                # Extrair valores específicos
                principal_cargo = None
                if cargo_cols and not pd.isna(row[cargo_cols[0]]):
                    principal_cargo = str(row[cargo_cols[0]])
                
                piso_salarial = None
                if piso_cols and not pd.isna(row[piso_cols[0]]):
                    piso_salarial = str(row[piso_cols[0]])
                
                carga_horaria = None
                if carga_cols and not pd.isna(row[carga_cols[0]]):
                    carga_horaria = str(row[carga_cols[0]])
                
                # Verificar se o sindicato já existe
                sindicato = Sindicato.query.filter_by(nome=nome_sindicato).first()
                
                if not sindicato:
                    # Criar novo sindicato
                    sindicato = Sindicato(
                        nome=nome_sindicato,
                        estado=estado,
                        principal_cargo=principal_cargo,
                        piso_salarial=piso_salarial,
                        carga_horaria=carga_horaria
                    )
                    db.session.add(sindicato)
                else:
                    # Atualizar sindicato existente
                    if estado and not sindicato.estado:
                        sindicato.estado = estado
                    if principal_cargo:
                        sindicato.principal_cargo = principal_cargo
                    if piso_salarial:
                        sindicato.piso_salarial = piso_salarial
                    if carga_horaria:
                        sindicato.carga_horaria = carga_horaria
                
                # Adicionar dados processados para o retorno
                processed_data.append({
                    'sindicato': nome_sindicato,
                    'estado': estado,
                    'cargo': principal_cargo,
                    'piso': piso_salarial,
                    'carga': carga_horaria
                })
            
            # Marcar arquivo como processado
            arquivo.processado = True
            db.session.commit()
            
            self._log_info(f"Excel processado com sucesso: {len(processed_data)} sindicatos")
            return processed_data
            
        except Exception as e:
            self._log_error(f"Erro ao processar Excel: {str(e)}")
            db.session.rollback()
            return {"success": False, "message": f"Erro ao processar Excel: {str(e)}"}
    
    def save_to_database(self, excel_path, sindicatos_data):
        """Salva os dados de sindicatos no banco de dados"""
        try:
            # Criar sindicatos
            for sindicato_data in sindicatos_data.get("sindicatos", []):
                # Verificar se já existe
                existing = Sindicato.query.filter_by(nome=sindicato_data["nome"]).first()
                if not existing:
                    sindicato = Sindicato(
                        nome=sindicato_data["nome"],
                        sigla=sindicato_data.get("sigla", ""),
                        estado=sindicato_data.get("estado", ""),
                        categoria=sindicato_data.get("categoria", ""),
                        site=sindicato_data.get("site", ""),
                        twitter=sindicato_data.get("twitter", "")
                    )
                    db.session.add(sindicato)
            
            # Atualizar arquivo como processado
            arquivo = Arquivo.query.filter_by(caminho=excel_path).first()
            if arquivo:
                arquivo.processado = True
            
            db.session.commit()
            
            # Registrar log
            self._log_info(f"Dados de sindicatos salvos no banco de dados para: {os.path.basename(excel_path)}")
            
            return {"success": True, "message": "Dados salvos com sucesso"}
        except Exception as e:
            db.session.rollback()
            # Registrar erro
            self._log_error(f"Erro ao salvar dados de sindicatos no banco de dados: {str(e)}")
            return {"success": False, "message": f"Erro ao salvar no banco de dados: {str(e)}"}
    
    def _log_info(self, message):
        """Registra mensagem de informação no log"""
        log = Log(tipo="excel", nivel="INFO", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    def _log_error(self, message):
        """Registra mensagem de erro no log"""
        log = Log(tipo="excel", nivel="ERROR", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()


class FileManager:
    """Classe para gerenciamento de arquivos"""
    
    def __init__(self, app=None):
        """Inicializa o gerenciador de arquivos"""
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializa com a aplicação Flask"""
        self.upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def save_file(self, file):
        """Salva um arquivo enviado"""
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Registrar arquivo no banco de dados
            file_size = os.path.getsize(filepath)
            file_ext = os.path.splitext(filename)[1].lower().replace('.', '')
            
            arquivo = Arquivo(
                nome=filename,
                tipo=file_ext,
                caminho=filepath,
                tamanho=file_size,
                processado=False
            )
            
            db.session.add(arquivo)
            db.session.commit()
            
            # Registrar log
            self._log_info(f"Arquivo salvo com sucesso: {filename}")
            
            return {
                "success": True,
                "filename": filename,
                "filepath": filepath,
                "file_id": arquivo.id
            }
        except Exception as e:
            # Registrar erro
            self._log_error(f"Erro ao salvar arquivo: {str(e)}")
            return {"success": False, "message": f"Erro ao salvar arquivo: {str(e)}"}
    
    def delete_file(self, file_id):
        """Exclui um arquivo pelo ID"""
        try:
            arquivo = Arquivo.query.get(file_id)
            if not arquivo:
                return {"success": False, "message": "Arquivo não encontrado"}
            
            # Excluir arquivo físico
            if os.path.exists(arquivo.caminho):
                os.remove(arquivo.caminho)
            
            # Excluir registro do banco
            db.session.delete(arquivo)
            db.session.commit()
            
            # Registrar log
            self._log_info(f"Arquivo excluído com sucesso: {arquivo.nome}")
            
            return {"success": True, "message": "Arquivo excluído com sucesso"}
        except Exception as e:
            db.session.rollback()
            # Registrar erro
            self._log_error(f"Erro ao excluir arquivo: {str(e)}")
            return {"success": False, "message": f"Erro ao excluir arquivo: {str(e)}"}
    
    def delete_files_by_type(self, file_type):
        """Exclui todos os arquivos de um determinado tipo"""
        try:
            arquivos = Arquivo.query.filter_by(tipo=file_type).all()
            
            for arquivo in arquivos:
                # Excluir arquivo físico
                if os.path.exists(arquivo.caminho):
                    os.remove(arquivo.caminho)
                
                # Excluir registro do banco
                db.session.delete(arquivo)
            
            db.session.commit()
            
            # Registrar log
            self._log_info(f"Todos os arquivos do tipo {file_type} foram excluídos")
            
            return {"success": True, "message": f"Arquivos do tipo {file_type} excluídos com sucesso"}
        except Exception as e:
            db.session.rollback()
            # Registrar erro
            self._log_error(f"Erro ao excluir arquivos do tipo {file_type}: {str(e)}")
            return {"success": False, "message": f"Erro ao excluir arquivos: {str(e)}"}
    
    def delete_all_files(self):
        """Exclui todos os arquivos"""
        try:
            arquivos = Arquivo.query.all()
            
            for arquivo in arquivos:
                # Excluir arquivo físico
                if os.path.exists(arquivo.caminho):
                    os.remove(arquivo.caminho)
                
                # Excluir registro do banco
                db.session.delete(arquivo)
            
            db.session.commit()
            
            # Registrar log
            self._log_info("Todos os arquivos foram excluídos")
            
            return {"success": True, "message": "Todos os arquivos excluídos com sucesso"}
        except Exception as e:
            db.session.rollback()
            # Registrar erro
            self._log_error(f"Erro ao excluir todos os arquivos: {str(e)}")
            return {"success": False, "message": f"Erro ao excluir arquivos: {str(e)}"}
    
    def _log_info(self, message):
        """Registra mensagem de informação no log"""
        log = Log(tipo="app", nivel="INFO", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    def _log_error(self, message):
        """Registra mensagem de erro no log"""
        log = Log(tipo="app", nivel="ERROR", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
