import openai
import logging
from random import randint
import yfinance as yf

def obter_dados_acao(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    return data

def gerar_relatorio_investidor(dados_usuario):
    try:
        logging.info("Gerando relatório de investimento para: %s", dados_usuario)

        # Lógica de personalização para recomendações
        idade = int(dados_usuario.get('idade', 0))
        profissao = dados_usuario.get('profissao', '').lower()
        objetivo = dados_usuario.get('objetivo', '').lower()
        investimentos = dados_usuario.get('investimentos', '')

        recomendacoes = []

        # Recomendações baseadas na idade
        if idade < 30:
            recomendacoes.append("Como você é jovem, investir em ações de crescimento pode ser uma boa escolha.")
        elif idade < 50:
            recomendacoes.append("Com a meia-idade, diversificar seus investimentos entre ações e títulos pode ser uma boa estratégia.")
        else:
            recomendacoes.append("Como você está mais perto da aposentadoria, investimentos mais conservadores como títulos e fundos imobiliários são recomendados.")

        # Recomendações baseadas na profissão
        if 'engenheiro' in profissao:
            recomendacoes.append("Como engenheiro, você pode considerar investir em empresas de tecnologia e inovação.")
        elif 'médico' in profissao:
            recomendacoes.append("Como médico, você pode investir em fundos de saúde e biotecnologia.")
        else:
            recomendacoes.append("Independentemente da sua profissão, diversificar é a chave para um portfólio de investimentos saudável.")

        # Recomendações baseadas no objetivo financeiro
        if 'aposentadoria' in objetivo:
            recomendacoes.append("Para a aposentadoria, considere investir em um plano de previdência privada e em títulos de longo prazo.")
        elif 'casa' in   objetivo:
            recomendacoes.append("Para comprar uma casa, investimentos de médio prazo como CDBs e LCIs são recomendados.")
        else:
            recomendacoes.append("Para outros objetivos, mantenha uma carteira diversificada para balancear risco e retorno.")

        # Adicionando dados das ações ao relatório
        if investimentos:
            tickers = [ticker.strip() for ticker in investimentos.split(',')]
            for ticker in tickers:
                dados_acao = obter_dados_acao(ticker)
                if not dados_acao.empty:
                    preco_atual = dados_acao['Close'].iloc[-1]
                    recomendacoes.append(f"Ação {ticker.upper()}: Preço Atual: ${preco_atual:.2f}")

        prompt = (
            f"Nome: {dados_usuario.get('nome', '')}\n"
            f"Idade: {dados_usuario.get('idade', '')}\n"
            f"Estado: {dados_usuario.get('estado', '')}\n"
            f"Profissão: {dados_usuario.get('profissao', '')}\n"
            f"Estado Civil: {dados_usuario.get('estado_civil', '')}\n"
            f"Filhos: {dados_usuario.get('filhos', '')}\n"
            f"Objetivo Financeiro: {dados_usuario.get('objetivo', '')}\n"
            f"Tolerância ao Risco: {dados_usuario.get('tolerancia_risco', '')}\n"
            f"Investimentos Atuais: {dados_usuario.get('investimentos', '')}\n"
            f"Renda Mensal: {dados_usuario.get('renda_mensal', '')}\n"
            f"Despesas Mensais: {dados_usuario.get('despesas_mensais', '')}\n"
            f"Horizonte de Tempo: {dados_usuario.get('horizonte_tempo', '')} anos\n"
            f"Experiência com Investimentos: {dados_usuario.get('experiencia_investimentos', '')}\n\n"
            "Baseado nas informações fornecidas, por favor, forneça um relatório detalhado e personalizado do perfil de investidor. "
            "Inclua recomendações de investimentos adequados, estratégias financeiras, e qualquer outra informação relevante para ajudar no planejamento financeiro. "
            "Use um tom sarcástico e humorístico, mas sem exagerar e perder o tom, como o Bruno Perini faria, e mantenha as respostas curtas e diretas ao ponto, mas com recomendações.\n\n"
            "Resposta:"
        )

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um consultor financeiro experiente, sarcástico e com humor como o Bruno Perini."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        relatorio = response.choices[0].message['content'].strip()

        # Adicionando recomendações personalizadas ao relatório
        for recomendacao in recomendacoes:
            relatorio += f"\n- {recomendacao}"

        logging.info("Relatório gerado com sucesso: %s", relatorio)
        return relatorio
    except Exception as e:
        logging.error(f"Erro ao chamar a API do OpenAI ou gerar relatório: {str(e)}")
        raise e

def verificar_consistencia_respostas(dados_usuario):
    for key, value in dados_usuario.items():
        if not value:
            return False, f"O campo '{key}' está vazio. Por favor, preencha todas as informações."
    return True, ""

def gerar_relatorio_com_verificacao(dados_usuario):
    consistencia, mensagem = verificar_consistencia_respostas(dados_usuario)
    if not consistencia:
        return mensagem
    return gerar_relatorio_investidor(dados_usuario)

# Função para treinar a IA com diversos casos
def treinar_ia(casos):
    logging.info("Treinando a IA com casos: %s", casos)
    for caso in casos:
        gerar_relatorio_investidor(caso)

def obter_acoes_recomendadas(dados_usuario):
    try:
        tickers = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
        acoes = []
        for ticker in tickers:
            dados_acao = obter_dados_acao(ticker)
            if not dados_acao.empty:
                preco_atual = dados_acao['Close'].iloc[-1]
                acoes.append({
                    'nome': ticker,
                    'ticker': ticker,
                    'preco_atual': preco_atual,
                    'descricao': f"Recomendação baseada no perfil de {dados_usuario['nome']}."
                })
        return acoes
    except Exception as e:
        logging.error(f"Erro ao obter ações recomendadas: {str(e)}")
        raise e
