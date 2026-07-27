import streamlit as st

from app.database.admin_db import get_admin_analysis_report, is_admin_user
from app.services.network_checker import has_network_connection
from app.ui.components.report_view import render_report_details


def get_input_type_label(input_type: str) -> str:
    if input_type == "audio":
        return "Áudio"

    return "Vídeo"


def back_to_admin():
    st.session_state["page"] = "admin"
    st.rerun()


def render_admin_detail(user_id: str, access_token: str):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return

    if not is_admin_user(user_id, access_token):
        st.error("Acesso restrito a administradores.")
        return

    selected_analysis_id = st.session_state.get("admin_selected_analysis")

    if not selected_analysis_id:
        st.warning("Nenhuma análise selecionada.")
        if st.button("Voltar ao painel admin"):
            back_to_admin()
        return

    try:
        analysis = get_admin_analysis_report(
            user_id,
            access_token,
            selected_analysis_id
        )
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return

    if not analysis:
        st.error("Análise não encontrada.")
        if st.button("Voltar ao painel admin"):
            back_to_admin()
        return

    report = analysis.get("report_json")

    if not report:
        st.warning("Esta análise não possui relatório disponível.")
        if st.button("Voltar ao painel admin"):
            back_to_admin()
        return

    st.title("Detalhes da análise")

    if st.button("Voltar ao painel admin"):
        back_to_admin()

    st.caption(
        f"Análise: {analysis.get('title')} | "
        f"Tipo: {get_input_type_label(analysis.get('input_type', 'video'))} | "
        f"Usuário: {analysis.get('user_id')}"
    )

    render_report_details(report, video_name="admin_analise_historico")

    st.divider()

    if st.button("Voltar ao painel admin", key="admin_detail_back_bottom"):
        back_to_admin()