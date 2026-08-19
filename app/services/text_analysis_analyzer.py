from google import genai

from app.services.gemini_full_context_analyzer import (
    extract_json,
    get_gemini_settings,
)


TEXT_FALLBACK_MESSAGE = (
    "Análise textual por IA indisponível no momento. "
    "Não foi possível gerar a correção do texto."
)


def get_text_ai_unavailable_response(message: str = TEXT_FALLBACK_MESSAGE) -> dict:
    return {
        "disponivel": False,
        "mensagem": message,
        "texto_corrigido": "",
        "principais_correcoes": [],
        "avaliacao": {},
        "analise": "",
        "recomendacoes": [],
    }


def analyze_text_with_gemini(text_content: str) -> dict:
    api_key, model_name = get_gemini_settings()

    if not api_key:
        return get_text_ai_unavailable_response()

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
Você é um avaliador rigoroso de textos em português.

Avalie o texto digitado pelo usuário como uma produção escrita curta, semelhante a uma redação, apresentação escrita ou desenvolvimento de uma ideia.

Retorne apenas JSON válido neste formato:

{{
  "texto_corrigido": "versão corrigida do texto, preservando o sentido original",
  "principais_correcoes": [
    "correção objetiva 1",
    "correção objetiva 2"
  ],
  "avaliacao": {{
    "ortografia_gramatica": 0.0,
    "pontuacao": 0.0,
    "coerencia": 0.0,
    "coesao": 0.0,
    "clareza_objetividade": 0.0,
    "estrutura": 0.0,
    "desenvolvimento_argumentacao": 0.0
  }},
  "analise": "avaliação geral objetiva, natural e compreensível para o usuário final",
  "recomendacoes": [
    "recomendação prática 1",
    "recomendação prática 2"
  ]
}}

Critérios:
- ortografia_gramatica: avalie erros de ortografia, acentuação, concordância, regência, flexões e construção gramatical.
- pontuacao: avalie vírgulas, pontos, separação de frases, períodos longos e uso adequado dos sinais.
- coerencia: avalie se as ideias fazem sentido entre si e se o texto mantém uma linha lógica.
- coesao: avalie conectivos, ligação entre frases, progressão das ideias e transições.
- clareza_objetividade: avalie se o texto é claro, direto, compreensível e evita confusão.
- estrutura: avalie se há começo, desenvolvimento, conclusão e organização geral.
- desenvolvimento_argumentacao: avalie se a ideia foi desenvolvida, explicada, justificada e aprofundada. Penalize textos rasos, genéricos, muito simples ou sem progressão.

Escala obrigatória:
- 0.00 a 0.20 = crítico, texto muito comprometido.
- 0.21 a 0.40 = ruim, muitos problemas relevantes.
- 0.41 a 0.60 = regular, problemas frequentes ou desenvolvimento fraco.
- 0.61 a 0.80 = bom, poucos problemas, mas ainda com pontos de melhoria.
- 0.81 a 1.00 = excelente, texto correto, claro, bem estruturado e bem desenvolvido.

Regras rígidas de avaliação:
- Seja severo. Não dê notas altas para textos apenas compreensíveis.
- Se o texto for simples, curto em desenvolvimento ou apenas apresentar uma ideia sem explicá-la, desenvolvimento_argumentacao deve ser no máximo 0.40.
- Se não houver começo, desenvolvimento e conclusão claros, estrutura deve ser no máximo 0.50.
- Se houver muitos erros ortográficos, ortografia_gramatica deve ser no máximo 0.45.
- Se houver pontuação confusa ou períodos mal separados, pontuacao deve ser no máximo 0.45.
- Se as ideias estiverem soltas ou pouco conectadas, coesao deve ser no máximo 0.45.
- Se a ideia principal não estiver clara, clareza_objetividade deve ser no máximo 0.45.
- Se o texto parecer improvisado, raso ou sem aprofundamento, não atribua nota geral alta.
- Um texto com muitos erros ortográficos e pouco desenvolvimento não deve receber avaliação boa.
- Um texto sem desenvolvimento argumentativo adequado não pode ser tratado como texto bem construído.

Regras para a correção:
- preserve ao máximo a ideia original do usuário.
- corrija ortografia, pontuação, gramática, clareza e organização.
- não invente informações novas.
- não acrescente dados que não estejam no texto.
- não mude o sentido do texto.
- não transforme o texto em outro tema.
- se o texto estiver confuso, corrija apenas até onde for possível sem inventar conteúdo.

Regras para a análise:
- cite problemas concretos percebidos.
- explique se o texto tem pouco desenvolvimento, ausência de conclusão, baixa coesão ou erros recorrentes.
- as recomendações devem ser práticas e úteis.
- não use markdown.
- não escreva nada fora do JSON.

Texto do usuário:
{text_content}
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )

        response_text = getattr(response, "text", "") or ""

        if not response_text.strip():
            raise ValueError("A IA retornou uma resposta vazia.")

        parsed = extract_json(response_text)

        return {
            "disponivel": True,
            "mensagem": "Análise textual por IA executada com sucesso.",
            "texto_corrigido": parsed.get("texto_corrigido", "").strip(),
            "principais_correcoes": parsed.get("principais_correcoes", []),
            "avaliacao": parsed.get("avaliacao", {}),
            "analise": parsed.get("analise", "").strip(),
            "recomendacoes": parsed.get("recomendacoes", []),
        }

    except Exception as error:
        return get_text_ai_unavailable_response(
            f"{TEXT_FALLBACK_MESSAGE} | Erro técnico: {str(error)}"
        )