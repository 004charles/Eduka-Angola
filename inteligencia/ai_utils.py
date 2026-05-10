import google.generativeai as genai
import json
import os
from django.conf import settings

def gerar_exercicios_ia(aula_titulo, aula_descricao):
    """
    Usa o Google Gemini para gerar 3 questões de múltipla escolha baseadas no conteúdo da aula.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key or api_key == "":
        return {"error": "Chave de API do Gemini não configurada no .env ou settings.py"}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = f"""
        Você é um assistente educacional especializado em criar exercícios de fixação para a plataforma EdukAngola.
        Com base no título e na descrição da aula abaixo, crie exatamente 3 perguntas de múltipla escolha em Português (Angola/Portugal).
        Cada pergunta deve ter 4 alternativas, sendo exatamente uma correta.
        
        REGRAS:
        1. Responda APENAS com um objeto JSON válido.
        2. Não inclua Markdown, explicações fora do JSON ou blocos de código.
        3. O formato deve ser rigorosamente este:
        {{
            "questoes": [
                {{
                    "texto": "Texto da pergunta...",
                    "explicacao": "Explicação curta do porquê esta é a resposta correta.",
                    "alternativas": [
                        {{"texto": "Opção A", "correta": true}},
                        {{"texto": "Opção B", "correta": false}},
                        {{"texto": "Opção C", "correta": false}},
                        {{"texto": "Opção D", "correta": false}}
                    ]
                }}
            ]
        }}

        CONTEÚDO DA AULA:
        Título: {aula_titulo}
        Descrição: {aula_descricao}
        """

        response = model.generate_content(prompt)
        text = response.text
        
        # Limpeza básica de possíveis marcações de markdown do modelo
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        data = json.loads(text.strip())
        return data
        
    except Exception as e:
        return {"error": f"Erro na comunicação com a IA: {str(e)}"}
def gerar_resumo_ia(aula_titulo, aula_descricao):
    """
    Gera um resumo estruturado e pedagógico da aula.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        return "Erro: API Key não configurada."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = f"""
        Você é um tutor acadêmico da EdukAngola. 
        Crie um resumo executivo e didático para a aula abaixo.
        Use bullet points para destacar os conceitos principais.
        O tom deve ser motivador e profissional.
        
        AULA: {aula_titulo}
        DESCRIÇÃO: {aula_descricao}
        """

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Não foi possível gerar o resumo automaticamente: {str(e)}"

def responder_duvida_ia(pergunta, aula_titulo, aula_descricao, historico=None):
    """
    Atua como um assistente de IA focado no conteúdo da aula para responder dúvidas dos alunos.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        return "Desculpe, o assistente está offline no momento."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        contexto = f"""
        Você é o 'Eduka AI', um assistente especializado da plataforma EdukAngola.
        Seu objetivo é ajudar o aluno a entender a aula: '{aula_titulo}'.
        Contexto da aula: {aula_descricao}
        
        REGRAS:
        1. Responda APENAS com base no contexto da aula ou conhecimentos gerais relacionados ao tema.
        2. Seja breve, claro e educado.
        3. Se não souber a resposta ou não estiver relacionada ao tema, sugira que o aluno pergunte ao instrutor na aba de 'Dúvidas'.
        """

        # Aqui poderíamos expandir para usar chat history se necessário
        response = model.generate_content(f"{contexto}\n\nPergunta do Aluno: {pergunta}")
        return response.text.strip()
    except Exception as e:
        return "Tive um pequeno problema técnico ao processar sua dúvida. Pode tentar novamente?"
def gerar_descricao_aula_ia(aula_titulo):
    """
    Cria uma descrição detalhada para uma aula com base apenas no título.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        return ""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = f"""
        Você é um especialista em currículo educacional da EdukAngola.
        Crie uma descrição detalhada e atrativa (cerca de 3 a 5 frases) para uma aula com o título: '{aula_titulo}'.
        O texto deve explicar a importância do tema e o que o aluno aprenderá.
        Use um tom profissional e encorajador.
        Responda APENAS o texto da descrição.
        """

        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return ""

def analisar_mercado_angola_ia(contexto_cursos):
    """
    Usa o Gemini para analisar o mercado angolano e identificar gaps de competências.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = f"""
        VOCÊ É UM ANALISTA DE INTELIGÊNCIA DE MERCADO SENIOR EM ANGOLA.
        Sua missão é realizar uma análise de impacto cruzando tendências REAIS E ATUAIS (conhecimento web) com os dados da plataforma EdukAngola.

        DADOS DA PLATAFORMA (CURSOS ATUAIS):
        {contexto_cursos}

        INSTRUÇÕES DE ANÁLISE:
        1. Baseie-se no cenário econômico de Angola em 2024/2025 (Crescimento do agronegócio, digitalização bancária, exploração mineira e diversificação econômica).
        2. Identifique 5 competências que são CRÍTICAS no mercado angolano agora, mas que os cursos acima NÃO cobrem ou cobrem de forma insuficiente.
        3. O insight_texto deve ser uma união entre o que está a acontecer no país e como a EdukAngola pode liderar essa formação.

        FORMATO DE RESPOSTA (JSON APENAS):
        {{
            "gaps": [
                {{
                    "skill": "Nome da Competência Real",
                    "demanda": 90,
                    "oferta": 10,
                    "tendencia": "up"
                }}
            ],
            "insight_texto": "Análise profunda unindo dados externos e internos...",
            "top_centros_sugeridos": ["Centros ou Instituições que deveriam focar nisso"]
        }}
        """

        response = model.generate_content(prompt)
        text = response.text
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        return json.loads(text.strip())
    except Exception as e:
        print(f"Erro no Analytics IA: {e}")
        return None

def gerar_perfil_competencias_ia(aluno_nome, curso_titulo, nota, exercicios_concluidos):
    """
    Gera uma descrição técnica das competências validadas para o certificado.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key: return "Competências técnicas validadas com sucesso."

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        Como avaliador técnico da EdukAngola, escreva um parágrafo profissional (3-4 linhas) 
        descrevendo as competências que o aluno {aluno_nome} demonstrou ao concluir o curso {curso_titulo} 
        com nota {nota} e resolvendo {exercicios_concluidos} exercícios práticos.
        Foque em termos técnicos e habilidades de mercado.
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except: return "Habilidades práticas e teóricas validadas pela plataforma EdukAngola."

def orientacao_vocacional_ia(perfil_aluno, interesses, centros_disponiveis="ISPTEC, ITEL, Agostinho Neto"):
    """
    Sugere cursos com base no interesse do aluno e centros parceiros.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key: return {"orientacao": "Configure a API Key.", "keywords": []}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = f"""
        Você é o Mentor de Carreira da EdukAngola. Analise o perfil e interesses:
        PERFIL: {perfil_aluno}
        INTERESSES: {interesses}

        ESTES SÃO OS CENTROS PARCEIROS DISPONÍVEIS NA NOSSA PLATAFORMA: {centros_disponiveis}

        Responda OBRIGATORIAMENTE em JSON no seguinte formato:
        {{
            "orientacao": "Texto motivador...",
            "keywords": ["busca1", "busca2"],
            "sugestoes_externas": [
                {{
                    "curso": "Nome da Formação",
                    "saidas": "Vagas em Angola",
                    "instituicoes_referencia": "Escolha APENAS entre os centros parceiros listados acima que oferecem este curso ou similar"
                }}
            ]
        }}
        Se nenhum dos centros parceiros oferecer o curso exato, sugira o mais próximo ou mencione que eles têm áreas base (TI, Gestão, Engenharia).
        """
        response = model.generate_content(prompt)
        import json
        texto = response.text.strip()
        # Limpar markdown se a IA colocar
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        
        return json.loads(texto)
    except Exception as e:
        print(f"Erro IA: {e}")
        return {"orientacao": "Foque em tecnologia e gestão.", "keywords": ["tecnologia", "gestão"]}

def orientacao_escolar_ia(perfil_dict, escolas_disponiveis="Liceu Mutu-ya-Kevela, PUNIV Central, Escola Técnica de Luanda"):
    """
    Função de IA focada no Ensino Médio/Geral.
    Avalia as respostas do aluno da 9ª classe e recomenda o melhor caminho acadêmico.
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key: 
        return {"analise": "Configure a API Key.", "curso_ensino_medio": "Desconhecido", "keywords": []}

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        nivel_academico = perfil_dict.get('nivel', '9_classe')
        perfil_str = f"Nível Académico: {'Terminou 9ª Classe' if nivel_academico == '9_classe' else 'Terminou Ensino Médio'} | Gostos: {perfil_dict.get('gostos', 'Não informado')} | Notas altas: {perfil_dict.get('notas', 'Não informado')} | Orçamento: {perfil_dict.get('orcamento', 'Não informado')}"
        
        contexto_prompt = "Você está falando com um jovem que terminou a 9ª classe e não sabe que caminho seguir no Ensino Médio (Liceu/Técnico)."
        if nivel_academico == "ensino_medio":
            contexto_prompt = "Você está falando com um jovem que terminou o Ensino Médio e quer saber qual curso superior (Universidade) ou técnico de alta empregabilidade deve seguir."

        prompt = f"""
        Você é o Orientador Académico Eduka AI em Angola.
        {contexto_prompt}
        
        PERFIL DO ALUNO:
        {perfil_str}
        
        Nós temos escolas/instituições ativas no portal na província dele: {escolas_disponiveis}

        Baseado no perfil do aluno, retorne um objeto JSON estrito com esta estrutura:
        {{
            "analise_perfil": "Um parágrafo amigável explicando qual o perfil dele (ex: Exatas, Humanas, Saúde) e por que.",
            "curso_ensino_medio": "Se terminou a 9ª classe: O curso ideal do Ensino Médio. Se terminou o Ensino Médio: O curso superior ideal (Licenciatura).",
            "alternativa_profissional": "Uma sugestão de curso profissional prático e rápido de curta duração com alta empregabilidade em Angola",
            "futuro_universidade": "Cursos superiores ou áreas de atuação que esse caminho permite",
            "keywords": ["busca1", "busca2"] // Palavras-chave curtas para filtrarmos a nossa base de dados (ex: "Físicas e Biológicas", "Informática", "Direito")
        }}
        """
        response = model.generate_content(prompt)
        import json
        texto = response.text.strip()
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        
        return json.loads(texto)
    except Exception as e:
        print(f"Erro IA Escolar: {e}")
        return {
            "analise_perfil": "Tens um perfil muito versátil.",
            "curso_ensino_medio": "Ciências Físicas e Biológicas",
            "alternativa_profissional": "Informática",
            "futuro_universidade": "Diversos cursos nas engenharias ou ciências.",
            "keywords": ["Físicas e Biológicas"]
        }
