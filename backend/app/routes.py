from flask import Blueprint, request, render_template, redirect, url_for
from .services import gerar_recomendacao_investimento
import logging

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/gerar-recomendacao', methods=['POST'])
def gerar_recomendacao():
    try:
        dados_usuario = request.form.to_dict()
        logging.info("Requisição recebida: %s", dados_usuario)
        recomendacao = gerar_recomendacao_investimento(dados_usuario)
        return render_template('resultado.html', recomendacao=recomendacao)
    except Exception as e:
        logging.error(f"Erro ao gerar recomendação: {str(e)}")
        return render_template('resultado.html', recomendacao=f"Erro: {str(e)}")