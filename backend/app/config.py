import logging
from dotenv import load_dotenv
import os
import openai

def load_config(app):
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Configurações da API OpenAI
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logging.error("A chave da API OpenAI não foi encontrada no arquivo .env")
    else:
        app.config['OPENAI_API_KEY'] = api_key
        openai.api_key = api_key
    
    # Configuração do logger
    logging.basicConfig(level=logging.INFO)