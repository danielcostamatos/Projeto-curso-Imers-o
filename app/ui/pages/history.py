from datetime import datetime, timezone

import streamlit as st

from app.database.supabase_db import (
    MONTHLY_ANALYSIS_LIMIT,
    delete_analysis_supabase,
    get_all_analyses_supabase,
    get_average_score_supabase,
    get_history_stats_supabase,
    get_remaining_monthly_analyses_supabase,
)
from app.services.network_checker import has_network_connection
from app.ui.components.navigation import render_back_to_home_button
from app.ui.components.score import render_score_badge, render_score_circle


def get_days_until_expiration(expires_at: str) -> int:
    if not expires_at:
        return 0

    try:
        expires_datetime = datetime.fromisoformat(
            expires_at.replace("Z", "+00:00")
        )

        now = datetime.now(timezone.utc)
        remaining_time = expires_datetime - now

        return max(remaining_time.days + 1, 0)

    except Exception:
        return 0


def get_input_type_label(input_type: str) -> str:
    if input_type == "audio":
        return "Áudio"

    if input_type == "text":
        return "Texto"

    return "Vídeo"


def get_input_type_icon(input_type: str) -> str:
    if input_type == "audio":
        return "🎙️"

    if input_type == "text":
        return "📝"

    return "🎥"


def render_analysis_title(title: str, ai_available: bool):
    if ai_available:
        st.write(f"📄 {title}")
    else:
        st.write(f"⚠️ 📄 {title}")
        st.caption("Análise gerada sem IA. Resultados podem ser menos precisos.")


def render_analysis_type(input_type: str):
    icon = get_input_type_icon(input_type)
    label = get_input_type_label(input_type)

    st.caption(f"{icon} Tipo: {label}")


def render_delete_warning(title: str, input_type: str):
    st.warning(
        f"Você tem certeza que deseja descartar a análise **{title}**?"
    )

    st.write(
        "Após o descarte, esta análise não poderá mais ser acessada no seu histórico."
    )

    if input_type == "text":
        st.caption(
            "Atenção: o limite mensal utilizado por esta análise não será restaurado. "
            "Em análises por texto, o conteúdo digitado permanece registrado no relatório "
            "para fins de controle e acompanhamento."
        )
        return

    st.caption(
        "Atenção: o limite mensal utilizado por esta análise não será restaurado, "
        "pois o relatório permanece registrado na nuvem para fins de controle e acompanhamento. "
        "O conteúdo bruto original, seja áudio ou vídeo, não é armazenado no banco de dados."
    )


def render_history(user_id: str, access_token: str):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return

    st.title("Histórico de Análises")

    avg_score = get_average_score_supabase(user_id, access_token)
    stats = get_history_stats_supabase(user_id, access_token)

    try:
        remaining_analyses = get_remaining_monthly_analyses_supabase(
            user_id,
            access_token
        )
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return

    st.subheader("Aproveitamento geral")
    render_score_circle(avg_score)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Análises disponíveis", stats["total_analyses"])

    with col2:
        st.metric(
            "Restantes no mês",
            f"{remaining_analyses}/{MONTHLY_ANALYSIS_LIMIT}"
        )

    with col3:
        st.metric("Melhor score", f"{stats['best_score']}/100")

    with col4:
        delta = stats["score_delta"]
        st.metric("Evolução", f"{delta:+} pontos")

    st.divider()

    analyses = get_all_analyses_supabase(user_id, access_token)

    if not analyses:
        st.info("Nenhuma análise disponível no momento.")
        render_back_to_home_button()
        return

    st.subheader("Análises realizadas")

    for analysis in analyses:
        analysis_id = analysis["id"]
        title = analysis["title"]
        score = analysis["score"]
        created_at = analysis["created_at"]
        ai_available = analysis["ai_available"]
        expires_at = analysis.get("expires_at")
        input_type = analysis.get("input_type", "video")

        days_remaining = get_days_until_expiration(expires_at)

        col1, col2, col3, col4, col5 = st.columns([4, 1.5, 2, 1.5, 1.5])

        with col1:
            render_analysis_title(title, ai_available)
            render_analysis_type(input_type)
            st.caption(f"Criada em: {created_at}")

        with col2:
            render_score_badge(score)

        with col3:
            if days_remaining <= 1:
                st.caption("Descartada em até 1 dia")
            else:
                st.caption(f"Descartada em {days_remaining} dias")

        with col4:
            if st.button("Abrir", key=f"open_{analysis_id}"):
                st.session_state["selected_analysis"] = analysis_id
                st.session_state["page"] = "detail"
                st.rerun()

        with col5:
            if st.button("Descartar", key=f"delete_{analysis_id}"):
                st.session_state["pending_delete_analysis"] = analysis_id
                st.rerun()

        if st.session_state.get("pending_delete_analysis") == analysis_id:
            with st.container(border=True):
                render_delete_warning(title, input_type)

                cancel_col, confirm_col = st.columns([1, 1])

                with cancel_col:
                    if st.button("Cancelar", key=f"cancel_delete_{analysis_id}"):
                        st.session_state.pop("pending_delete_analysis", None)
                        st.rerun()

                with confirm_col:
                    if st.button(
                        "Sim, descartar análise",
                        key=f"confirm_delete_{analysis_id}",
                        type="primary"
                    ):
                        try:
                            delete_analysis_supabase(
                                analysis_id,
                                user_id,
                                access_token
                            )
                        except Exception:
                            st.error("Erro, verifique sua conexão com a rede.")
                            return

                        if st.session_state.get("selected_analysis") == analysis_id:
                            del st.session_state["selected_analysis"]

                        st.session_state.pop("pending_delete_analysis", None)

                        st.success("Análise descartada com sucesso.")
                        st.rerun()

        st.divider()

    render_back_to_home_button()