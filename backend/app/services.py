import openai
import logging

def gerar_recomendacao_investimento(dados_usuario):
    try:
        logging.info("Gerando recomendação de investimento para: %s", dados_usuario)

        prompt = (
            f"Nome do Usuário: {dados_usuario['nome']}\n"
            f"Idade: {dados_usuario['idade']}\n"
            f"Objetivo Financeiro: {dados_usuario['objetivo']}\n"
            f"Tolerância ao Risco: {dados_usuario['tolerancia_risco']}\n"
            f"Investimentos Atuais: {dados_usuario['investimentos']}\n"
            f"Renda Mensal: {dados_usuario['renda_mensal']}\n"
            f"Despesas Mensais: {dados_usuario['despesas_mensais']}\n"
            f"Horizonte de Tempo: {dados_usuario['horizonte_tempo']} anos\n"
            f"Experiência com Investimentos: {dados_usuario['experiencia_investimentos']}\n\n"
            "Baseado nas informações fornecidas, por favor, forneça uma recomendação detalhada e personalizada de investimento que inclua:\n"
            "- Sugestões de alocação de ativos (ações, títulos, fundos imobiliários, etc.)\n"
            "- Estratégias de investimento adequadas ao perfil e objetivos do usuário\n"
            "- Considerações sobre risco e retorno\n"
            "- Qualquer outra recomendação relevante para ajudar o usuário a alcançar seus objetivos financeiros.\n\n"
            "Resposta:"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um consultor financeiro experiente e prestativo."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        logging.info("Recomendação gerada com sucesso: %s", response.choices[0].message['content'].strip())
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logging.error(f"Erro ao chamar a API do OpenAI ou gerar recomendação: {str(e)}")
        raise e