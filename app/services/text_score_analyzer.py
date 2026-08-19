def clamp_metric(value) -> float:
    try:
        metric = float(value)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(metric, 1.0))


def calculate_text_score(text_metrics: dict) -> dict:
    ortografia_gramatica = clamp_metric(
        text_metrics.get("ortografia_gramatica", 0)
    )
    pontuacao = clamp_metric(text_metrics.get("pontuacao", 0))
    coerencia = clamp_metric(text_metrics.get("coerencia", 0))
    coesao = clamp_metric(text_metrics.get("coesao", 0))
    clareza_objetividade = clamp_metric(
        text_metrics.get("clareza_objetividade", 0)
    )
    estrutura = clamp_metric(text_metrics.get("estrutura", 0))
    desenvolvimento_argumentacao = clamp_metric(
        text_metrics.get("desenvolvimento_argumentacao", 0)
    )

    score = (
        ortografia_gramatica * 20 +
        pontuacao * 15 +
        coerencia * 15 +
        coesao * 15 +
        clareza_objetividade * 15 +
        estrutura * 10 +
        desenvolvimento_argumentacao * 10
    )

    metricas = [
        ortografia_gramatica,
        pontuacao,
        coerencia,
        coesao,
        clareza_objetividade,
        estrutura,
        desenvolvimento_argumentacao,
    ]

    metricas_criticas = sum(1 for metrica in metricas if metrica <= 0.40)
    metricas_ruins = sum(1 for metrica in metricas if metrica <= 0.55)

    if desenvolvimento_argumentacao <= 0.25:
        score = min(score, 35)

    elif desenvolvimento_argumentacao <= 0.40:
        score = min(score, 45)

    if coerencia <= 0.30:
        score = min(score, 35)

    elif coerencia <= 0.45:
        score = min(score, 50)

    if clareza_objetividade <= 0.30:
        score = min(score, 35)

    elif clareza_objetividade <= 0.45:
        score = min(score, 50)

    if estrutura <= 0.30:
        score = min(score, 40)

    elif estrutura <= 0.45:
        score = min(score, 55)

    if ortografia_gramatica <= 0.30:
        score = min(score, 40)

    elif ortografia_gramatica <= 0.45:
        score = min(score, 55)

    if pontuacao <= 0.30:
        score = min(score, 40)

    elif pontuacao <= 0.45:
        score = min(score, 55)

    if coesao <= 0.35:
        score = min(score, 45)

    elif coesao <= 0.50:
        score = min(score, 60)

    if metricas_criticas >= 3:
        score = min(score, 45)

    if metricas_criticas >= 4:
        score = min(score, 35)

    if metricas_ruins >= 5:
        score = min(score, 55)

    if (
        desenvolvimento_argumentacao <= 0.45
        and estrutura <= 0.50
        and coerencia <= 0.55
    ):
        score = min(score, 50)

    if (
        ortografia_gramatica <= 0.45
        and pontuacao <= 0.45
        and desenvolvimento_argumentacao <= 0.50
    ):
        score = min(score, 45)

    score = max(score, 0)
    score = round(score)

    if score >= 85:
        classificacao = "Excelente"
        comentario = "Texto muito bem escrito, claro, correto e bem desenvolvido."
    elif score >= 70:
        classificacao = "Bom"
        comentario = "Texto bom, mas ainda com pontos de revisão, organização ou desenvolvimento."
    elif score >= 50:
        classificacao = "Regular"
        comentario = "Texto compreensível, mas com problemas relevantes de escrita, estrutura ou desenvolvimento."
    else:
        classificacao = "Precisa melhorar"
        comentario = "Texto com problemas importantes de escrita, clareza, estrutura ou desenvolvimento da ideia."

    return {
        "score": score,
        "classificacao": classificacao,
        "comentario": comentario,
        "detalhes": {
            "ia_metricas": {
                "ortografia_gramatica": ortografia_gramatica,
                "pontuacao": pontuacao,
                "coerencia": coerencia,
                "coesao": coesao,
                "clareza_objetividade": clareza_objetividade,
                "estrutura": estrutura,
                "desenvolvimento_argumentacao": desenvolvimento_argumentacao,
            }
        }
    }