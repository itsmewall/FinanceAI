from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv
import os

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Obter a chave da API do OpenAI a partir das variáveis de ambiente
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/gerar-recomendacao', methods=['POST'])
def gerar_recomendacao():
    dados_usuario = request.json
    recomendacao = gerar_recomendacao_investimento(dados_usuario)
    return jsonify(recomendacao)

def gerar_recomendacao_investimento(dados_usuario):
    prompt = (
        f"Usuário: {dados_usuario['nome']}\n"
        f"Idade: {dados_usuario['idade']}\n"
        f"Objetivo financeiro: {dados_usuario['objetivo']}\n"
        f"Tolerância ao risco: {dados_usuario['tolerancia_risco']}\n"
        f"Investimentos atuais: {dados_usuario['investimentos']}\n"
        f"Renda mensal: {dados_usuario['renda_mensal']}\n"
        f"Despesas mensais: {dados_usuario['despesas_mensais']}\n"
        "Crie um plano de investimento personalizado para este usuário."
    )

    resposta = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        max_tokens=500
    )

    return resposta.choices[0].text.strip()

if __name__ == '__main__':
    app.run(debug=True)