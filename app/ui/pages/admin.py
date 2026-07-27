import streamlit as st

from app.database.admin_db import (
    get_admin_analyses,
    get_admin_analyses_by_user,
    get_admin_profiles,
    is_admin_user,
)
from app.services.network_checker import has_network_connection
from app.ui.components.navigation import render_back_to_home_button
from app.ui.components.report_view import render_report_details
from app.ui.components.score import render_score_badge


def get_input_type_label(input_type: str) -> str:
    if input_type == "audio":
        return "Áudio"

    return "Vídeo"


def get_status_label(status: str) -> str:
    if status == "deleted":
        return "Descartada"

    return "Ativa"


def get_profile_full_name(profile: dict) -> str:
    full_name = (
        f"{profile.get('first_name', '')} "
        f"{profile.get('last_name', '')}"
    ).strip()

    if not full_name:
        return "Usuário sem nome"

    return full_name


def get_profile_option_label(profile: dict) -> str:
    full_name = get_profile_full_name(profile)
    city = profile.get("city") or "Cidade não informada"
    state = profile.get("state") or ""

    location = f"{city} {state}".strip()

    return f"{full_name} — {location}"


def calculate_analysis_summary(analyses: list) -> dict:
    total_analyses = len(analyses)

    scores = [
        analysis.get("score", 0)
        for analysis in analyses
        if analysis.get("score") is not None
    ]

    average_score = round(sum(scores) / len(scores), 1) if scores else 0
    best_score = max(scores) if scores else 0

    total_audio = sum(
        1 for analysis in analyses
        if analysis.get("input_type") == "audio"
    )

    total_video = sum(
        1 for analysis in analyses
        if analysis.get("input_type") == "video"
    )

    return {
        "total_analyses": total_analyses,
        "average_score": average_score,
        "best_score": best_score,
        "total_audio": total_audio,
        "total_video": total_video,
    }


def render_admin_metrics(profiles: list, analyses: list):
    summary = calculate_analysis_summary(analyses)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Usuários", len(profiles))

    with col2:
        st.metric("Análises", summary["total_analyses"])

    with col3:
        st.metric("Áudio", summary["total_audio"])

    with col4:
        st.metric("Vídeo", summary["total_video"])


def render_selected_user_profile(profile: dict):
    st.subheader("Usuário selecionado")

    full_name = get_profile_full_name(profile)
    city = profile.get("city") or "Cidade não informada"
    state = profile.get("state") or ""

    with st.container(border=True):
        st.write(f"👤 **{full_name}**")
        st.caption(f"Localização: {city} {state}")
        st.caption(f"Cadastrado em: {profile.get('created_at')}")
        st.caption(f"ID do usuário: {profile.get('id')}")


def render_selected_user_metrics(analyses: list):
    summary = calculate_analysis_summary(analyses)

    st.subheader("Resumo do usuário")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Análises", summary["total_analyses"])

    with col2:
        st.metric("Média", f"{summary['average_score']}/100")

    with col3:
        st.metric("Melhor score", f"{summary['best_score']}/100")

    with col4:
        st.metric("Áudio", summary["total_audio"])

    with col5:
        st.metric("Vídeo", summary["total_video"])


def render_user_analyses(analyses: list):
    st.subheader("Análises do usuário")

    if not analyses:
        st.info("Este usuário ainda não possui análises registradas.")
        return

    for analysis in analyses:
        analysis_id = analysis.get("id")
        title = analysis.get("title") or "Análise sem título"
        input_type = get_input_type_label(analysis.get("input_type", "video"))
        score = analysis.get("score", 0)
        status = get_status_label(analysis.get("status", "active"))
        created_at = analysis.get("created_at")
        ai_available = analysis.get("ai_available", False)

        with st.container(border=True):
            col1, col2, col3 = st.columns([4, 1.5, 2])

            with col1:
                st.write(f"📄 **{title}**")
                st.caption(f"Tipo: {input_type}")
                st.caption(f"Status: {status}")
                st.caption(f"Criada em: {created_at}")

                if not ai_available:
                    st.caption(
                        "⚠️ Análise gerada sem IA ou com IA indisponível."
                    )

            with col2:
                render_score_badge(score)

            with col3:
                if st.button("Ver detalhes", key=f"admin_detail_{analysis_id}"):
                    st.session_state["admin_selected_analysis"] = analysis_id
                    st.session_state["page"] = "admin_detail"
                    st.rerun()


def render_admin(user_id: str, access_token: str):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return

    if not is_admin_user(user_id, access_token):
        st.error("Acesso restrito a administradores.")
        render_back_to_home_button()
        return

    st.title("Painel Administrativo")

    st.caption(
        "Área somente leitura para acompanhamento de usuários e análises do sistema."
    )

    try:
        profiles = get_admin_profiles(user_id, access_token)
        all_analyses = get_admin_analyses(user_id, access_token)
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return

    render_admin_metrics(profiles, all_analyses)

    st.divider()

    st.subheader("Filtrar por usuário")

    if not profiles:
        st.info("Nenhum usuário cadastrado foi encontrado.")
        render_back_to_home_button()
        return

    profile_options = {
        profile["id"]: profile
        for profile in profiles
    }

    selected_user_id = st.selectbox(
        "Selecione um usuário para visualizar as análises",
        options=list(profile_options.keys()),
        format_func=lambda profile_id: get_profile_option_label(
            profile_options[profile_id]
        )
    )

    previous_user_id = st.session_state.get("admin_previous_user_id")

    if previous_user_id != selected_user_id:
        st.session_state.pop("admin_selected_analysis", None)
        st.session_state["admin_previous_user_id"] = selected_user_id

    selected_profile = profile_options[selected_user_id]

    try:
        user_analyses = get_admin_analyses_by_user(
            user_id,
            access_token,
            selected_user_id
        )
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return

    render_selected_user_profile(selected_profile)

    st.divider()

    render_selected_user_metrics(user_analyses)

    st.divider()

    render_user_analyses(user_analyses)

    render_back_to_home_button()