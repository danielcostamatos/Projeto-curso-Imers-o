import streamlit as st

from app.database.supabase_db import save_analysis_supabase
from app.services.attention_points_analyzer import generate_attention_points
from app.services.audio_extractor import extract_audio
from app.services.audio_file_manager import delete_temp_audio_file
from app.services.gemini_full_context_analyzer import (
    analyze_full_transcription_with_gemini,
)
from app.services.network_checker import has_network_connection
from app.services.pause_analyzer import analyze_pauses
from app.services.repetition_analyzer import (
    analyze_frequent_terms,
    analyze_sequential_repetitions,
)
from app.services.report_builder import build_report
from app.services.score_analyzer import calculate_communication_score
from app.services.text_analysis_analyzer import analyze_text_with_gemini
from app.services.text_report_builder import build_text_report
from app.services.text_score_analyzer import calculate_text_score
from app.services.transcriber import transcribe_audio


def show_ai_connection_error():
    if has_network_connection():
        st.error("Erro ao conectar com a IA. Tente novamente em instantes.")
    else:
        st.error("Erro, verifique sua conexão com a rede.")


def build_analysis_from_audio(audio_path: str):
    texto = transcribe_audio(audio_path)
    pause_data = analyze_pauses(audio_path)
    sequential_repetitions = analyze_sequential_repetitions(texto)
    frequent_terms = analyze_frequent_terms(texto)

    partial_report = {
        "transcricao": texto,
        "pausas": pause_data,
        "repeticoes": {
            "sequenciais": sequential_repetitions,
            "termos_recorrentes": frequent_terms,
        },
    }

    ai_full_analysis = analyze_full_transcription_with_gemini(texto)

    if not ai_full_analysis.get("disponivel", False):
        show_ai_connection_error()
        return None

    score_data = calculate_communication_score(
        partial_report,
        ia_metricas=ai_full_analysis.get("metricas", {})
    )

    attention_points = generate_attention_points(partial_report)

    report = build_report(
        transcription_text=texto,
        pause_data=pause_data,
        frequent_terms=frequent_terms,
        sequential_repetitions=sequential_repetitions,
        score_data=score_data,
        attention_points=attention_points,
        recommendations=ai_full_analysis.get("recomendacoes", []),
    )

    report["analise_global_ia"] = ai_full_analysis

    return report


def build_analysis_from_text(text_content: str):
    clean_text = (text_content or "").strip()

    if not clean_text:
        st.error("Nenhum texto foi encontrado para análise.")
        return None

    text_analysis = analyze_text_with_gemini(clean_text)

    if not text_analysis.get("disponivel", False):
        show_ai_connection_error()
        return None

    score_data = calculate_text_score(
        text_analysis.get("avaliacao", {})
    )

    return build_text_report(
        original_text=clean_text,
        text_analysis=text_analysis,
        score_data=score_data,
    )


def generate_report_from_video(
    video_path: str,
    audio_path: str,
    user_id: str,
    access_token: str
):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return None

    extracted_audio = extract_audio(video_path, audio_path)

    if not extracted_audio:
        return None

    report = build_analysis_from_audio(extracted_audio)

    if not report:
        return None

    report["input_type"] = "video"

    try:
        save_analysis_supabase(report, video_path, user_id, access_token)
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return None

    return report


def generate_report_from_audio(
    audio_path: str,
    user_id: str,
    access_token: str
):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return None

    if not audio_path:
        st.error("Nenhum áudio foi encontrado para análise.")
        return None

    try:
        report = build_analysis_from_audio(audio_path)

        if not report:
            return None

        report["input_type"] = "audio"

        try:
            save_analysis_supabase(report, audio_path, user_id, access_token)
        except Exception:
            st.error("Erro, verifique sua conexão com a rede.")
            return None

        return report

    finally:
        delete_temp_audio_file(audio_path)


def generate_report_from_text(
    text_content: str,
    user_id: str,
    access_token: str
):
    if not has_network_connection():
        st.error("Erro, verifique sua conexão com a rede.")
        return None

    report = build_analysis_from_text(text_content)

    if not report:
        return None

    try:
        save_analysis_supabase(
            report,
            "text_input",
            user_id,
            access_token
        )
    except Exception:
        st.error("Erro, verifique sua conexão com a rede.")
        return None

    return report


def generate_report(
    video_path: str,
    audio_path: str,
    user_id: str,
    access_token: str
):
    return generate_report_from_video(
        video_path,
        audio_path,
        user_id,
        access_token
    )