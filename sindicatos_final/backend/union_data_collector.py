"""
Módulo para automação de coleta de dados de sindicatos
"""
import os
import re
import time
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from backend.models import db, Sindicato, Convencao, Clausula, Log
from backend.gemini_integration import GeminiAPI
from backend.pdf_processor import PDFProcessor

class UnionDataCollector:
    """Classe para automação de coleta de dados de sindicatos"""
    
    def __init__(self):
        """Inicializa o coletor de dados de sindicatos"""
        self.gemini_api = GeminiAPI()
        self.pdf_processor = PDFProcessor()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        self.download_dir = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(self.download_dir, exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("union_collector.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("UnionDataCollector")
    
    def collect_data_for_union(self, sindicato_id=None):
        """Coleta dados para um sindicato específico ou todos os sindicatos"""
        try:
            if sindicato_id:
                sindicato = Sindicato.query.get(sindicato_id)
                if not sindicato:
                    self._log_error(f"Sindicato ID {sindicato_id} não encontrado")
                    return {"success": False, "message": "Sindicato não encontrado"}
                
                # Coletar dados para este sindicato específico
                return self._process_single_union(sindicato)
            
            # Caso contrário, coletar para todos os sindicatos
            sindicatos = Sindicato.query.all()
            results = []
            
            for sindicato in sindicatos:
                result = self._process_single_union(sindicato)
                results.append({
                    "sindicato": sindicato.nome,
                    "success": result.get("success", False),
                    "message": result.get("message", ""),
                    "conventions_found": len(result.get("conventions", []))
                })
            
            self._log_info(f"Coleta de dados concluída para {len(sindicatos)} sindicatos")
            
            return {
                "success": True,
                "results": results,
                "total_unions": len(sindicatos)
            }
        except Exception as e:
            self._log_error(f"Erro ao coletar dados de sindicatos: {str(e)}")
            return {"success": False, "message": f"Erro ao coletar dados: {str(e)}"}
    
    def _process_single_union(self, sindicato):
        """Processa um único sindicato para coleta de dados"""
        self._log_info(f"Iniciando coleta de dados para: {sindicato.nome}")
        
        try:
            # 1. Verificar site do sindicato
            if not sindicato.site:
                return {"success": False, "message": "Sindicato não possui site cadastrado", "conventions": []}
            
            # Garantir que o site tenha o protocolo
            site_url = sindicato.site
            if not site_url.startswith(('http://', 'https://')):
                site_url = 'https://' + site_url
            
            # 2. Buscar convenções coletivas no site
            conventions = self._find_conventions_on_website(site_url, sindicato)
            
            # 3. Baixar e processar as convenções encontradas
            processed_conventions = []
            for convention in conventions:
                result = self._download_and_process_convention(convention, sindicato)
                if result.get("success"):
                    processed_conventions.append(result)
            
            self._log_info(f"Coleta concluída para {sindicato.nome}: {len(processed_conventions)} convenções processadas")
            
            return {
                "success": True,
                "message": f"Coleta concluída: {len(processed_conventions)} convenções processadas",
                "conventions": processed_conventions,
                "union": sindicato.to_dict()
            }
        except Exception as e:
            self._log_error(f"Erro ao processar sindicato {sindicato.nome}: {str(e)}")
            return {"success": False, "message": f"Erro: {str(e)}", "conventions": []}
    
    def _find_conventions_on_website(self, site_url, sindicato):
        """Busca convenções coletivas no site do sindicato"""
        try:
            self._log_info(f"Buscando convenções no site: {site_url}")
            
            # Tentar acessar o site
            response = requests.get(site_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Analisar o HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar links que possam ser convenções coletivas
            conventions = []
            
            # Palavras-chave para identificar páginas de convenções
            keywords = [
                'convencao', 'convenção', 'coletiva', 'acordo', 'cct', 'act', 
                'negociacao', 'negociação', 'sindical', 'trabalhista'
            ]
            
            # Buscar links com palavras-chave no texto ou URL
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text().lower()
                
                # Verificar se o link ou texto contém palavras-chave
                if any(keyword in text.lower() for keyword in keywords) or \
                   any(keyword in href.lower() for keyword in keywords):
                    
                    # Normalizar URL
                    if not href.startswith(('http://', 'https://')):
                        href = urljoin(site_url, href)
                    
                    # Verificar se é um PDF
                    is_pdf = href.lower().endswith('.pdf')
                    
                    conventions.append({
                        'url': href,
                        'titulo': link.get_text().strip() or f"Convenção {datetime.now().year}",
                        'tipo': 'PDF' if is_pdf else 'Link',
                        'ano': self._extract_year_from_text(link.get_text()) or datetime.now().year
                    })
            
            # Se não encontrou nada, tentar buscar em páginas específicas
            if not conventions:
                common_paths = [
                    '/convencoes', '/convenções', '/acordos', '/documentos', 
                    '/downloads', '/publicacoes', '/publicações'
                ]
                
                for path in common_paths:
                    try:
                        subpage_url = urljoin(site_url, path)
                        subpage_response = requests.get(subpage_url, headers=self.headers, timeout=15)
                        
                        if subpage_response.status_code == 200:
                            subpage_soup = BeautifulSoup(subpage_response.text, 'html.parser')
                            
                            for link in subpage_soup.find_all('a', href=True):
                                href = link.get('href')
                                text = link.get_text().lower()
                                
                                # Verificar se é um PDF ou contém palavras-chave
                                if href.lower().endswith('.pdf') or \
                                   any(keyword in text.lower() for keyword in keywords) or \
                                   any(keyword in href.lower() for keyword in keywords):
                                    
                                    # Normalizar URL
                                    if not href.startswith(('http://', 'https://')):
                                        href = urljoin(subpage_url, href)
                                    
                                    # Verificar se é um PDF
                                    is_pdf = href.lower().endswith('.pdf')
                                    
                                    conventions.append({
                                        'url': href,
                                        'titulo': link.get_text().strip() or f"Convenção {datetime.now().year}",
                                        'tipo': 'PDF' if is_pdf else 'Link',
                                        'ano': self._extract_year_from_text(link.get_text()) or datetime.now().year
                                    })
                    except Exception as e:
                        self._log_error(f"Erro ao acessar subpágina {path}: {str(e)}")
            
            self._log_info(f"Encontradas {len(conventions)} possíveis convenções no site {site_url}")
            
            # Remover duplicatas
            unique_conventions = []
            seen_urls = set()
            
            for conv in conventions:
                if conv['url'] not in seen_urls:
                    seen_urls.add(conv['url'])
                    unique_conventions.append(conv)
            
            return unique_conventions
            
        except requests.exceptions.RequestException as e:
            self._log_error(f"Erro ao acessar site {site_url}: {str(e)}")
            return []
        except Exception as e:
            self._log_error(f"Erro ao buscar convenções no site {site_url}: {str(e)}")
            return []
    
    def _download_and_process_convention(self, convention_info, sindicato):
        """Baixa e processa uma convenção coletiva"""
        url = convention_info['url']
        
        try:
            self._log_info(f"Baixando convenção: {url}")
            
            # Criar nome de arquivo baseado na URL
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path) or f"convencao_{convention_info['ano']}.pdf"
            
            if not filename.lower().endswith('.pdf'):
                filename += '.pdf'
            
            # Caminho completo para salvar
            save_path = os.path.join(self.download_dir, filename)
            
            # Baixar o arquivo
            response = requests.get(url, headers=self.headers, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Processar o PDF
            if os.path.exists(save_path):
                # Extrair texto do PDF
                pdf_text = self.pdf_processor.extract_text_from_pdf(save_path)
                
                # Usar Gemini para extrair informações estruturadas
                structured_data = self.gemini_api.process_convention_content(pdf_text, convention_info)
                
                # Salvar no banco de dados
                self._save_convention_to_database(structured_data, convention_info, sindicato, save_path)
                
                return {
                    "success": True,
                    "url": url,
                    "save_path": save_path,
                    "file_size": os.path.getsize(save_path),
                    "structured_data": structured_data
                }
            else:
                self._log_error(f"Falha ao salvar arquivo: {save_path}")
                return {"success": False, "error": "Falha ao salvar arquivo", "url": url}
            
        except Exception as e:
            self._log_error(f"Erro ao baixar/processar convenção {url}: {str(e)}")
            return {"success": False, "error": str(e), "url": url}
    
    def _save_convention_to_database(self, structured_data, convention_info, sindicato, file_path):
        """Salva os dados da convenção no banco de dados"""
        try:
            # Verificar se já existe
            existing = Convencao.query.filter_by(
                sindicato_id=sindicato.id,
                ano=convention_info['ano']
            ).first()
            
            if existing:
                self._log_info(f"Convenção de {convention_info['ano']} já existe para {sindicato.nome}")
                return
            
            # Criar nova convenção
            convencao = Convencao(
                sindicato_id=sindicato.id,
                titulo=convention_info['titulo'],
                ano=convention_info['ano'],
                arquivo_path=file_path,
                data_inicio=structured_data.get('vigencia', {}).get('inicio'),
                data_fim=structured_data.get('vigencia', {}).get('fim'),
                reajuste=structured_data.get('reajuste_salarial')
            )
            
            db.session.add(convencao)
            db.session.flush()  # Para obter o ID da convenção
            
            # Adicionar cláusulas
            for clausula_info in structured_data.get('clausulas', []):
                clausula = Clausula(
                    convencao_id=convencao.id,
                    numero=clausula_info.get('numero', ''),
                    titulo=clausula_info.get('titulo', ''),
                    conteudo=''  # O conteúdo seria extraído em um processamento mais detalhado
                )
                db.session.add(clausula)
            
            db.session.commit()
            self._log_info(f"Convenção {convention_info['ano']} salva para {sindicato.nome}")
            
        except Exception as e:
            db.session.rollback()
            self._log_error(f"Erro ao salvar convenção no banco: {str(e)}")
            raise
    
    def _extract_year_from_text(self, text):
        """Extrai o ano de um texto"""
        # Buscar padrões como "2023", "2023/2024", "2023-2024"
        year_patterns = [
            r'20\d{2}',  # Ano simples como 2023
            r'20\d{2}[/-]20\d{2}',  # Padrão ano/ano como 2023/2024 ou 2023-2024
        ]
        
        for pattern in year_patterns:
            match = re.search(pattern, text)
            if match:
                # Retornar o primeiro ano encontrado
                year_str = match.group(0).split('/')[0].split('-')[0]
                return int(year_str)
        
        return None
    
    def _log_info(self, message):
        """Registra mensagem de informação no log"""
        self.logger.info(message)
        log = Log(tipo="automacao", nivel="INFO", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    def _log_error(self, message):
        """Registra mensagem de erro no log"""
        self.logger.error(message)
        log = Log(tipo="automacao", nivel="ERROR", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
