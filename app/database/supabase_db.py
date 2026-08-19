from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.services.supabase_client import get_supabase_client


MONTHLY_ANALYSIS_LIMIT = 30
ANALYSIS_EXPIRATION_DAYS = 15
VALID_INPUT_TYPES = {"audio", "video", "text"}


def get_authenticated_client(access_token: str):
    client = get_supabase_client()
    client.postgrest.auth(access_token)
    return client


def get_current_utc_datetime() -> datetime:
    return datetime.now(timezone.utc)


def get_iso_datetime(value: datetime) -> str:
    return value.isoformat()


def get_month_range() -> tuple[str, str]:
    now = get_current_utc_datetime()

    start_of_month = now.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    if start_of_month.month == 12:
        start_of_next_month = start_of_month.replace(
            year=start_of_month.year + 1,
            month=1
        )
    else:
        start_of_next_month = start_of_month.replace(
            month=start_of_month.month + 1
        )

    return (
        get_iso_datetime(start_of_month),
        get_iso_datetime(start_of_next_month)
    )


def count_monthly_analyses_supabase(user_id: str, access_token: str) -> int:
    supabase = get_authenticated_client(access_token)

    start_of_month, start_of_next_month = get_month_range()

    response = (
        supabase
        .table("analyses")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .gte("created_at", start_of_month)
        .lt("created_at", start_of_next_month)
        .execute()
    )

    return response.count or 0


def get_remaining_monthly_analyses_supabase(
    user_id: str,
    access_token: str
) -> int:
    used = count_monthly_analyses_supabase(user_id, access_token)
    remaining = MONTHLY_ANALYSIS_LIMIT - used

    return max(remaining, 0)


def can_create_analysis_supabase(user_id: str, access_token: str) -> bool:
    used = count_monthly_analyses_supabase(user_id, access_token)

    return used < MONTHLY_ANALYSIS_LIMIT


def get_analysis_title(input_path: str, input_type: str) -> str:
    if input_type == "audio":
        return "Áudio gravado pelo navegador"

    if input_type == "text":
        return "Texto digitado"

    return Path(input_path).stem


def get_input_reference(input_path: str, input_type: str) -> str:
    if input_type == "audio":
        return "audio_recording"

    if input_type == "text":
        return "text_input"

    return input_path


def save_analysis_supabase(
    report: dict,
    video_path: str,
    user_id: str,
    access_token: str
):
    supabase = get_authenticated_client(access_token)

    input_type = report.get("input_type", "video")

    if input_type not in VALID_INPUT_TYPES:
        input_type = "video"

    title = get_analysis_title(video_path, input_type)
    score = report["score_comunicacao"]["score"]
    ai_available = report.get("analise_global_ia", {}).get("disponivel", False)

    now = get_current_utc_datetime()
    expires_at = now + timedelta(days=ANALYSIS_EXPIRATION_DAYS)

    data = {
        "user_id": user_id,
        "title": title,
        "video_name": get_input_reference(video_path, input_type),
        "input_type": input_type,
        "score": score,
        "transcription": report["transcricao"],
        "report_json": report,
        "ai_available": ai_available,
        "expires_at": get_iso_datetime(expires_at),
        "status": "active",
    }

    supabase.table("analyses").insert(data).execute()


def get_all_analyses_supabase(user_id: str, access_token: str):
    supabase = get_authenticated_client(access_token)

    now = get_iso_datetime(get_current_utc_datetime())

    response = (
        supabase
        .table("analyses")
        .select("*")
        .eq("user_id", user_id)
        .eq("status", "active")
        .gt("expires_at", now)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


def get_analysis_by_id_supabase(
    analysis_id: str,
    user_id: str,
    access_token: str
):
    supabase = get_authenticated_client(access_token)

    now = get_iso_datetime(get_current_utc_datetime())

    response = (
        supabase
        .table("analyses")
        .select("*")
        .eq("id", analysis_id)
        .eq("user_id", user_id)
        .eq("status", "active")
        .gt("expires_at", now)
        .single()
        .execute()
    )

    if not response.data:
        return None

    return response.data["report_json"]


def delete_analysis_supabase(
    analysis_id: str,
    user_id: str,
    access_token: str
):
    supabase = get_authenticated_client(access_token)

    (
        supabase
        .table("analyses")
        .update({"status": "deleted"})
        .eq("id", analysis_id)
        .eq("user_id", user_id)
        .execute()
    )


def get_average_score_supabase(user_id: str, access_token: str):
    data = get_all_analyses_supabase(user_id, access_token)

    if not data:
        return 0

    scores = [row["score"] for row in data]
    return round(sum(scores) / len(scores), 2)


def get_history_stats_supabase(user_id: str, access_token: str):
    data = get_all_analyses_supabase(user_id, access_token)

    if not data:
        return {
            "total_analyses": 0,
            "best_score": 0,
            "score_delta": 0,
        }

    chronological_data = list(reversed(data))
    scores = [row["score"] for row in chronological_data]

    return {
        "total_analyses": len(scores),
        "best_score": max(scores),
        "score_delta": scores[-1] - scores[0],
    }


def get_score_history_supabase(user_id: str, access_token: str):
    data = get_all_analyses_supabase(user_id, access_token)
    chronological_data = list(reversed(data))

    return [
        (row["title"], row["score"])
        for row in chronological_data
    ]