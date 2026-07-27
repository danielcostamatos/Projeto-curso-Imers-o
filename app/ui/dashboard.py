import streamlit as st

from app.database.profile_db import profile_exists
from app.services.network_checker import has_network_connection
from app.ui.components.avatar import render_avatar
from app.ui.components.sidebar import render_sidebar
from app.ui.pages.analysis import render_analysis
from app.ui.pages.auth import render_login
from app.ui.pages.detail import render_detail
from app.ui.pages.history import render_history
from app.ui.pages.home import render_home
from app.ui.pages.profile import render_complete_profile, render_profile
from app.ui.pages.admin import render_admin
from app.ui.pages.admin_detail import render_admin_detail
from app.ui.session_state import get_access_token, get_current_user_id
from app.ui.styles import apply_global_styles


st.set_page_config(
    page_title="Análise de Comunicação",
    layout="wide",
    initial_sidebar_state="expanded"
)


def run_app():
    apply_global_styles()

    user_id = get_current_user_id()
    access_token = get_access_token()

    if not user_id or not access_token:
        render_login()
        return

    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return

    if not profile_exists(user_id, access_token):
        render_complete_profile(user_id, access_token)
        return

    if "page" not in st.session_state:
        st.session_state["page"] = "home"

    render_sidebar(user_id, access_token, render_avatar)

    current_page = st.session_state.get("page", "home")

    if current_page == "home":
        render_home(user_id, access_token)

    elif current_page == "analysis":
        render_analysis(user_id, access_token)

    elif current_page == "history":
        render_history(user_id, access_token)

    elif current_page == "detail":
        render_detail(user_id, access_token)

    elif current_page == "profile":
        render_profile(user_id, access_token)

    elif current_page == "admin":
        render_admin(user_id, access_token)

    elif current_page == "admin_detail":
        render_admin_detail(user_id, access_token)

    else:
        st.session_state["page"] = "home"
        st.rerun()


if __name__ == "__main__":
    run_app()