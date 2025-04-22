import os
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from backend.models import db, Sindicato, Convencao, Clausula, Noticia, Arquivo, Log
from backend.gemini_integration import GeminiAPI
from backend.pdf_processor import PDFProcessor, ExcelProcessor, FileManager

class TwitterNewsTracker:
    """Classe para rastreamento de notícias do Twitter/X e sites de sindicatos"""
    
    def __init__(self):
        """Inicializa o rastreador de notícias"""
        self.gemini_api = GeminiAPI()
    
    def get_union_news(self, sindicato_id=None):
        """Obtém notícias de sindicatos"""
        try:
            # Em uma implementação real, buscaríamos notícias do Twitter/X e sites
            # Para demonstração, retornamos dados simulados
            
            # Se um sindicato específico foi solicitado
            if sindicato_id:
                sindicato = Sindicato.query.get(sindicato_id)
                if not sindicato:
                    return {"success": False, "message": "Sindicato não encontrado"}
                
                # Simular busca para este sindicato específico
                return self._get_mock_news_for_union(sindicato)
            
            # Caso contrário, buscar para todos os sindicatos
            sindicatos = Sindicato.query.all()
            all_news = []
            
            for sindicato in sindicatos:
                union_news = self._get_mock_news_for_union(sindicato)
                if union_news.get("success", False):
                    all_news.extend(union_news.get("news", []))
            
            # Registrar log
            self._log_info(f"Obtidas {len(all_news)} notícias de sindicatos")
            
            return {
                "success": True,
                "news": all_news,
                "total": len(all_news)
            }
        except Exception as e:
            # Registrar erro
            self._log_error(f"Erro ao obter notícias de sindicatos: {str(e)}")
            return {"success": False, "message": f"Erro ao obter notícias: {str(e)}"}
    
    def _get_mock_news_for_union(self, sindicato):
        """Gera notícias simuladas para um sindicato"""
        # Em uma implementação real, faríamos web scraping e consultas à API do Twitter/X
        
        # Notícias simuladas
        mock_news = [
            {
                "titulo": f"Assembleia Geral do {sindicato.nome} aprova nova pauta de reivindicações",
                "conteudo": "Em assembleia realizada ontem, os trabalhadores aprovaram por unanimidade a pauta de reivindicações para a negociação coletiva deste ano. Entre os principais pontos estão reajuste salarial acima da inflação, melhoria no plano de saúde e implementação de home office parcial.",
                "fonte": "Twitter",
                "url": f"https://twitter.com/{sindicato.twitter}/status/123456789",
                "data_publicacao": "2025-04-15 10:30:00",
                "sindicato_id": sindicato.id
            },
            {
                "titulo": f"{sindicato.nome} inicia negociação com empresas do setor",
                "conteudo": "Representantes do sindicato e das empresas do setor se reuniram hoje para a primeira rodada de negociações da convenção coletiva 2025/2026. O clima foi de diálogo, mas ainda há divergências significativas em relação ao percentual de reajuste salarial.",
                "fonte": "Site Oficial",
                "url": f"https://{sindicato.site}/noticias/negociacao-2025",
                "data_publicacao": "2025-04-18 14:45:00",
                "sindicato_id": sindicato.id
            }
        ]
        
        return {
            "success": True,
            "news": mock_news,
            "total": len(mock_news),
            "union": sindicato.to_dict()
        }
    
    def search_news_by_keyword(self, keyword):
        """Busca notícias por palavra-chave"""
        try:
            # Em uma implementação real, buscaríamos notícias com a palavra-chave
            # Para demonstração, retornamos dados simulados
            
            # Simular busca por palavra-chave
            mock_results = [
                {
                    "titulo": f"Impacto da nova legislação trabalhista sobre {keyword}",
                    "conteudo": f"Especialistas analisam como as recentes mudanças na legislação trabalhista afetam as negociações sobre {keyword} nas convenções coletivas.",
                    "fonte": "Portal de Notícias",
                    "url": f"https://noticias.exemplo.com/legislacao-{keyword}",
                    "data_publicacao": "2025-04-10 09:15:00"
                },
                {
                    "titulo": f"Sindicatos unidos por melhores condições de {keyword}",
                    "conteudo": f"Diversos sindicatos se uniram em uma frente comum para negociar melhores condições de {keyword} para os trabalhadores de diferentes setores.",
                    "fonte": "Jornal Sindical",
                    "url": f"https://jornalsindical.com.br/uniao-{keyword}",
                    "data_publicacao": "2025-04-05 16:30:00"
                }
            ]
            
            # Registrar log
            self._log_info(f"Busca por '{keyword}' retornou {len(mock_results)} resultados")
            
            return {
                "success": True,
                "keyword": keyword,
                "results": mock_results,
                "total": len(mock_results)
            }
        except Exception as e:
            # Registrar erro
            self._log_error(f"Erro ao buscar notícias com palavra-chave '{keyword}': {str(e)}")
            return {"success": False, "message": f"Erro ao buscar notícias: {str(e)}"}
    
    def save_news_to_database(self, news_data):
        """Salva notícias no banco de dados"""
        try:
            # Criar notícias
            for news_item in news_data.get("news", []):
                # Verificar se já existe
                existing = Noticia.query.filter_by(
                    titulo=news_item["titulo"],
                    fonte=news_item["fonte"]
                ).first()
                
                if not existing:
                    noticia = Noticia(
                        titulo=news_item["titulo"],
                        conteudo=news_item["conteudo"],
                        fonte=news_item["fonte"],
                        url=news_item.get("url", ""),
                        data_publicacao=news_item.get("data_publicacao"),
                        sindicato_id=news_item.get("sindicato_id")
                    )
                    db.session.add(noticia)
            
            db.session.commit()
            
            # Registrar log
            self._log_info(f"Notícias salvas no banco de dados")
            
            return {"success": True, "message": "Notícias salvas com sucesso"}
        except Exception as e:
            db.session.rollback()
            # Registrar erro
            self._log_error(f"Erro ao salvar notícias no banco de dados: {str(e)}")
            return {"success": False, "message": f"Erro ao salvar notícias: {str(e)}"}
    
    def _log_info(self, message):
        """Registra mensagem de informação no log"""
        log = Log(tipo="web", nivel="INFO", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    def _log_error(self, message):
        """Registra mensagem de erro no log"""
        log = Log(tipo="web", nivel="ERROR", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
