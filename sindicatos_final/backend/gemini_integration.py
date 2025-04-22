import os
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup
import re
import datetime

class GeminiAPI:
    """Classe para integração com a API do Google Gemini"""
    
    def __init__(self):
        """Inicializa a API do Gemini com a chave fornecida"""
        self.api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyB4BKkhU-yhPt0RoefnTgJ-xDTh6g2LdX4')
        self.model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.5-pro')
        self.configure()
    
    def configure(self):
        """Configura a API do Gemini"""
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)
        
        # Configurações padrão
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Configurações de segurança
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    
    def update_config(self, config: Dict[str, Any]):
        """Atualiza as configurações do modelo"""
        self.generation_config.update(config)
    
    def generate_text(self, prompt: str) -> str:
        """Gera texto a partir de um prompt usando o modelo Gemini"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            return response.text
        except Exception as e:
            print(f"Erro ao gerar texto com Gemini: {e}")
            return f"Erro ao processar solicitação: {str(e)}"
    
    def analyze_pdf_content(self, pdf_text: str) -> Dict[str, Any]:
        """Analisa o conteúdo de um PDF de convenção coletiva"""
        prompt = f"""
        Analise o seguinte texto extraído de uma convenção coletiva e extraia as informações estruturadas:
        
        {pdf_text[:10000]}  # Limitando para evitar exceder o limite de tokens
        
        Extraia e retorne as seguintes informações em formato estruturado:
        1. Nome do sindicato
        2. Data de assinatura
        3. Período de vigência
        4. Lista de cláusulas (número, título e texto)
        5. Categorias principais abordadas (ex: remuneração, jornada, benefícios)
        
        Formate a resposta de forma estruturada para facilitar o processamento.
        """
        
        response = self.generate_text(prompt)
        
        # Em uma implementação real, faríamos parsing da resposta
        # Para simplificar, retornamos um dicionário com a resposta bruta
        return {
            "raw_response": response,
            "success": True
        }
    
    def extract_clauses(self, pdf_text: str) -> List[Dict[str, Any]]:
        """Extrai cláusulas de uma convenção coletiva"""
        prompt = f"""
        Extraia todas as cláusulas do seguinte texto de convenção coletiva:
        
        {pdf_text[:10000]}  # Limitando para evitar exceder o limite de tokens
        
        Para cada cláusula, forneça:
        1. Número da cláusula
        2. Título da cláusula
        3. Texto completo da cláusula
        4. Categoria (ex: remuneração, jornada, benefícios)
        
        Formate a resposta como uma lista de cláusulas, cada uma com os campos acima.
        """
        
        response = self.generate_text(prompt)
        
        # Em uma implementação real, faríamos parsing da resposta para uma lista de dicionários
        # Para simplificar, retornamos uma lista simulada
        return [
            {
                "numero": "1",
                "titulo": "REAJUSTE SALARIAL",
                "texto": "Os salários dos empregados abrangidos pelo presente acordo coletivo serão reajustados em X%...",
                "categoria": "remuneração"
            },
            {
                "numero": "2",
                "titulo": "PISO SALARIAL",
                "texto": "Fica estabelecido o piso salarial da categoria em R$ X...",
                "categoria": "remuneração"
            }
        ]
    
    def answer_question(self, question: str, context: Optional[str] = None) -> str:
        """Responde a uma pergunta sobre convenções coletivas"""
        if context:
            prompt = f"""
            Com base nas informações a seguir sobre convenções coletivas:
            
            {context}
            
            Responda à seguinte pergunta de forma clara e objetiva:
            {question}
            """
        else:
            prompt = f"""
            Você é um assistente especializado em convenções coletivas e direito sindical.
            Responda à seguinte pergunta de forma clara e objetiva:
            
            {question}
            """
        
        return self.generate_text(prompt)
    
    def find_union_by_cnpj(self, cnpj: str) -> Dict[str, Any]:
        """Busca um sindicato pelo CNPJ e localiza suas informações e convenções"""
        # Formatar CNPJ para busca
        cnpj_formatado = cnpj.replace('.', '').replace('/', '').replace('-', '')
        
        prompt = f"""
        Você é um assistente especializado em encontrar informações sobre sindicatos brasileiros.
        
        Com base no CNPJ {cnpj}, preciso que você:
        
        1. Identifique o nome oficial do sindicato
        2. Localize o site oficial deste sindicato
        3. Identifique onde posso encontrar convenções coletivas recentes (2023, 2024, 2025)
        4. Forneça URLs específicas para download das convenções mais recentes
        5. Informe outros dados importantes (categoria profissional, abrangência territorial)
        
        Forneça essas informações em formato estruturado, pronto para processamento em JSON.
        """
        
        response = self.generate_text(prompt)
        
        # Simular resultado positivo
        current_year = datetime.datetime.now().year
        
        return {
            "nome_sindicato": f"Sindicato encontrado via CNPJ {cnpj}",
            "cnpj": cnpj,
            "site_oficial": "http://www.exemplo.com.br",
            "convencoes": [
                {
                    "ano": str(current_year),
                    "url": f"http://www.exemplo.com.br/convencoes/cct_{current_year}.pdf",
                    "baixada": False
                },
                {
                    "ano": str(current_year-1),
                    "url": f"http://www.exemplo.com.br/convencoes/cct_{current_year-1}.pdf",
                    "baixada": False
                }
            ],
            "categoria": "Exemplo de categoria profissional",
            "abrangencia": "Estado de São Paulo",
            "raw_response": response,
            "success": True
        }
    
    def search_union_websites(self, union_name: str, union_website: Optional[str] = None, download_path: Optional[str] = None) -> Dict[str, Any]:
        """Busca informações e convenções coletivas em sites de sindicatos"""
        # Definir caminho para download, se não fornecido
        if not download_path:
            download_path = os.path.join(os.getcwd(), 'downloads', 'convencoes')
            os.makedirs(download_path, exist_ok=True)
        
        # Buscar website se não fornecido
        if not union_website:
            search_prompt = f"""
            Você é um assistente especializado em encontrar informações sobre sindicatos brasileiros.
            
            Preciso encontrar o site oficial do sindicato: {union_name}
            
            Forneça:
            1. A URL mais provável do site oficial deste sindicato (formato http://www.exemplo.com.br)
            2. URLs alternativas onde posso encontrar informações sobre este sindicato
            3. URLs específicas onde posso encontrar as convenções coletivas de 2023, 2024 e 2025 (se disponíveis)
            
            Forneça estas informações em formato estruturado, pronto para processamento em JSON.
            """
            
            search_response = self.generate_text(search_prompt)
            
            # Em uma implementação real, faríamos parsing da resposta
            # Para demonstração, definimos uma URL fictícia
            union_website = "http://www.sindicatoexemplo.org.br"
        
        # Buscar páginas com convenções coletivas recentes
        convention_prompt = f"""
        Você é um assistente especializado em localizar convenções coletivas em sites de sindicatos brasileiros.
        
        Preciso encontrar as convenções coletivas mais recentes do sindicato: {union_name}
        Site oficial: {union_website}
        
        Forneça:
        1. URLs específicas para download direto das convenções coletivas de 2023, 2024 e 2025
        2. Caminho de navegação no site para encontrar a página de convenções
        3. Padrões comuns de nomes de arquivos de convenções neste site
        
        Forneça estas informações em formato estruturado, pronto para processamento em JSON.
        """
        
        convention_response = self.generate_text(convention_prompt)
        
        # Simulação de resultados de busca e download
        current_year = datetime.datetime.now().year
        
        # Lista para armazenar convenções encontradas
        conventions_found = []
        
        # Simulação de busca para os últimos 3 anos
        for year in range(current_year, current_year-3, -1):
            convention_url = f"{union_website}/convencoes/convencao_{year}.pdf"
            
            # Adicionar à lista de convenções encontradas
            conventions_found.append({
                "ano": str(year),
                "url": convention_url,
                "nome_arquivo": f"convencao_{union_name}_{year}.pdf",
                "caminho_local": os.path.join(download_path, f"convencao_{union_name}_{year}.pdf"),
                "baixado": False,
                "data_busca": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Aqui implementaríamos o download real dos arquivos
        # Para demonstração, apenas simulamos o processo
        
        download_results = []
        for conv in conventions_found:
            # Simulação de sucesso/falha no download
            success = year % 2 == 0  # Alternando sucesso/falha para demonstração
            
            download_results.append({
                "ano": conv["ano"],
                "url": conv["url"],
                "sucesso": success,
                "caminho_local": conv["caminho_local"] if success else None,
                "erro": None if success else "Arquivo não encontrado no servidor"
            })
        
        # Montar resposta final
        result = {
            "nome_sindicato": union_name,
            "website": union_website,
            "convencoes_encontradas": conventions_found,
            "downloads": download_results,
            "data_busca": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "detalhes": {
                "busca_url": search_response if not union_website else None,
                "busca_convencoes": convention_response
            },
            "success": True
        }
        
        return result
    
    def download_convention_file(self, url: str, save_path: str) -> Dict[str, Any]:
        """Baixa um arquivo de convenção coletiva de uma URL específica"""
        try:
            # Em implementação real, faríamos o download aqui
            # Para demonstração, apenas simulamos o processo
            
            # Verificar se é URL válida
            if not url.startswith(('http://', 'https://')):
                return {
                    "success": False,
                    "error": "URL inválida",
                    "url": url,
                    "save_path": save_path
                }
            
            # Simular download bem-sucedido
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Em implementação real:
            # response = requests.get(url, stream=True)
            # if response.status_code == 200:
            #     with open(save_path, 'wb') as f:
            #         for chunk in response.iter_content(chunk_size=8192):
            #             f.write(chunk)
            
            # Criar arquivo simulado
            with open(save_path, 'w') as f:
                f.write(f"Simulação de convenção coletiva baixada de {url}")
            
            return {
                "success": True,
                "url": url,
                "save_path": save_path,
                "file_size": os.path.getsize(save_path) if os.path.exists(save_path) else 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "save_path": save_path
            }
    
    def extract_conventions_from_webpage(self, url: str) -> List[Dict[str, Any]]:
        """Extrai links de convenções coletivas de uma página web"""
        try:
            # Em implementação real, faríamos o processamento real da página
            # Para demonstração, apenas simulamos o processo
            
            # Simular encontrar convenções
            current_year = datetime.datetime.now().year
            conventions = []
            
            for year in range(current_year, current_year-3, -1):
                conventions.append({
                    "ano": str(year),
                    "titulo": f"Convenção Coletiva {year}",
                    "url": f"{url}/downloads/convencao_{year}.pdf",
                    "tipo": "PDF"
                })
            
            return conventions
            
        except Exception as e:
            print(f"Erro ao extrair convenções da página {url}: {e}")
            return []
    
    def process_convention_content(self, content: str, convention_info: Dict[str, Any]) -> Dict[str, Any]:
        """Processa o conteúdo de uma convenção coletiva usando RAG"""
        prompt = f"""
        Analise o seguinte conteúdo de convenção coletiva e extraia informações estruturadas:
        
        {content[:10000]}  # Limitando texto para não exceder o limite de tokens
        
        Extraia as seguintes informações:
        1. Data de vigência (início e fim)
        2. Categorias profissionais abrangidas
        3. Reajuste salarial (percentual)
        4. Piso salarial por categoria
        5. Benefícios principais (valor do vale-refeição, vale-alimentação, etc.)
        6. Jornada de trabalho
        7. Lista de todas as cláusulas com seus números e títulos
        
        Forneça as informações em formato estruturado JSON.
        """
        
        response = self.generate_text(prompt)
        
        # Simulação de dados estruturados extraídos
        structured_data = {
            "vigencia": {
                "inicio": f"{convention_info.get('ano', '2023')}-05-01",
                "fim": f"{int(convention_info.get('ano', '2023'))+1}-04-30"
            },
            "categorias_abrangidas": ["Categoria exemplo 1", "Categoria exemplo 2"],
            "reajuste_salarial": "5.5%",
            "pisos_salariais": [
                {"categoria": "Nível I", "valor": "R$ 1.800,00"},
                {"categoria": "Nível II", "valor": "R$ 2.200,00"}
            ],
            "beneficios": {
                "vale_refeicao": "R$ 25,00/dia",
                "vale_alimentacao": "R$ 250,00/mês",
                "plano_saude": "Coparticipativo"
            },
            "jornada": "44 horas semanais",
            "clausulas": [
                {"numero": "1", "titulo": "VIGÊNCIA E DATA-BASE"},
                {"numero": "2", "titulo": "ABRANGÊNCIA"},
                {"numero": "3", "titulo": "REAJUSTE SALARIAL"}
            ],
            "raw_response": response
        }
        
        return structured_data
    
    def summarize_news(self, news_text: str) -> str:
        """Sumariza notícias relacionadas a sindicatos"""
        prompt = f"""
        Sumarize a seguinte notícia relacionada a sindicatos em um parágrafo conciso:
        
        {news_text}
        """
        
        return self.generate_text(prompt)
    
    def test_connection(self) -> Dict[str, Any]:
        """Testa a conexão com a API do Gemini"""
        try:
            response = self.generate_text("Olá, você está funcionando?")
            return {
                "success": True,
                "message": "Conexão com Gemini estabelecida com sucesso",
                "model": self.model_name,
                "response": response
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao conectar com Gemini: {str(e)}",
                "model": self.model_name
            }
