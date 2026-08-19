def build_report(
    transcription_text: str,
    pause_data: dict,
    frequent_terms: dict,
    sequential_repetitions: list,
    score_data: dict,
    attention_points: list[str],
    recommendations: list[str] | None = None,
) -> dict:
    return {
        "transcricao": transcription_text,
        "score_comunicacao": score_data,
        "pontos_atencao": attention_points,
        "recomendacoes": recommendations or [],
        "pausas": {
            "duracao_total": pause_data.get("duracao_total", 0),
            "quantidade_pausas_longas": pause_data.get(
                "quantidade_pausas_longas",
                0
            ),
            "tempo_total_silencio": pause_data.get("tempo_total_silencio", 0),
            "pausas_longas": pause_data.get("pausas_longas", []),
        },
        "repeticoes": {
            "sequenciais": sequential_repetitions,
            "termos_recorrentes": frequent_terms,
        },
    }