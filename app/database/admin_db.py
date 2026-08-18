from app.services.supabase_client import get_supabase_client


def get_authenticated_client(access_token: str):
    supabase = get_supabase_client()
    supabase.postgrest.auth(access_token)
    return supabase


def is_admin_user(user_id: str, access_token: str) -> bool:
    if not user_id or not access_token:
        return False

    supabase = get_authenticated_client(access_token)

    response = (
        supabase
        .table("admin_users")
        .select("id")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )

    return bool(response.data)


def get_admin_profiles(user_id: str, access_token: str):
    if not is_admin_user(user_id, access_token):
        return []

    supabase = get_authenticated_client(access_token)

    response = (
        supabase
        .table("profiles")
        .select(
            "id, full_name, birth_date, city, state, avatar_url, created_at"
        )
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def get_admin_analyses(user_id: str, access_token: str):
    if not is_admin_user(user_id, access_token):
        return []

    supabase = get_authenticated_client(access_token)

    response = (
        supabase
        .table("analyses")
        .select(
            "id, user_id, title, input_type, score, ai_available, status, created_at"
        )
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def get_admin_analyses_by_user(
    admin_user_id: str,
    access_token: str,
    selected_user_id: str
):
    if not is_admin_user(admin_user_id, access_token):
        return []

    if not selected_user_id:
        return []

    supabase = get_authenticated_client(access_token)

    response = (
        supabase
        .table("analyses")
        .select(
            "id, user_id, title, input_type, score, ai_available, status, created_at"
        )
        .eq("user_id", selected_user_id)
        .order("created_at", desc=True)
        .execute()
    )

    return response.data or []


def get_admin_analysis_report(
    admin_user_id: str,
    access_token: str,
    analysis_id: str
):
    if not is_admin_user(admin_user_id, access_token):
        return None

    if not analysis_id:
        return None

    supabase = get_authenticated_client(access_token)

    response = (
        supabase
        .table("analyses")
        .select(
            "id, user_id, title, input_type, score, report_json, created_at"
        )
        .eq("id", analysis_id)
        .maybe_single()
        .execute()
    )

    return response.data