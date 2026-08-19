def build_text_report(
    original_text: str,
    text_analysis: dict,
    score_data: dict,
) -> dict:
    text_metrics = text_analysis.get("avaliacao", {})

    return {
        "input_type": "text",
        "transcricao": original_text,
        "score_comunicacao": score_data,
        "correcao_textual": {
            "texto_corrigido": text_analysis.get("texto_corrigido", ""),
            "principais_correcoes": text_analysis.get("principais_correcoes", []),
            "comentario_geral": text_analysis.get("analise", ""),
        },
        "avaliacao_textual": text_metrics,
        "recomendacoes": text_analysis.get("recomendacoes", []),
        "analise_global_ia": {
            "disponivel": text_analysis.get("disponivel", False),
            "mensagem": text_analysis.get("mensagem", ""),
            "analise": text_analysis.get("analise", ""),
            "metricas": text_metrics,
        },
        "pontos_atencao": [],
        "pausas": {
            "duracao_total": 0,
            "quantidade_pausas_longas": 0,
            "tempo_total_silencio": 0,
            "pausas_longas": [],
        },
        "repeticoes": {
            "sequenciais": [],
            "termos_recorrentes": {},
        },
    }