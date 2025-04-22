import pandas as pd
import numpy as np
from openpyxl import load_workbook
from PIL import Image
import io
import os
import re
import logging
from datetime import datetime

from backend.models import Sindicato, Convencao, Clausula, db


class ExcelProcessor:
    def __init__(self):
        self.output_folder = "imagens_extraidas"
        os.makedirs(self.output_folder, exist_ok=True)

    def process_excel_file_with_images(self, file_path):
        """Processa arquivo Excel com imagens e retorna DataFrames estruturados"""
        try:
            df = pd.read_excel(file_path)
            
            # Verificar estrutura mínima necessária
            required_columns = ['SINDICATO', 'ESTADO']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(missing_columns)}")
            
            # Normalizar nomes das colunas e tratar valores ausentes
            df.columns = [col.strip().upper() for col in df.columns]
            df = df.fillna('')
            
            # Processar cada linha válida
            processed_data = []
            for idx, row in df.iterrows():
                if not row['SINDICATO'].strip():
                    continue

                # Extrair dados principais
                sindicato_data = {
                    'nome': row['SINDICATO'].strip(),
                    'estado': row.get('ESTADO', '').strip(),
                    'cnpj': row.get('CNPJ', '').strip(),
                    'cidade': row.get('CIDADE', '').strip(),
                    'categoria': row.get('CATEGORIA', '').strip(),
                    'site': row.get('SITE', '').strip(),
                    'email': row.get('EMAIL', '').strip(),
                    'telefone': row.get('TELEFONE', '').strip()
                }

                # Dados específicos do sindicato
                for col in df.columns:
                    if 'CARGO' in col or 'FUNÇÃO' in col:
                        sindicato_data['principal_cargo'] = row[col].strip() if row[col] else ''
                    elif 'PISO' in col or 'SALÁRIO' in col:
                        valor = str(row[col]).replace('R$', '').replace('.', '').replace(',', '.').strip()
                        try:
                            sindicato_data['piso_salarial'] = float(valor) if valor else None
                        except:
                            sindicato_data['piso_salarial'] = None
                    elif 'CARGA' in col or 'HORÁRIA' in col or 'JORNADA' in col:
                        valor = str(row[col]).replace('h', '').replace('hrs', '').strip()
                        try:
                            sindicato_data['carga_horaria'] = int(valor) if valor else None
                        except:
                            sindicato_data['carga_horaria'] = None

                processed_data.append(sindicato_data)

            return processed_data

        except Exception as e:
            logging.error(f"Erro ao processar Excel: {str(e)}")
            raise

    def process_excel(self, arquivo_id):
        """Processa um arquivo Excel e salva os dados no banco"""
        try:
            arquivo = Arquivo.query.get(arquivo_id)
            if not arquivo:
                raise ValueError(f"Arquivo não encontrado: {arquivo_id}")

            # Processar dados do Excel
            dados_processados = self.process_excel_file_with_images(arquivo.caminho)
            
            if not dados_processados:
                raise ValueError("Nenhum dado válido encontrado no arquivo Excel")

            # Salvar no banco de dados
            for dados in dados_processados:
                # Verificar se o sindicato já existe
                sindicato = Sindicato.query.filter_by(nome=dados['nome']).first()
                
                if not sindicato:
                    sindicato = Sindicato(**dados)
                    db.session.add(sindicato)
                else:
                    # Atualizar dados existentes
                    for key, value in dados.items():
                        if value:  # Só atualiza se o valor não for vazio
                            setattr(sindicato, key, value)
            
            # Marcar arquivo como processado
            arquivo.processado = True
            db.session.commit()
            
            # Log de sucesso
            self._log_info(f"Excel processado com sucesso: {len(dados_processados)} sindicatos")
            
            return {
                "success": True,
                "message": f"Arquivo processado com sucesso. {len(dados_processados)} sindicatos encontrados.",
                "data": dados_processados
            }

        except Exception as e:
            db.session.rollback()
            error_msg = f"Erro ao processar Excel: {str(e)}"
            self._log_error(error_msg)
            return {"success": False, "message": error_msg}

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
