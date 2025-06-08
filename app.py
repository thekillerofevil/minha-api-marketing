# app.py
# Este é o arquivo principal da nossa API.
# Ele usa o Flask, um micro-framework web para Python.

import os
import threading
import time
import schedule
import random
from flask import Flask, jsonify, request
import google.generativeai as genai

# --- Configuração Inicial ---

# No Render, você vai configurar isso como uma "Environment Variable".
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    # Se a chave não estiver configurada, a API não vai iniciar.
    # Isso é uma medida de segurança.
    print("A variável de ambiente GOOGLE_API_KEY não foi configurada.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

app = Flask(__name__)

# --- Lógica Principal da Geração de Conteúdo ---

def gerar_post_instagram(tema: str):
    """
    Função que chama a API Gemini para criar o conteúdo do post.
    """
    prompt = f"""
    Aja como um especialista em social media para uma agência de marketing digital.
    Crie um post completo para o Instagram sobre o seguinte tema: '{tema}'.
    O post deve ser otimizado para engajamento.

    Por favor, gere uma resposta no formato JSON contendo os seguintes campos:
    - "legenda": Um texto cativante e informativo para a legenda, com quebras de linha usando '\\n'.
    - "hashtags": Uma string com as 10 melhores hashtags para este post, separadas por espaço.
    - "sugestao_imagem": Uma descrição detalhada para uma imagem que combine com o post, para ser usada em uma ferramenta de IA de geração de imagem como Midjourney ou DALL-E.
    """
    try:
        response = model.generate_content(prompt)
        # Limpa a saída para garantir que é um JSON válido
        json_response = response.text.strip().replace("```json", "").replace("```", "")
        return json_response
    except Exception as e:
        print(f"Erro ao gerar conteúdo: {e}")
        return None

# --- Endpoints da API (Para uso manual) ---

@app.route('/')
def index():
    return "<h1>API de Marketing com Gemini está no ar!</h1><p>Use o endpoint /gerar-post para criar conteúdo.</p>"

@app.route('/gerar-post', methods=['POST'])
def endpoint_gerar_post():
    data = request.get_json()
    if not data or 'tema' not in data:
        return jsonify({"erro": "O campo 'tema' é obrigatório."}), 400

    tema = data['tema']
    conteudo_post = gerar_post_instagram(tema)

    if conteudo_post:
        return conteudo_post, 200, {'Content-Type': 'application/json; charset=utf-8'}
    else:
        return jsonify({"erro": "Não foi possível gerar o conteúdo."}), 500

# --- Lógica de Automação (Agendamento) ---

TEMAS_MARKETING = [
    "A importância do SEO para pequenas empresas",
    "Como criar um funil de vendas que converte",
    "5 dicas para anúncios eficazes no Instagram",
    "Marketing de conteúdo: como começar?",
    "O futuro do marketing com inteligência artificial"
]

def job_agendado():
    print(">>> Executando tarefa agendada: Gerando post do dia...")
    tema_aleatorio = random.choice(TEMAS_MARKETING)

    conteudo_gerado = gerar_post_instagram(tema_aleatorio)

    if conteudo_gerado:
        print("--- Conteúdo Gerado com Sucesso ---")
        print(conteudo_gerado)
        print("-----------------------------------")
    else:
        print("Falha ao gerar conteúdo agendado.")

def run_scheduler():
    schedule.every().day.at("09:00").do(job_agendado)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    if GOOGLE_API_KEY:
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    else:
        print("Aplicação não iniciada. A chave da API do Google não foi encontrada.")
