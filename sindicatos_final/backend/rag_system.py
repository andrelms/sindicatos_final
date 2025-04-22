"""
Sistema RAG (Retrieval Augmented Generation) aprimorado para consultas baseadas em documentos
"""
import os
import re
import json
import logging
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from backend.models import db, Sindicato, Convencao, Clausula, Log
from backend.gemini_integration import GeminiAPI
from backend.pdf_processor import PDFProcessor

# Garantir que os recursos do NLTK estejam disponíveis
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class RAGSystem:
    """Sistema RAG aprimorado para consultas baseadas em documentos"""
    
    def __init__(self):
        """Inicializa o sistema RAG"""
        self.gemini_api = GeminiAPI()
        self.pdf_processor = PDFProcessor()
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words=stopwords.words('portuguese')
        )
        self.document_vectors = None
        self.documents = []
        self.document_sources = []
        self.document_metadata = []
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("rag_system.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("RAGSystem")
    
    def index_all_documents(self) -> Dict[str, Any]:
        """Indexa todos os documentos disponíveis no sistema"""
        try:
            self._log_info("Iniciando indexação de todos os documentos")
            
            # Limpar índices existentes
            self.documents = []
            self.document_sources = []
            self.document_metadata = []
            
            # 1. Indexar convenções coletivas
            self._index_conventions()
            
            # 2. Indexar cláusulas
            self._index_clauses()
            
            # 3. Criar vetores TF-IDF
            if self.documents:
                self.document_vectors = self.vectorizer.fit_transform(self.documents)
                self._log_info(f"Vetorização concluída: {self.document_vectors.shape[0]} documentos, {self.document_vectors.shape[1]} características")
            else:
                self._log_warning("Nenhum documento encontrado para indexação")
            
            return {
                "success": True,
                "message": f"Indexação concluída: {len(self.documents)} documentos indexados",
                "documents_count": len(self.documents),
                "features_count": self.document_vectors.shape[1] if self.document_vectors is not None else 0
            }
        except Exception as e:
            self._log_error(f"Erro ao indexar documentos: {str(e)}")
            return {"success": False, "message": f"Erro ao indexar documentos: {str(e)}"}
    
    def _index_conventions(self) -> None:
        """Indexa todas as convenções coletivas"""
        try:
            conventions = Convencao.query.all()
            self._log_info(f"Indexando {len(conventions)} convenções coletivas")
            
            for convention in conventions:
                # Verificar se o arquivo existe
                if not convention.arquivo_path or not os.path.exists(convention.arquivo_path):
                    self._log_warning(f"Arquivo não encontrado para convenção ID {convention.id}: {convention.arquivo_path}")
                    continue
                
                # Extrair texto do PDF
                try:
                    pdf_text = self.pdf_processor.extract_text_from_pdf(convention.arquivo_path)
                    
                    # Dividir o texto em chunks para melhor recuperação
                    chunks = self._split_text_into_chunks(pdf_text, chunk_size=1000, overlap=200)
                    
                    # Adicionar cada chunk como um documento separado
                    for i, chunk in enumerate(chunks):
                        self.documents.append(chunk)
                        self.document_sources.append({
                            "type": "convention",
                            "id": convention.id,
                            "title": convention.titulo,
                            "year": convention.ano,
                            "union_id": convention.sindicato_id,
                            "file_path": convention.arquivo_path,
                            "chunk_id": i,
                            "total_chunks": len(chunks)
                        })
                        self.document_metadata.append({
                            "title": f"{convention.titulo} (Parte {i+1}/{len(chunks)})",
                            "source": f"Convenção Coletiva {convention.ano}",
                            "union": Sindicato.query.get(convention.sindicato_id).nome if convention.sindicato_id else "Desconhecido",
                            "page_range": f"Parte {i+1} de {len(chunks)}"
                        })
                    
                    self._log_info(f"Convenção ID {convention.id} indexada: {len(chunks)} chunks")
                except Exception as e:
                    self._log_error(f"Erro ao processar convenção ID {convention.id}: {str(e)}")
        except Exception as e:
            self._log_error(f"Erro ao indexar convenções: {str(e)}")
    
    def _index_clauses(self) -> None:
        """Indexa todas as cláusulas de convenções"""
        try:
            clauses = Clausula.query.all()
            self._log_info(f"Indexando {len(clauses)} cláusulas")
            
            for clause in clauses:
                # Verificar se há conteúdo
                if not clause.conteudo:
                    continue
                
                # Adicionar a cláusula como documento
                self.documents.append(clause.conteudo)
                
                # Obter informações da convenção
                convention = Convencao.query.get(clause.convencao_id)
                
                self.document_sources.append({
                    "type": "clause",
                    "id": clause.id,
                    "title": clause.titulo,
                    "number": clause.numero,
                    "convention_id": clause.convencao_id,
                    "union_id": convention.sindicato_id if convention else None
                })
                
                self.document_metadata.append({
                    "title": f"Cláusula {clause.numero}: {clause.titulo}",
                    "source": f"Convenção Coletiva {convention.ano if convention else 'Desconhecida'}",
                    "union": Sindicato.query.get(convention.sindicato_id).nome if convention and convention.sindicato_id else "Desconhecido",
                    "page_range": "Cláusula específica"
                })
            
            self._log_info(f"Indexação de cláusulas concluída")
        except Exception as e:
            self._log_error(f"Erro ao indexar cláusulas: {str(e)}")
    
    def query(self, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Realiza uma consulta no sistema RAG
        
        Args:
            query_text: Texto da consulta
            top_k: Número de documentos relevantes a recuperar
            
        Returns:
            Dicionário com resultados da consulta
        """
        try:
            self._log_info(f"Processando consulta: {query_text}")
            
            # Verificar se há documentos indexados
            if not self.documents or self.document_vectors is None:
                self._log_warning("Nenhum documento indexado. Realizando indexação...")
                self.index_all_documents()
                
                if not self.documents or self.document_vectors is None:
                    return {
                        "success": False,
                        "message": "Não há documentos indexados para consulta",
                        "answer": "Não foi possível responder à consulta pois não há documentos indexados no sistema."
                    }
            
            # Vetorizar a consulta
            query_vector = self.vectorizer.transform([query_text])
            
            # Calcular similaridade com todos os documentos
            similarities = cosine_similarity(query_vector, self.document_vectors).flatten()
            
            # Obter os índices dos top_k documentos mais similares
            top_indices = similarities.argsort()[-top_k:][::-1]
            
            # Filtrar apenas documentos com similaridade mínima
            filtered_indices = [idx for idx in top_indices if similarities[idx] > 0.1]
            
            if not filtered_indices:
                return {
                    "success": False,
                    "message": "Nenhum documento relevante encontrado para a consulta",
                    "answer": "Não foram encontrados documentos relevantes para responder à sua consulta."
                }
            
            # Construir contexto para o Gemini
            context = self._build_context_from_documents(filtered_indices, similarities)
            
            # Gerar resposta com o Gemini
            prompt = f"""
            Você é um assistente especializado em convenções coletivas e acordos sindicais.
            Responda à seguinte consulta com base APENAS nas informações fornecidas no contexto abaixo.
            Se a informação não estiver no contexto, diga que não possui essa informação.
            Sempre cite a fonte específica (nome do sindicato, ano da convenção, número da cláusula) para cada informação.
            
            CONTEXTO:
            {context}
            
            CONSULTA:
            {query_text}
            
            RESPOSTA (em português):
            """
            
            answer = self.gemini_api.generate_text(prompt)
            
            # Registrar a consulta
            self._log_info(f"Consulta processada: {len(filtered_indices)} documentos relevantes encontrados")
            
            # Preparar fontes para retorno
            sources = [
                {
                    "title": self.document_metadata[idx]["title"],
                    "source": self.document_metadata[idx]["source"],
                    "union": self.document_metadata[idx]["union"],
                    "similarity": float(similarities[idx]),
                    "content_preview": self.documents[idx][:200] + "..." if len(self.documents[idx]) > 200 else self.documents[idx],
                    "metadata": self.document_sources[idx]
                }
                for idx in filtered_indices
            ]
            
            return {
                "success": True,
                "query": query_text,
                "answer": answer,
                "sources": sources,
                "total_sources": len(sources)
            }
        except Exception as e:
            self._log_error(f"Erro ao processar consulta: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao processar consulta: {str(e)}",
                "query": query_text,
                "answer": "Ocorreu um erro ao processar sua consulta. Por favor, tente novamente."
            }
    
    def _build_context_from_documents(self, indices: List[int], similarities: np.ndarray) -> str:
        """Constrói o contexto a partir dos documentos recuperados"""
        context_parts = []
        
        for i, idx in enumerate(indices):
            source_info = f"[Fonte: {self.document_metadata[idx]['source']}, {self.document_metadata[idx]['union']}, {self.document_metadata[idx]['title']}]"
            context_parts.append(f"--- Documento {i+1} (Relevância: {similarities[idx]:.2f}) {source_info} ---\n{self.documents[idx]}\n")
        
        return "\n".join(context_parts)
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Divide um texto em chunks com sobreposição"""
        words = word_tokenize(text, language='portuguese')
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            
            # Se chegou ao final do texto, parar
            if i + chunk_size >= len(words):
                break
        
        return chunks
    
    def index_specific_document(self, document_path: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Indexa um documento específico
        
        Args:
            document_path: Caminho para o documento
            metadata: Metadados do documento
            
        Returns:
            Resultado da indexação
        """
        try:
            self._log_info(f"Indexando documento específico: {document_path}")
            
            # Verificar se o arquivo existe
            if not os.path.exists(document_path):
                return {"success": False, "message": f"Arquivo não encontrado: {document_path}"}
            
            # Extrair texto do PDF
            if document_path.lower().endswith('.pdf'):
                document_text = self.pdf_processor.extract_text_from_pdf(document_path)
            else:
                with open(document_path, 'r', encoding='utf-8') as f:
                    document_text = f.read()
            
            # Dividir o texto em chunks
            chunks = self._split_text_into_chunks(document_text)
            
            # Se não houver documentos indexados ainda, inicializar o vectorizer
            if not self.documents:
                self.documents = chunks
                self.document_vectors = self.vectorizer.fit_transform(self.documents)
            else:
                # Adicionar os novos chunks
                old_doc_count = len(self.documents)
                self.documents.extend(chunks)
                
                # Recriar os vetores
                self.document_vectors = self.vectorizer.fit_transform(self.documents)
            
            # Adicionar metadados
            for i in range(len(chunks)):
                self.document_sources.append({
                    "type": metadata.get("type", "custom"),
                    "id": metadata.get("id", f"custom_{len(self.document_sources)}"),
                    "file_path": document_path,
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    **metadata
                })
                
                self.document_metadata.append({
                    "title": f"{metadata.get('title', 'Documento')} (Parte {i+1}/{len(chunks)})",
                    "source": metadata.get("source", "Documento personalizado"),
                    "union": metadata.get("union", "N/A"),
                    "page_range": f"Parte {i+1} de {len(chunks)}"
                })
            
            self._log_info(f"Documento indexado: {len(chunks)} chunks")
            
            return {
                "success": True,
                "message": f"Documento indexado com sucesso: {len(chunks)} chunks",
                "chunks_count": len(chunks)
            }
        except Exception as e:
            self._log_error(f"Erro ao indexar documento: {str(e)}")
            return {"success": False, "message": f"Erro ao indexar documento: {str(e)}"}
    
    def clear_index(self) -> Dict[str, Any]:
        """Limpa o índice de documentos"""
        try:
            self.documents = []
            self.document_sources = []
            self.document_metadata = []
            self.document_vectors = None
            
            self._log_info("Índice de documentos limpo")
            
            return {"success": True, "message": "Índice de documentos limpo com sucesso"}
        except Exception as e:
            self._log_error(f"Erro ao limpar índice: {str(e)}")
            return {"success": False, "message": f"Erro ao limpar índice: {str(e)}"}
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do índice"""
        try:
            # Contar tipos de documentos
            doc_types = {}
            for source in self.document_sources:
                doc_type = source.get("type", "unknown")
                doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # Contar por sindicato
            union_counts = {}
            for i, source in enumerate(self.document_sources):
                if "union_id" in source and source["union_id"]:
                    union_id = source["union_id"]
                    union_name = self.document_metadata[i]["union"]
                    key = f"{union_name} (ID: {union_id})"
                    union_counts[key] = union_counts.get(key, 0) + 1
            
            return {
                "success": True,
                "total_documents": len(self.documents),
                "document_types": doc_types,
                "unions_distribution": union_counts,
                "vectorizer_features": self.document_vectors.shape[1] if self.document_vectors is not None else 0,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            self._log_error(f"Erro ao obter estatísticas do índice: {str(e)}")
            return {"success": False, "message": f"Erro ao obter estatísticas: {str(e)}"}
    
    def _log_info(self, message: str) -> None:
        """Registra mensagem de informação no log"""
        self.logger.info(message)
        log = Log(tipo="rag", nivel="INFO", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    def _log_warning(self, message: str) -> None:
        """Registra mensagem de aviso no log"""
        self.logger.warning(message)
        log = Log(tipo="rag", nivel="WARNING", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    def _log_error(self, message: str) -> None:
        """Registra mensagem de erro no log"""
        self.logger.error(message)
        log = Log(tipo="rag", nivel="ERROR", mensagem=message)
        db.session.add(log)
        try:
            db.session.commit()
        except:
            db.session.rollback()
