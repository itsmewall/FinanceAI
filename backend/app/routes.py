from flask import Blueprint, request, render_template, jsonify
from .services import gerar_relatorio_com_verificacao, treinar_ia

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('chat.html')

@main_bp.route('/gerar-relatorio', methods=['POST'])
def gerar_relatorio():
    dados_usuario = request.json
    relatorio = gerar_relatorio_com_verificacao(dados_usuario)
    return jsonify({'relatorio': relatorio})

@main_bp.route('/treinar', methods=['POST'])
def treinar():
    casos = request.json
    treinar_ia(casos)
    return jsonify({'status': 'Treinamento concluído com sucesso'})