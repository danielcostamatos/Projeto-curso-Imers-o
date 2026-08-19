import streamlit as st

from app.services.docx_exporter import build_docx_report


TEXT_EVALUATION_LABELS = {
    "ortografia_gramatica": "Ortografia e gramática",
    "pontuacao": "Pontuação",
    "coerencia": "Coerência",
    "coesao": "Coesão",
    "clareza_objetividade": "Clareza e objetividade",
    "estrutura": "Estrutura",
    "desenvolvimento_argumentacao": "Desenvolvimento da ideia",
}


def render_ai_warning():
    st.warning(
        "⚠️ Esta análise foi gerada sem avaliação da IA. "
        "Os resultados podem ser menos precisos."
    )


def render_filtered_attention_points(report: dict):
    pontos_filtrados = []

    for ponto in report.get("pontos_atencao", []):
        ponto_lower = ponto.lower()

        if "uso frequente" in ponto_lower:
            continue

        if "vício" in ponto_lower or "vicio" in ponto_lower:
            continue

        if "vícios" in ponto_lower or "vicios" in ponto_lower:
            continue

        pontos_filtrados.append(ponto)

    if pontos_filtrados:
        for ponto in pontos_filtrados:
            st.write(f"⚠️ {ponto}")
    else:
        st.write("Nenhum ponto crítico identificado nesta análise.")


def render_pause_details(report: dict):
    pausas = report.get("pausas", {})

    st.write(f"⏱ Duração total: {pausas.get('duracao_total', 0)}s")
    st.write(f"🛑 Pausas longas: {pausas.get('quantidade_pausas_longas', 0)}")
    st.write(f"🔇 Tempo em silêncio: {pausas.get('tempo_total_silencio', 0)}s")

    pausas_longas = pausas.get("pausas_longas", [])

    if pausas_longas:
        st.write("Pausas detectadas:")

        for pausa in pausas_longas:
            st.write(
                f"- {round(pausa['start'], 2)}s → "
                f"{round(pausa['end'], 2)}s "
                f"({round(pausa['duration'], 2)}s)"
            )
    else:
        st.write("Nenhuma pausa longa detectada.")


def render_repetition_details(report: dict):
    repeticoes = report.get("repeticoes", {})

    sequenciais = repeticoes.get("sequenciais", [])
    termos_recorrentes = repeticoes.get("termos_recorrentes", {})

    if sequenciais:
        st.write("Repetições em sequência:")

        for repeticao in sequenciais:
            st.write(f"- {repeticao['termo']}")
    else:
        st.write("Nenhuma repetição em sequência.")

    if termos_recorrentes:
        st.write("Termos mais recorrentes:")

        for termo, qtd in termos_recorrentes.items():
            st.write(f"- {termo}: {qtd}")
    else:
        st.write("Nenhum termo recorrente relevante.")


def render_recommendations(report: dict):
    recommendations = report.get("recomendacoes", [])

    if recommendations:
        for recommendation in recommendations:
            st.write(f"✅ {recommendation}")
    else:
        st.write("Nenhuma recomendação específica foi gerada para esta análise.")


def render_report_download(report: dict, video_name: str):
    docx_bytes = build_docx_report(report, video_name=video_name)

    st.download_button(
        label="Baixar relatório em DOCX",
        data=docx_bytes,
        file_name="relatorio_analise_comunicacao.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def render_score_section(report: dict, title: str):
    score_data = report["score_comunicacao"]

    st.subheader(title)
    st.metric("Pontuação geral", f"{score_data['score']}/100")
    st.write(f"**Classificação:** {score_data['classificacao']}")
    st.write(score_data["comentario"])


def render_text_evaluation(report: dict):
    evaluation = report.get("avaliacao_textual", {})

    if not evaluation:
        st.write("Nenhuma avaliação textual detalhada foi encontrada.")
        return

    for key, label in TEXT_EVALUATION_LABELS.items():
        value = evaluation.get(key)

        if value is None:
            continue

        try:
            percentage = round(float(value) * 100)
        except (TypeError, ValueError):
            percentage = 0

        st.write(f"**{label}:** {percentage}/100")


def render_text_report_details(report: dict, video_name: str):
    render_score_section(report, "Score textual")

    analise_ia = report.get("analise_global_ia", {})

    if not analise_ia.get("disponivel", False):
        render_ai_warning()

    correction = report.get("correcao_textual", {})

    st.subheader("Correção")
    corrected_text = correction.get("texto_corrigido", "")

    if corrected_text:
        st.write(corrected_text)
    else:
        st.write("Nenhuma versão corrigida foi gerada.")

    principais_correcoes = correction.get("principais_correcoes", [])

    st.subheader("Principais correções")

    if principais_correcoes:
        for item in principais_correcoes:
            st.write(f"✏️ {item}")
    else:
        st.write("Nenhuma correção específica foi listada.")

    st.subheader("Avaliação textual")
    render_text_evaluation(report)

    st.subheader("Análise geral")
    st.write(correction.get("comentario_geral", ""))

    st.subheader("Recomendações")
    render_recommendations(report)

    with st.expander("Ver texto original enviado"):
        st.write(report.get("transcricao", ""))

    st.divider()

    render_report_download(report, video_name)


def render_oral_report_details(report: dict, video_name: str):
    render_score_section(report, "Score de comunicação")

    analise_ia = report.get("analise_global_ia", {})

    if not analise_ia.get("disponivel", False):
        render_ai_warning()

    st.subheader("Transcrição")
    st.write(report["transcricao"])

    st.subheader("Análise global por IA")
    st.write(analise_ia.get("analise", ""))

    st.subheader("Recomendações")
    render_recommendations(report)

    st.subheader("Pontos de atenção")
    render_filtered_attention_points(report)

    st.subheader("Pausas")
    render_pause_details(report)

    st.subheader("Repetições")
    render_repetition_details(report)

    st.divider()

    render_report_download(report, video_name)


def render_report_details(report: dict, video_name: str = "video_analisado"):
    if report.get("input_type") == "text":
        render_text_report_details(report, video_name)
        return

    render_oral_report_details(report, video_name)