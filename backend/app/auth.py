import json
import os
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logging.basicConfig(level=logging.INFO)

def carregar_usuarios():
    if os.path.exists('usuarios.json'):
        with open('usuarios.json', 'r') as f:
            return json.load(f)
    return {}

def salvar_usuarios(usuarios):
    with open('usuarios.json', 'w') as f:
        json.dump(usuarios, f)

def registrar_usuario(email, senha, nome):
    usuarios = carregar_usuarios()
    if email in usuarios:
        return False, "Usuário já registrado."
    
    user_id = str(uuid.uuid4())
    hashed_senha = generate_password_hash(senha)
    usuarios[email] = {
        'user_id': user_id,
        'nome': nome,
        'senha': hashed_senha,
    }
    salvar_usuarios(usuarios)
    return True, user_id

def autenticar_usuario(email, senha):
    usuarios = carregar_usuarios()
    if email not in usuarios:
        return False, "Usuário não encontrado."
    
    usuario = usuarios[email]
    if not check_password_hash(usuario['senha'], senha):
        return False, "Senha incorreta."
    
    return True, usuario['user_id']

def carregar_dados_usuario(user_id):
    caminho_arquivo = f"usuarios/{user_id}.json"
    if os.path.exists(caminho_arquivo):
        with open(caminho_arquivo, 'r') as f:
            return json.load(f)
    return {}

def salvar_dados_usuario(user_id, dados_usuario):
    caminho_arquivo = f"usuarios/{user_id}.json"
    os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
    with open(caminho_arquivo, 'w') as f:
        json.dump(dados_usuario, f)
    logging.info(f"Dados do usuário {user_id} salvos com sucesso.")