from flask import Blueprint, request, jsonify, render_template, session
from .services import gerar_relatorio_com_verificacao, obter_acoes_recomendadas, treinar_modelo_com_dados_financeiros, carregar_modelo_usuario
import uuid
import numpy as np

# Definir tickers e casos aqui
tickers = [
    "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NFLX", "NVDA", "BABA", "V", 
    "ITUB4.SA", "BBDC4.SA", "PETR4.SA", "VALE3.SA", "ABEV3.SA", "JBSS3.SA",
    "EMBR3.SA", "WEGE3.SA", "RENT3.SA", "LREN3.SA"
]

def gerar_casos_de_treinamento(n=10000):
    casos = []
    for _ in range(n):
        idade = np.random.randint(18, 70)
        profissao = np.random.choice(['engenheiro', 'medico', 'professor', 'advogado', 'empresario', 'analista'])
        objetivo = np.random.choice(['viver de renda', 'comprar uma casa', 'educacao dos filhos', 'aposentadoria'])
        tolerancia_risco = np.random.choice(['baixa', 'media', 'alta'])
        recomendacao = np.random.choice(tickers)
        casos.append({
            'idade': idade,
            'profissao': profissao,
            'objetivo': objetivo,
            'tolerancia_risco': tolerancia_risco,
            'recomendacao': recomendacao
        })
    return casos

casos = gerar_casos_de_treinamento()

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return render_template('chat.html')

@main_bp.route('/gerar-relatorio', methods=['POST'])
def gerar_relatorio():
    dados_usuario = request.json
    user_id = session.get('user_id')
    dados_usuario['user_id'] = user_id
    carregar_modelo_usuario(user_id)
    treinar_modelo_com_dados_financeiros(user_id, tickers, casos)
    relatorio = gerar_relatorio_com_verificacao(dados_usuario)
    return jsonify({'relatorio': relatorio})

@main_bp.route('/obter-acoes', methods=['POST'])
def obter_acoes():
    dados_usuario = request.json
    dados_usuario['user_id'] = session.get('user_id')
    acoes = obter_acoes_recomendadas(dados_usuario)
    return jsonify({'acoes': acoes})

@main_bp.route('/recomendacoes')
def recomendacoes():
    return render_template('recomendacoes.html')
