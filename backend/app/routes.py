from flask import Blueprint, request, jsonify, render_template
from .services import gerar_relatorio_com_verificacao, treinar_modelo_com_dados_financeiros, obter_acoes_recomendadas

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('chat.html')

@main_bp.route('/gerar-relatorio', methods=['POST'])
def gerar_relatorio():
    dados_usuario = request.json
    relatorio = gerar_relatorio_com_verificacao(dados_usuario)
    return jsonify({'relatorio': relatorio})

@main_bp.route('/recomendacoes')
def recomendacoes():
    return render_template('recomendacoes.html')

@main_bp.route('/obter-acoes', methods=['POST'])
def obter_acoes():
    dados_usuario = request.json
    acoes = obter_acoes_recomendadas(dados_usuario)
    return jsonify({'acoes': acoes})

@main_bp.route('/treinar', methods=['POST'])
def treinar():
    casos = request.json
    tickers = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]  # Adicionar mais tickers conforme necessário
    treinar_modelo_com_dados_financeiros(tickers, casos)
    return jsonify({'status': 'Treinamento concluído com sucesso'})