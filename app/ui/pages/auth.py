import os

import streamlit as st

from app.services.network_checker import has_network_connection
from app.services.supabase_client import get_supabase_client
from app.services.temp_file_cleaner import clean_temp_files
from app.utils.validators import get_password_rules_message, is_valid_password


supabase = get_supabase_client()


def translate_auth_error(error_message: str) -> str:
    error_message = error_message.lower()

    if "user already registered" in error_message:
        return "Este e-mail já possui cadastro."

    if "invalid login credentials" in error_message:
        return "E-mail ou senha incorretos."

    if "email not confirmed" in error_message:
        return "E-mail ainda não confirmado. Verifique sua caixa de entrada antes de fazer login."

    if "email" in error_message and "confirm" in error_message:
        return "E-mail ainda não confirmado. Verifique sua caixa de entrada antes de fazer login."

    if "email rate limit exceeded" in error_message:
        return (
            "O limite temporário de envio de e-mails foi atingido. "
            "Aguarde alguns minutos e tente novamente."
        )

    if "otp_expired" in error_message or "token has expired" in error_message:
        return "Link de recuperação expirado. Solicite um novo link."

    if "invalid token" in error_message:
        return "Link de recuperação inválido ou expirado. Solicite um novo link."

    if "invalid refresh token" in error_message:
        return "Link de recuperação inválido ou expirado. Solicite um novo link."

    if "jwt" in error_message and "expired" in error_message:
        return "Link de recuperação expirado. Solicite um novo link."

    if "session" in error_message and "not found" in error_message:
        return "Sessão de recuperação inválida. Solicite um novo link."

    if "new password should be different" in error_message:
        return "A nova senha precisa ser diferente da senha atual."

    if "password" in error_message:
        return get_password_rules_message()

    return "Não foi possível concluir a operação. Verifique os dados informados."


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def get_query_param(param_name: str) -> str:
    value = st.query_params.get(param_name, "")

    if isinstance(value, list):
        return value[0] if value else ""

    return value or ""


def is_password_reset_request() -> bool:
    return (
        get_query_param("reset_password") == "1"
        and bool(get_query_param("token_hash"))
    )


def get_password_reset_redirect_url() -> str | None:
    redirect_url = os.getenv("PASSWORD_RESET_REDIRECT_URL", "").strip()

    if not redirect_url:
        return None

    return redirect_url


def send_password_reset_email(email: str):
    redirect_url = get_password_reset_redirect_url()

    if redirect_url:
        supabase.auth.reset_password_for_email(
            email,
            {
                "redirect_to": redirect_url,
            }
        )
        return

    supabase.auth.reset_password_for_email(email)


def clear_auth_session():
    st.session_state.pop("user", None)
    st.session_state.pop("access_token", None)
    clean_temp_files()


def finish_password_reset():
    st.session_state["password_reset_completed"] = True
    st.query_params.clear()
    st.rerun()


def verify_recovery_token_and_update_password(
    token_hash: str,
    recovery_type: str,
    new_password: str,
):
    response = supabase.auth.verify_otp({
        "token_hash": token_hash,
        "type": recovery_type,
    })

    session = getattr(response, "session", None)

    if session:
        access_token = getattr(session, "access_token", None)
        refresh_token = getattr(session, "refresh_token", None)

        if access_token and refresh_token:
            supabase.auth.set_session(access_token, refresh_token)

    supabase.auth.update_user({
        "password": new_password
    })


def render_password_update_form():
    st.title("Análise de Comunicação")
    st.subheader("Definir nova senha")

    st.info("Digite uma nova senha para concluir a recuperação da sua conta.")

    token_hash = get_query_param("token_hash")
    recovery_type = get_query_param("type") or "recovery"

    if not token_hash or recovery_type != "recovery":
        st.error("Link de recuperação inválido ou expirado. Solicite um novo link.")

        if st.button("Voltar para login"):
            st.query_params.clear()
            st.rerun()

        return

    with st.form("update_password_form"):
        new_password = st.text_input(
            "Nova senha",
            type="password",
            key="new_recovery_password"
        )
        confirm_password = st.text_input(
            "Confirmar nova senha",
            type="password",
            key="confirm_recovery_password"
        )

        st.caption(get_password_rules_message())

        submitted = st.form_submit_button("Salvar nova senha")

        if submitted:
            if not has_network_connection():
                st.error("Erro, verifique sua conexão com a rede.")
                return

            if new_password != confirm_password:
                st.error("As senhas não coincidem.")
                return

            if not is_valid_password(new_password):
                st.error(get_password_rules_message())
                return

            try:
                verify_recovery_token_and_update_password(
                    token_hash=token_hash,
                    recovery_type=recovery_type,
                    new_password=new_password,
                )

                try:
                    supabase.auth.sign_out()
                except Exception:
                    pass

                clear_auth_session()
                finish_password_reset()

            except Exception as e:
                st.error(translate_auth_error(str(e)))

    if st.button("Solicitar novo link de recuperação"):
        st.query_params.clear()
        st.rerun()


def render_login():
    if is_password_reset_request():
        render_password_update_form()
        return

    st.title("Análise de Comunicação")
    st.subheader("Acesse sua conta")

    if st.session_state.pop("password_reset_completed", False):
        st.success("Senha atualizada com sucesso! Faça login usando sua nova senha.")

    tab_login, tab_signup, tab_reset = st.tabs(
        ["Entrar", "Criar conta", "Esqueci minha senha"]
    )

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Senha", type="password")
            submitted = st.form_submit_button("Entrar")

            if submitted:
                if not has_network_connection():
                    st.error("Erro, verifique sua conexão com a rede.")
                    return

                email = normalize_email(email)

                if not email or not password:
                    st.error("Informe e-mail e senha para entrar.")
                    return

                try:
                    response = supabase.auth.sign_in_with_password({
                        "email": email,
                        "password": password
                    })

                    clean_temp_files()

                    st.session_state["user"] = response.user
                    st.session_state["access_token"] = response.session.access_token
                    st.success("Login realizado com sucesso!")
                    st.rerun()

                except Exception as e:
                    st.error(translate_auth_error(str(e)))

    with tab_signup:
        st.info(
            "Após criar sua conta, pode ser necessário confirmar o e-mail antes "
            "de fazer login. Verifique sua caixa de entrada e também a pasta de spam."
        )

        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Senha", type="password", key="signup_password")
            confirm_password = st.text_input(
                "Confirmar senha",
                type="password",
                key="signup_confirm_password"
            )

            st.caption(get_password_rules_message())

            submitted = st.form_submit_button("Criar conta")

            if submitted:
                if not has_network_connection():
                    st.error("Erro, verifique sua conexão com a rede.")
                    return

                email = normalize_email(email)

                if not email:
                    st.error("Informe um e-mail válido.")
                    return

                if password != confirm_password:
                    st.error("As senhas não coincidem.")
                    return

                if not is_valid_password(password):
                    st.error(get_password_rules_message())
                    return

                try:
                    response = supabase.auth.sign_up({
                        "email": email,
                        "password": password
                    })

                    if response.session:
                        clean_temp_files()

                        st.session_state["user"] = response.user
                        st.session_state["access_token"] = response.session.access_token
                        st.success("Conta criada com sucesso! Complete seu cadastro.")
                        st.rerun()
                    else:
                        st.success(
                            "Conta criada com sucesso! Verifique seu e-mail para "
                            "confirmar a conta antes de fazer login."
                        )
                        st.info(
                            "Caso não encontre o e-mail de confirmação, verifique "
                            "também a pasta de spam ou lixo eletrônico."
                        )

                except Exception as e:
                    st.error(translate_auth_error(str(e)))

    with tab_reset:
        st.info(
            "Informe o e-mail cadastrado para receber um link de recuperação de senha."
        )

        with st.form("password_reset_form"):
            reset_email = st.text_input(
                "Email",
                key="password_reset_email"
            )

            submitted = st.form_submit_button("Enviar link de recuperação")

            if submitted:
                if not has_network_connection():
                    st.error("Erro, verifique sua conexão com a rede.")
                    return

                reset_email = normalize_email(reset_email)

                if not reset_email:
                    st.error("Informe o e-mail cadastrado.")
                    return

                try:
                    send_password_reset_email(reset_email)

                    st.success(
                        "Se este e-mail estiver cadastrado, enviaremos um link de "
                        "recuperação. Verifique sua caixa de entrada e a pasta de spam."
                    )

                except Exception as e:
                    st.error(translate_auth_error(str(e)))