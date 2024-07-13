import openai
import logging

def gerar_recomendacao_investimento(dados_usuario):
    try:
        logging.info("Gerando recomendação de investimento para: %s", dados_usuario)

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

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente financeiro."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        logging.info("Recomendação gerada com sucesso: %s", response.choices[0].message['content'].strip())
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.error(f"Erro ao chamar a API do OpenAI ou gerar recomendação: {str(e)}")
        raise e