from flask import Blueprint, request, render_template, jsonify
from .services import gerar_recomendacao_investimento
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('chat.html')

@main_bp.route('/gerar-recomendacao', methods=['POST'])
def gerar_recomendacao():
    try:
        dados_usuario = request.json
        logging.info("Requisição recebida: %s", dados_usuario)
        recomendacao = gerar_recomendacao_investimento(dados_usuario)
        return jsonify({"recomendacao": recomendacao})
    except Exception as e:
        logging.error(f"Erro ao gerar recomendação: {str(e)}")
        return jsonify({"error": str(e)}), 500