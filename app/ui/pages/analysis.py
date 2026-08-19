import streamlit as st

from app.database.supabase_db import (
    MONTHLY_ANALYSIS_LIMIT,
    can_create_analysis_supabase,
    get_remaining_monthly_analyses_supabase,
)
from app.database.profile_db import get_profile
from app.services.analysis_pipeline import (
    generate_report,
    generate_report_from_audio,
    generate_report_from_text,
)
from app.services.audio_file_manager import save_recorded_audio
from app.services.network_checker import has_network_connection
from app.services.temp_file_cleaner import clean_temp_files
from app.ui.components.navigation import render_back_to_home_button
from app.ui.components.report_view import render_report_details
from app.ui.session_state import clear_analysis_session
from app.utils.app_mode import get_app_mode_label, is_web_mode
from app.utils.file_manager import save_uploaded_file


TEXT_ANALYSIS_MIN_CHARACTERS = 300
TEXT_ANALYSIS_MAX_CHARACTERS = 3000


def get_user_first_name(user_id: str, access_token: str) -> str:
    try:
        profile = get_profile(user_id, access_token)
    except Exception:
        return "seu nome"

    if not profile:
        return "seu nome"

    full_name = (profile.get("full_name") or "").strip()

    if not full_name:
        return "seu nome"

    return full_name.split()[0]


def reset_current_analysis():
    clean_temp_files()
    clear_analysis_session()


def select_analysis_method(method: str):
    reset_current_analysis()
    st.session_state["analysis_method"] = method
    st.rerun()


def clear_selected_analysis_method():
    st.session_state.pop("analysis_method", None)
    reset_current_analysis()
    st.rerun()


def get_result_reference_name() -> str:
    report = st.session_state.get("report", {})
    input_type = report.get("input_type")

    if input_type == "audio":
        return "audio_gravado"

    if input_type == "text":
        return "texto_digitado"

    return st.session_state.get("video_path", "video_analisado")


def render_analysis_result():
    st.title("Resultado da análise")

    video_path = st.session_state.get("video_path")
    report = st.session_state.get("report", {})

    if report.get("input_type") == "video" and video_path:
        render_result_video(video_path)

    st.divider()

    render_report_details(
        st.session_state["report"],
        video_name=get_result_reference_name()
    )

    st.divider()

    render_result_actions()


def render_result_video(video_path: str):
    st.markdown('<div class="result-video-card">', unsafe_allow_html=True)

    with st.container(border=True):
        st.subheader("Vídeo analisado")
        st.caption("Arquivo utilizado para gerar esta análise.")
        st.video(video_path)

    st.markdown("</div>", unsafe_allow_html=True)


def render_result_actions():
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Voltar ao início", use_container_width=True):
            st.session_state["page"] = "home"
            st.rerun()

    with col2:
        if st.button("Acompanhe sua evolução", use_container_width=True):
            st.session_state["page"] = "history"
            st.rerun()

    with col3:
        if st.button("Iniciar nova análise", use_container_width=True):
            st.session_state.pop("analysis_method", None)
            reset_current_analysis()
            st.session_state["page"] = "analysis"
            st.rerun()


def render_analysis_privacy_notice():
    with st.expander("Privacidade e qualidade da análise", expanded=False):
        st.markdown(
            """
            * Vídeos e áudios são utilizados apenas temporariamente para processamento.
            * Vídeos e áudios brutos não são salvos no banco de dados nem no Supabase Storage.
            * Textos digitados são salvos como parte do relatório da análise textual, junto com score, correção e recomendações.
            * As análises ficam disponíveis por 15 dias e podem ser descartadas pelo usuário.
            * O descarte remove a análise do histórico comum, mas mantém o registro para controle interno.
            * Para análises por áudio ou vídeo, certifique-se de que o áudio foi captado com clareza, com pouco ruído externo e boa distância do microfone.
            """
        )


def render_audio_quality_notice(source: str):
    if source == "video":
        message = (
            "Certifique-se de que o áudio do vídeo foi captado com clareza, "
            "sem ruído externo relevante, eco excessivo, volume muito baixo ou "
            "falas sobrepostas. Esses fatores podem interferir na transcrição e "
            "no resultado da análise."
        )
    else:
        message = (
            "Certifique-se de que o áudio foi captado com clareza, sem ruído "
            "externo relevante, eco excessivo, volume muito baixo ou falas "
            "sobrepostas. Esses fatores podem interferir na transcrição e no "
            "resultado da análise."
        )

    st.info(message)


def render_text_privacy_notice():
    st.info(
        "O texto digitado será salvo como parte do relatório da análise textual, "
        "junto com a correção, avaliação, score e recomendações."
    )


def render_analysis_intro():
    st.title("Análise")

    st.write(
        "Escolha como deseja avaliar seu discurso. Você pode gravar sua fala, "
        "enviar um vídeo na versão local ou escrever um texto para análise."
    )

    st.caption(get_app_mode_label())

    render_analysis_privacy_notice()


def render_analysis_method_selector():
    render_analysis_intro()

    st.subheader("Como deseja avaliar seu discurso?")

    if is_web_mode():
        col_audio, col_text = st.columns(2)

        with col_audio:
            render_analysis_method_card(
                title="Gravar áudio",
                icon="🎙️",
                description=(
                    "Grave seu discurso diretamente pelo navegador "
                    "e receba uma análise da sua comunicação."
                ),
                button_label="Gravar áudio",
                method="audio",
            )

        with col_text:
            render_analysis_method_card(
                title="Escrever texto",
                icon="📝",
                description=(
                    "Digite sua apresentação ou ideia para avaliar clareza, "
                    "organização e estrutura do conteúdo."
                ),
                button_label="Escrever texto",
                method="text",
            )

        return

    col_video, col_audio, col_text = st.columns(3)

    with col_video:
        render_analysis_method_card(
            title="Enviar vídeo",
            icon="🎥",
            description=(
                "Envie um vídeo para analisar a fala a partir do conteúdo gravado."
            ),
            button_label="Enviar vídeo",
            method="video",
        )

    with col_audio:
        render_analysis_method_card(
            title="Gravar áudio",
            icon="🎙️",
            description=(
                "Grave seu discurso pelo navegador e gere uma análise da fala."
            ),
            button_label="Gravar áudio",
            method="audio",
        )

    with col_text:
        render_analysis_method_card(
            title="Escrever texto",
            icon="📝",
            description=(
                "Digite sua apresentação ou ideia para avaliar a estrutura do discurso."
            ),
            button_label="Escrever texto",
            method="text",
        )


def render_analysis_method_card(
    title: str,
    icon: str,
    description: str,
    button_label: str,
    method: str,
):
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        st.write(description)

        if st.button(button_label, use_container_width=True, key=f"method_{method}"):
            select_analysis_method(method)


def get_remaining_analyses_or_show_error(user_id: str, access_token: str):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        render_back_to_home_button()
        return None

    try:
        return get_remaining_monthly_analyses_supabase(user_id, access_token)
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        render_back_to_home_button()
        return None


def render_monthly_limit_status(remaining_analyses: int) -> bool:
    st.info(
        f"Você possui {remaining_analyses} de "
        f"{MONTHLY_ANALYSIS_LIMIT} análises disponíveis neste mês."
    )

    if remaining_analyses <= 0:
        st.warning(
            f"Você atingiu o limite mensal de {MONTHLY_ANALYSIS_LIMIT} análises. "
            "Tente novamente no próximo mês ou entre em contato com a equipe."
        )
        render_back_to_home_button()
        return False

    return True


def render_selected_method_header(title: str, description: str):
    st.title(title)
    st.write(description)

    render_analysis_privacy_notice()

    if st.button("Escolher outro tipo de análise"):
        clear_selected_analysis_method()

    st.divider()


def render_video_uploader(user_id: str, access_token: str):
    remaining_analyses = get_remaining_analyses_or_show_error(
        user_id,
        access_token
    )

    if remaining_analyses is None:
        return

    can_continue = render_monthly_limit_status(remaining_analyses)

    if not can_continue:
        return

    render_selected_method_header(
        title="Enviar vídeo",
        description=(
            "Envie um vídeo do seu discurso. Antes de analisar, confira se o arquivo "
            "carregado está correto."
        )
    )

    render_audio_quality_notice("video")

    with st.container(border=True):
        st.markdown("### Arquivo de vídeo")

        uploaded_file = st.file_uploader(
            "Envie um vídeo",
            type=["mp4", "mov", "avi", "mkv"]
        )

        st.caption("Formatos aceitos: MP4, MOV, AVI, MKV • Até 2GB")

        if not uploaded_file:
            return

        handle_uploaded_video(uploaded_file)

        st.divider()

        render_video_preview()

        if st.button("Analisar vídeo", type="primary"):
            process_video_analysis(user_id, access_token)


def handle_uploaded_video(uploaded_file):
    current_file_name = st.session_state.get("uploaded_file_name")

    if current_file_name == uploaded_file.name:
        return

    st.session_state["uploaded_file_name"] = uploaded_file.name
    st.session_state.pop("report", None)

    video_path = f"data/input/{uploaded_file.name}"
    audio_path = "data/temp/audio.wav"

    save_uploaded_file(uploaded_file, video_path)

    st.session_state["video_path"] = video_path
    st.session_state["audio_path"] = audio_path


def render_video_preview():
    st.markdown("### Pré-visualização do vídeo")
    st.caption("Confira se o arquivo enviado está correto antes de analisar.")

    preview_col, _ = st.columns([0.72, 0.28])

    with preview_col:
        st.video(st.session_state["video_path"])


def can_user_create_analysis_or_show_warning(
    user_id: str,
    access_token: str
) -> bool:
    try:
        can_create_analysis = can_create_analysis_supabase(
            user_id,
            access_token
        )
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return False

    if not can_create_analysis:
        st.warning(
            f"Você atingiu o limite mensal de {MONTHLY_ANALYSIS_LIMIT} análises. "
            "Tente novamente no próximo mês ou entre em contato com a equipe."
        )
        return False

    return True


def process_video_analysis(user_id: str, access_token: str):
    if not can_user_create_analysis_or_show_warning(user_id, access_token):
        return

    video_path = st.session_state.get("video_path")
    audio_path = st.session_state.get("audio_path")

    if not video_path or not audio_path:
        st.error("Não foi possível localizar o vídeo enviado. Tente enviar novamente.")
        return

    with st.spinner("Processando vídeo..."):
        report = generate_report(
            video_path,
            audio_path,
            user_id,
            access_token
        )

        if not report:
            return

        st.session_state["report"] = report
        st.success("Análise concluída e salva no histórico.")
        st.rerun()


def render_audio_analysis(user_id: str, access_token: str):
    remaining = get_remaining_analyses_or_show_error(user_id, access_token)

    if remaining is None:
        return

    can_continue = render_monthly_limit_status(remaining)

    if not can_continue:
        return

    render_selected_method_header(
        title="Gravar áudio",
        description=(
            "Grave seu discurso diretamente pelo navegador. O áudio bruto será usado "
            "apenas temporariamente para gerar a transcrição e a análise."
        )
    )

    render_audio_quality_notice("audio")

    with st.container(border=True):
        st.subheader("Grave seu discurso")

        st.caption(
            "Após a gravação, confira o áudio antes de iniciar a análise."
        )

        audio_file = st.audio_input("Clique para gravar seu áudio")

        if audio_file:
            st.audio(audio_file)

            if st.button("Analisar áudio", type="primary"):
                process_audio_analysis(audio_file, user_id, access_token)


def process_audio_analysis(audio_file, user_id: str, access_token: str):
    if not can_user_create_analysis_or_show_warning(user_id, access_token):
        return

    audio_path = save_recorded_audio(audio_file)

    st.session_state["audio_path"] = audio_path
    st.session_state["uploaded_file_name"] = "Áudio gravado pelo navegador"

    with st.spinner("Analisando seu áudio..."):
        report = generate_report_from_audio(
            audio_path,
            user_id,
            access_token
        )

    if report:
        st.session_state["report"] = report
        st.success("Análise concluída com sucesso.")
        st.rerun()


def render_text_analysis(user_id: str, access_token: str):
    remaining = get_remaining_analyses_or_show_error(user_id, access_token)

    if remaining is None:
        return

    can_continue = render_monthly_limit_status(remaining)

    if not can_continue:
        return

    render_selected_method_header(
        title="Escrever texto",
        description=(
            "Digite sua apresentação, explicação ou ideia. A análise textual avalia "
            "clareza, organização, coesão, repetições e pontos de melhoria do conteúdo."
        )
    )

    render_text_privacy_notice()

    with st.container(border=True):
        st.subheader("Texto do discurso")

        st.caption(
            "Esta opção não avalia pausas reais, entonação ou ritmo vocal, "
            "pois o conteúdo é digitado."
        )

        user_first_name = get_user_first_name(user_id, access_token)

        text_content = st.text_area(
            "Digite seu texto",
            height=260,
            max_chars=TEXT_ANALYSIS_MAX_CHARACTERS,
            placeholder=(
                f"Exemplo: Olá, meu nome é {user_first_name}. Hoje eu vou apresentar "
                "uma ideia sobre..."
            )
        )

        character_count = len((text_content or "").strip())

        st.caption(
            f"{character_count}/{TEXT_ANALYSIS_MAX_CHARACTERS} caracteres "
            f"• mínimo de {TEXT_ANALYSIS_MIN_CHARACTERS}"
        )

        if character_count and character_count < TEXT_ANALYSIS_MIN_CHARACTERS:
            st.warning(
                "Digite um texto um pouco maior para que a análise tenha contexto suficiente."
            )

        can_analyze_text = (
            TEXT_ANALYSIS_MIN_CHARACTERS
            <= character_count
            <= TEXT_ANALYSIS_MAX_CHARACTERS
        )

        if st.button(
            "Analisar texto",
            type="primary",
            disabled=not can_analyze_text
        ):
            process_text_analysis(text_content, user_id, access_token)


def process_text_analysis(
    text_content: str,
    user_id: str,
    access_token: str
):
    if not can_user_create_analysis_or_show_warning(user_id, access_token):
        return

    with st.spinner("Analisando seu texto..."):
        report = generate_report_from_text(
            text_content,
            user_id,
            access_token
        )

    if report:
        st.session_state["report"] = report
        st.session_state["uploaded_file_name"] = "Texto digitado"
        st.success("Análise concluída com sucesso.")
        st.rerun()


def render_selected_analysis_method(user_id: str, access_token: str):
    selected_method = st.session_state.get("analysis_method")

    if selected_method == "audio":
        render_audio_analysis(user_id, access_token)
        render_back_to_home_button()
        return

    if selected_method == "text":
        render_text_analysis(user_id, access_token)
        render_back_to_home_button()
        return

    if selected_method == "video" and not is_web_mode():
        render_video_uploader(user_id, access_token)
        render_back_to_home_button()
        return

    st.session_state.pop("analysis_method", None)
    st.rerun()


def render_analysis(user_id: str, access_token: str):
    if "report" in st.session_state:
        render_analysis_result()
        return

    if not st.session_state.get("analysis_method"):
        render_analysis_method_selector()
        render_back_to_home_button()
        return

    render_selected_analysis_method(user_id, access_token)