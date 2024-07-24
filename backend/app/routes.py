from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from .services import (
    gerar_relatorio_com_verificacao,
    obter_acoes_recomendadas,
    carregar_analises_csv,
    salvar_dados_usuario,
    carregar_modelo_usuario,
    treinar_modelo_com_dados_financeiros
)
from .auth import registrar_usuario, autenticar_usuario, carregar_dados_usuario

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('login.html')

@main_bp.route('/registrar', methods=['POST'])
def registrar():
    dados = request.json
    email = dados.get('email')
    senha = dados.get('senha')
    nome = dados.get('nome')
    sucesso, resposta = registrar_usuario(email, senha, nome)
    if sucesso:
        return jsonify({'message': 'Usuário registrado com sucesso.', 'user_id': resposta}), 201
    else:
        return jsonify({'message': resposta}), 400

@main_bp.route('/login', methods=['POST'])
def login():
    dados = request.json
    email = dados.get('email')
    senha = dados.get('senha')
    sucesso, resposta = autenticar_usuario(email, senha)
    if sucesso:
        user_id = resposta
        dados_usuario = carregar_dados_usuario(user_id)
        if dados_usuario:
            return jsonify({'message': 'Login bem-sucedido.', 'user_id': user_id, 'dados_usuario': dados_usuario}), 200
        else:
            return jsonify({'message': 'Login bem-sucedido. Complete seu perfil.', 'user_id': user_id}), 200
    else:
        return jsonify({'message': resposta}), 400

@main_bp.route('/completar-perfil', methods=['POST'])
def completar_perfil():
    dados_usuario = request.json
    user_id = dados_usuario.get('user_id')
    salvar_dados_usuario(user_id, dados_usuario)
    
    # Carregar análises do CSV
    df_analises = carregar_analises_csv('app/indicadores_financeiros_atualizados.csv')  # Atualize o caminho do CSV
    
    # Treinar o modelo de investimento
    treinar_modelo_com_dados_financeiros(user_id, [dados_usuario], df_analises)
    
    # Carregar o modelo do usuário
    carregar_modelo_usuario(user_id)
    
    # Gerar relatório e perfil de investidor
    relatorio, perfil_investidor = gerar_relatorio_com_verificacao(dados_usuario, df_analises)
    
    return jsonify({'relatorio': relatorio, 'perfil_investidor': perfil_investidor})

@main_bp.route('/chat')
def chat():
    return render_template('chat.html')

@main_bp.route('/recomendacoes')
def recomendacoes():
    return render_template('recomendacoes.html')

@main_bp.route('/obter-acoes', methods=['POST'])
def obter_acoes():
    dados_usuario = request.json
    
    # Carregar análises do CSV
    df_analises = carregar_analises_csv('app/indicadores_financeiros_atualizados.csv')  # Atualize o caminho do CSV
    
    acoes = obter_acoes_recomendadas(dados_usuario, df_analises)
    
    return jsonify({'acoes': acoes})
