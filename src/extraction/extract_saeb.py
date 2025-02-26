"""
Extração de dados SAEB.
"""
import os
import pandas as pd
import argparse
from datetime import datetime
import logging

from src.extraction.bigquery_connector import BigQueryConnector
from src.utils.config import Config
from src.utils.logging_utils import setup_logger

logger = setup_logger("extract_saeb")

class SAEBExtractor:
    """
    Classe para extração de dados do SAEB no BigQuery.
    """
    
    def __init__(self, config):
        """
        Inicializa o extrator.
        
        Args:
            config (Config)
        """
        self.config = config
        self.connector = BigQueryConnector(
            credentials_path=config.get("bigquery.credentials_path"),
            project_id=config.get("bigquery.project_id")
        )
        self.output_dir = config.get("extraction.output_dir")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_saeb_aluno_ef_9ano(self, anos=None, limit=None):
        """
        Extrai dados do 9º ano.
        
        Args:
            anos (list, optional)
            limit (int, optional)
        
        Returns:
            pandas.DataFrame: DF combinado com os dados extraídos
        """
        combined_df = pd.DataFrame()
        
        # Se a extração for feita por anos, extrai cada ano separadamente.
        if anos:
            for ano in anos:
                logger.info(f"Extraindo dados por ano {ano}")
                df = self.connector.extract_saeb_data(ano=ano, limit=limit)
                df['ano'] = ano  
                combined_df = pd.concat([combined_df, df], ignore_index=True)
        else:
            # Extrai todos os anos de uma vez.
            logger.info("Extracting all SAEB 9th grade data")
            combined_df = self.connector.extract_saeb_data(limit=limit)
        
        logger.info(f"{len(combined_df)} linhas retornadas")
        return combined_df
    
    def extract_dictionary(self):
        """
        Extrai dados do dicionario SAEB.
        
        Returns:
            pandas.DataFrame: DF com dados do dicionario.
        """
        logger.info("Extraindo dados do dicionario SAEB")
        dictionary_df = self.connector.extract_dictionary()
        logger.info(f"{len(dictionary_df)} linhas retornadas do dicionario")
        return dictionary_df
    
    def extract_and_save(self, anos=None, limit=None):
        """
        Extrai e salva os dados.
        
        Args:
            anos (list, optional)
            limit (int, optional)
        """
        # Dados de estudantes
        saeb_df = self.extract_saeb_aluno_ef_9ano(anos, limit)
        
        # Dados do dicionario
        dictionary_df = self.extract_dictionary()
        
        # Adiciona timestamp no nome do arquivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salva os dados extraídos
        saeb_output_path = os.path.join(self.output_dir, f"saeb_aluno_ef_9ano_{timestamp}.parquet")
        dictionary_output_path = os.path.join(self.output_dir, f"saeb_dictionary_{timestamp}.parquet")
        
        saeb_df.to_parquet(saeb_output_path, index=False)
        dictionary_df.to_parquet(dictionary_output_path, index=False)
        
        logger.info(f"Dados do SAEB salvos em {saeb_output_path}")
        logger.info(f"Dados do dicionario salvos em {dictionary_output_path}")
        
        return {
            "saeb_data_path": saeb_output_path,
            "dictionary_path": dictionary_output_path
        }
    
    def close(self):
        """Encerra conexão."""
        self.connector.close()


def main():
    """Main entry point para extração dos dados."""
    parser = argparse.ArgumentParser(description="Extrai dados do SAEB no BigQuery")
    parser.add_argument("--config", "-c", type=str, default="config.yml", help="Path do arquivo de configuração")
    parser.add_argument("--years", "-y", type=int, nargs="+", help="Anos para extração (ex: 2017 2019 2021)")
    parser.add_argument("--limit", "-l", type=int, help="Limite de linhas por ano")
    args = parser.parse_args()
    
    config = Config(args.config)
    
    extractor = SAEBExtractor(config)
    
    try:
        output_paths = extractor.extract_and_save(anos=args.years, limit=args.limit)
        
        print(f"DADOS SAEB: {output_paths['saeb_data_path']}")
        print(f"Dicionario: {output_paths['dictionary_path']}")
        
    except Exception as e:
        logger.error(f"Falha na extração: {str(e)}")
        raise
    finally:
        extractor.close()


if __name__ == "__main__":
    main()
