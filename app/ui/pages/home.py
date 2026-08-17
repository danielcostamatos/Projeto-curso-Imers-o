from html import escape

import streamlit as st

from app.database.profile_db import get_profile
from app.services.network_checker import has_network_connection
from app.services.temp_file_cleaner import clean_temp_files
from app.ui.session_state import clear_analysis_session


def get_home_name_label(profile: dict) -> str:
    if not profile:
        return "usuário"

    full_name = (profile.get("full_name") or "").strip()

    if full_name:
        return full_name.split()[0]

    first_name = (profile.get("first_name") or "").strip()

    if first_name:
        return first_name

    return "usuário"


def render_home(user_id: str, access_token: str):
    profile = get_profile(user_id, access_token)
    name_label = escape(get_home_name_label(profile))

    st.markdown(
        f"""
        <div class="welcome-pill">
            Bem-vindo de volta, {name_label} 👋
        </div>

        <div class="hero-title">
            Vamos analisar sua<br>comunicação?
        </div>

        <div class="hero-description">
            Envie seu discurso e receba uma análise completa com
            transcrição, organização da fala, pausas, repetições, pontos de atenção
            e uma avaliação geral por inteligência artificial.
        </div>
        """,
        unsafe_allow_html=True
    )

    col_analysis, col_history = st.columns([1.15, 0.85])

    with col_analysis:
        with st.container(border=True):
            st.markdown(
                """
                <div class="home-action-card">
                    <div class="home-action-icon">☁️</div>
                    <div class="home-action-title">Iniciar uma nova análise</div>
                    <div class="home-action-text">
                        Envie seu discurso para receber um feedback estruturado
                        sobre sua comunicação.
                    </div>
                    <div class="home-action-note">
                        Disponível para análise por áudio na versão web e por vídeo na versão local.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_a, col_b, col_c = st.columns([1, 1.4, 1])

            with col_b:
                if st.button("Iniciar análise", use_container_width=True):
                    clean_temp_files()
                    clear_analysis_session()

                    st.session_state["page"] = "analysis"
                    st.rerun()

    with col_history:
        with st.container(border=True):
            st.markdown(
                """
                <div class="home-action-card">
                    <div class="home-action-icon">📈</div>
                    <div class="home-action-title">Acompanhe sua evolução</div>
                    <div class="home-action-text">
                        Veja análises anteriores, acompanhe seus scores e observe
                        sua evolução ao longo do tempo.
                    </div>
                    <div class="home-action-note">
                        Histórico organizado por análise e desempenho.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            col_a, col_b, col_c = st.columns([1, 1.4, 1])

            with col_b:
                if st.button("Ver histórico", use_container_width=True):
                    if not has_network_connection():
                        st.error("Erro, verifique sua conexão com a rede.")
                        return

                    st.session_state["page"] = "history"
                    st.rerun()

    st.markdown(
        """
        <div class="privacy-card">
            <div class="privacy-icon">🔒</div>
            <div>
                <div class="privacy-title">Privacidade e segurança em primeiro lugar</div>
                <div class="privacy-text">
                    Seu conteúdo é privado e utilizado apenas para análise.
                    Não compartilhamos seu conteúdo com terceiros.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )