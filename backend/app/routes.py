from flask import Blueprint, request, jsonify, render_template
from .services import (
    gerar_relatorio_com_verificacao,
    treinar_modelo_com_dados_financeiros,
    obter_acoes_recomendadas,
    carregar_analises_csv,
    salvar_dados_usuario
)
import uuid
import numpy as np

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('chat.html')

@main_bp.route('/gerar-relatorio', methods=['POST'])
def gerar_relatorio():
    dados_usuario = request.json
    user_id = str(uuid.uuid4())
    dados_usuario['user_id'] = user_id
    
    # Salvar os dados do usuário
    salvar_dados_usuario(dados_usuario)
    
    # Carregar análises do CSV
    df_analises = carregar_analises_csv('indicadores_financeiros_atualizados.csv')
    
    # Gerar relatório e perfil de investidor
    relatorio, perfil_investidor = gerar_relatorio_com_verificacao(dados_usuario, df_analises)
    
    return jsonify({'relatorio': relatorio, 'perfil_investidor': perfil_investidor})

@main_bp.route('/recomendacoes')
def recomendacoes():
    return render_template('recomendacoes.html')

@main_bp.route('/obter-acoes', methods=['POST'])
def obter_acoes():
    dados_usuario = request.json
    
    # Carregar análises do CSV
    df_analises = carregar_analises_csv('indicadores_financeiros_atualizados.csv')
    
    acoes = obter_acoes_recomendadas(dados_usuario, df_analises)
    
    return jsonify({'acoes': acoes})
