import json
import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"

FALLBACK_MESSAGE = (
    "Análise global por IA indisponível no momento. "
    "O relatório foi gerado com os demais critérios normalmente."
)


def get_gemini_settings() -> tuple[str, str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()

    if not model_name:
        model_name = DEFAULT_GEMINI_MODEL

    return api_key, model_name


def extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Não foi possível localizar um JSON válido na resposta da IA.")

    return json.loads(text[start:end + 1])


def get_ai_unavailable_response(message: str = FALLBACK_MESSAGE) -> dict:
    return {
        "disponivel": False,
        "mensagem": message,
        "analise": "",
        "metricas": {},
        "recomendacoes": [],
    }


def analyze_full_transcription_with_gemini(transcription: str) -> dict:
    api_key, model_name = get_gemini_settings()

    if not api_key:
        return get_ai_unavailable_response()

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
Você é um avaliador rigoroso de comunicação oral em português.

Avalie a transcrição inteira e dê notas de 0 a 1.
As notas devem ser severas e proporcionais à frequência dos problemas.

Retorne apenas JSON válido neste formato:

{{
  "metricas": {{
    "controle_linguagem": 0.0,
    "clareza": 0.0,
    "formalidade": 0.0,
    "fluidez": 0.0,
    "qualidade_comunicacao": 0.0
  }},
  "analise": "análise objetiva, natural e compreensível para o usuário final",
  "recomendacoes": [
    "recomendação prática 1",
    "recomendação prática 2"
  ]
}}

Critérios internos:
- controle_linguagem: penalize vícios de linguagem, muletas, repetição excessiva, termos soltos e fala desorganizada.
- clareza: penalize frases confusas, ideias mal conectadas, erros gramaticais e falta de objetividade.
- formalidade: penalize gírias, coloquialidade excessiva, improviso excessivo e tom pouco profissional.
- fluidez: penalize hesitações, pausas, cortes, travamentos e quebras de raciocínio.
- qualidade_comunicacao: avalie segurança, organização, maturidade, objetividade e impacto geral.

Escala obrigatória:
- 0.00 a 0.20 = crítico, comunicação muito comprometida.
- 0.21 a 0.40 = ruim, muitos problemas relevantes.
- 0.41 a 0.60 = regular, problemas frequentes.
- 0.61 a 0.80 = bom, poucos problemas.
- 0.81 a 1.00 = excelente, fala clara, segura e bem estruturada.

Regras de avaliação:
- se houver muitos vícios, repetições ou fala confusa, controle_linguagem deve ser no máximo 0.35.
- se as ideias forem difíceis de entender, clareza deve ser no máximo 0.40.
- se houver travamentos frequentes, fluidez deve ser no máximo 0.40.
- se a fala parecer improvisada, insegura ou desorganizada, qualidade_comunicacao deve ser no máximo 0.40.
- não dê notas altas para falas apenas compreensíveis.
- seja rigoroso, não suavize falhas.
- a análise deve citar problemas concretos percebidos na transcrição.

Regras para recomendações:
- forneça recomendações práticas e aplicáveis.
- recomende ajustes de organização, clareza, objetividade e condução da fala.
- quando fizer sentido, recomende reduzir repetições, melhorar pausas e organizar melhor início, desenvolvimento e conclusão.
- não invente contexto fora da transcrição.

Regras para o texto da análise:
- escreva a análise como uma devolutiva para o usuário final.
- não cite nomes internos das métricas.
- não use termos como "controle_linguagem", "qualidade_comunicacao" ou qualquer chave do JSON.
- não coloque nomes de métricas entre aspas.
- não diga que uma métrica é "nula", "baixa" ou "alta" usando o nome técnico da métrica.
- explique os problemas em linguagem natural.
- seja direto, profissional e claro.
- não invente intenção, tema ou contexto que não estejam na transcrição.
- não use markdown.
- não escreva nada fora do JSON.

Transcrição:
{transcription}
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
            "mensagem": "Análise global por IA executada com sucesso.",
            "analise": parsed.get("analise", "").strip(),
            "metricas": parsed.get("metricas", {}),
            "recomendacoes": parsed.get("recomendacoes", []),
        }

    except Exception as error:
        return get_ai_unavailable_response(
            f"{FALLBACK_MESSAGE} | Erro técnico: {str(error)}"
        )