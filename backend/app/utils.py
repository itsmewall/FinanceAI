from dotenv import load_dotenv
import os
import openai

def load_config(app):
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Configurações da API OpenAI
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    openai.api_key = app.config['OPENAI_API_KEY']