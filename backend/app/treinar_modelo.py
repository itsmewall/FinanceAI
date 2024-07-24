import json
import logging
import numpy as np
from services import treinar_modelo_com_dados_financeiros, carregar_modelo_usuario

logging.basicConfig(level=logging.INFO)

# Carregar dados dos tickers e casos de treinamento
with open('dados_financeiros.json', 'r') as f:
    dados_financeiros = json.load(f)

def gerar_casos_de_treinamento(n=10000):
    casos = []
    for _ in range(n):
        idade = np.random.randint(18, 70)
        profissao = np.random.choice(['engenheiro', 'medico', 'professor', 'advogado', 'empresario', 'analista'])
        objetivo = np.random.choice(['viver de renda', 'comprar uma casa', 'educacao dos filhos', 'aposentadoria'])
        tolerancia_risco = np.random.choice(['baixa', 'media', 'alta'])
        recomendacao = np.random.choice([d['ticker'] for d in dados_financeiros])
        casos.append({
            'idade': idade,
            'profissao': profissao,
            'objetivo': objetivo,
            'tolerancia_risco': tolerancia_risco,
            'recomendacao': recomendacao
        })
    return casos

casos = gerar_casos_de_treinamento()

# Definir ID de usuário para teste
user_id = 'test_user'

# Treinar modelo com dados financeiros
treinar_modelo_com_dados_financeiros(user_id, [d['ticker'] for d in dados_financeiros], casos)

# Carregar modelo treinado para verificar
carregar_modelo_usuario(user_id)