from datetime import date, datetime

import streamlit as st

from app.database.profile_db import get_profile, save_profile
from app.services.avatar_storage import upload_avatar_image_to_storage
from app.services.network_checker import has_network_connection
from app.services.temp_file_cleaner import clean_temp_files
from app.ui.components.avatar import (
    render_avatar,
    render_uploaded_avatar_preview,
)
from app.ui.components.navigation import render_back_to_home_button


def parse_birth_date(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value).date()
    except Exception:
        return None


def get_profile_full_name(profile: dict) -> str:
    return (profile.get("full_name") or "").strip()


def render_complete_profile(user_id: str, access_token: str):
    st.title("Complete seu cadastro")
    st.write("Antes de continuar, preencha suas informações pessoais.")

    if st.button("Logout"):
        clean_temp_files()
        st.session_state.clear()
        st.rerun()

    st.subheader("Foto de perfil")

    avatar_file = st.file_uploader(
        "Foto de perfil (opcional)",
        type=["png", "jpg", "jpeg", "webp"]
    )

    render_uploaded_avatar_preview(avatar_file, width=120)

    with st.form("profile_form"):
        st.subheader("Informações pessoais")

        full_name = st.text_input(
            "Nome completo",
            placeholder="Ex: Daniel Costa"
        )

        birth_date = st.date_input(
            "Data de nascimento",
            value=None,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY"
        )

        st.subheader("Informações cadastrais")

        cpf = st.text_input("CPF", placeholder="000.000.000-00")
        phone = st.text_input("Telefone", placeholder="+55 (31) 99999-9999")

        st.subheader("Endereço")

        cep = st.text_input("CEP", placeholder="00000-000")
        street = st.text_input("Rua")
        number = st.text_input("Número")
        neighborhood = st.text_input("Bairro")
        city = st.text_input("Cidade")
        state = st.text_input("Estado", placeholder="MG", max_chars=2)

        submitted = st.form_submit_button("Salvar cadastro")

        if submitted:
            if not has_network_connection():
                st.error("Erro, verifique sua conexão com a rede.")
                return

            try:
                avatar_url = upload_avatar_image_to_storage(
                    avatar_file,
                    user_id,
                    access_token
                )
            except Exception:
                st.error("Não foi possível salvar a foto de perfil. Tente novamente.")
                return

            result = save_profile(
                user_id=user_id,
                access_token=access_token,
                full_name=full_name,
                birth_date=birth_date,
                cpf=cpf,
                phone=phone,
                cep=cep,
                street=street,
                number=number,
                neighborhood=neighborhood,
                city=city,
                state=state,
                avatar_url=avatar_url,
            )

            if result["success"]:
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["message"])


def render_profile(user_id: str, access_token: str):
    profile = get_profile(user_id, access_token)

    if not profile:
        st.warning("Perfil não encontrado.")
        render_back_to_home_button()
        return

    st.title("Meu perfil")

    render_avatar(profile.get("avatar_url", ""), width=140)

    avatar_file = st.file_uploader(
        "Alterar foto de perfil (opcional)",
        type=["png", "jpg", "jpeg", "webp"]
    )

    if avatar_file:
        render_uploaded_avatar_preview(avatar_file, width=120)

    with st.form("edit_profile_form"):
        st.subheader("Informações pessoais")

        full_name = st.text_input(
            "Nome completo",
            value=get_profile_full_name(profile)
        )

        birth_date = st.date_input(
            "Data de nascimento",
            value=parse_birth_date(profile.get("birth_date")),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY"
        )

        st.subheader("Informações cadastrais")

        cpf = st.text_input("CPF", value=profile.get("cpf", ""))
        phone = st.text_input("Telefone", value=profile.get("phone", ""))

        st.subheader("Endereço")

        cep = st.text_input("CEP", value=profile.get("cep", ""))
        street = st.text_input("Rua", value=profile.get("street", ""))
        number = st.text_input("Número", value=profile.get("number", ""))
        neighborhood = st.text_input(
            "Bairro",
            value=profile.get("neighborhood", "")
        )
        city = st.text_input("Cidade", value=profile.get("city", ""))
        state = st.text_input(
            "Estado",
            value=profile.get("state", ""),
            max_chars=2
        )

        submitted = st.form_submit_button("Salvar alterações")

        if submitted:
            if not has_network_connection():
                st.error("Erro, verifique sua conexão com a rede.")
                return

            avatar_url = profile.get("avatar_url", "")

            if avatar_file:
                try:
                    avatar_url = upload_avatar_image_to_storage(
                        avatar_file,
                        user_id,
                        access_token
                    )
                except Exception:
                    st.error("Não foi possível salvar a foto de perfil. Tente novamente.")
                    return

            result = save_profile(
                user_id=user_id,
                access_token=access_token,
                full_name=full_name,
                birth_date=birth_date,
                cpf=cpf,
                phone=phone,
                cep=cep,
                street=street,
                number=number,
                neighborhood=neighborhood,
                city=city,
                state=state,
                avatar_url=avatar_url,
            )

            if result["success"]:
                st.success("Perfil atualizado com sucesso.")
                st.rerun()
            else:
                st.error(result["message"])

    render_back_to_home_button()