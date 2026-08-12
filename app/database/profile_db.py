from datetime import date, datetime

from app.services.supabase_client import get_supabase_client
from app.utils.validators import (
    is_valid_cep,
    is_valid_cpf,
    is_valid_phone,
    normalize_cep,
    normalize_cpf,
    normalize_phone,
)


def get_authenticated_client(access_token: str):
    client = get_supabase_client()
    client.postgrest.auth(access_token)
    return client


def normalize_full_name(full_name: str) -> str:
    return " ".join((full_name or "").strip().split())


def split_full_name(full_name: str) -> tuple[str, str]:
    name_parts = normalize_full_name(full_name).split(" ", 1)

    first_name = name_parts[0] if name_parts else ""
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    return first_name, last_name


def normalize_birth_date(birth_date) -> str:
    if not birth_date:
        return ""

    if isinstance(birth_date, date):
        return birth_date.isoformat()

    if isinstance(birth_date, str):
        return birth_date.strip()

    return ""


def is_valid_birth_date(birth_date_value: str) -> bool:
    if not birth_date_value:
        return False

    try:
        parsed_birth_date = datetime.fromisoformat(birth_date_value).date()
    except ValueError:
        return False

    return parsed_birth_date <= date.today()


def save_profile(
    user_id: str,
    access_token: str,
    full_name: str,
    birth_date,
    cpf: str,
    phone: str,
    cep: str,
    street: str = "",
    number: str = "",
    neighborhood: str = "",
    city: str = "",
    state: str = "",
    avatar_url: str = "",
):
    supabase = get_authenticated_client(access_token)

    clean_full_name = normalize_full_name(full_name)
    clean_birth_date = normalize_birth_date(birth_date)
    clean_cpf = normalize_cpf(cpf)
    clean_phone = normalize_phone(phone)
    clean_cep = normalize_cep(cep)

    if len(clean_full_name) < 3 or len(clean_full_name.split()) < 2:
        return {"success": False, "message": "Informe um nome completo válido."}

    if not is_valid_birth_date(clean_birth_date):
        return {"success": False, "message": "Informe uma data de nascimento válida."}

    if not is_valid_cpf(clean_cpf):
        return {"success": False, "message": "Informe um CPF válido."}

    if not is_valid_phone(clean_phone):
        return {"success": False, "message": "Informe um telefone válido."}

    if not is_valid_cep(clean_cep):
        return {"success": False, "message": "Informe um CEP válido."}

    first_name, last_name = split_full_name(clean_full_name)

    data = {
        "id": user_id,
        "full_name": clean_full_name,
        "birth_date": clean_birth_date,
        "first_name": first_name,
        "last_name": last_name,
        "cpf": clean_cpf,
        "phone": clean_phone,
        "cep": clean_cep,
        "street": street.strip() if street else "",
        "number": number.strip() if number else "",
        "neighborhood": neighborhood.strip() if neighborhood else "",
        "city": city.strip() if city else "",
        "state": state.strip().upper() if state else "",
        "avatar_url": avatar_url,
    }

    try:
        supabase.table("profiles").upsert(data).execute()
        return {"success": True, "message": "Perfil salvo com sucesso."}

    except Exception as e:
        error_message = str(e).lower()

        if "duplicate" in error_message and "cpf" in error_message:
            return {"success": False, "message": "Este CPF já está cadastrado."}

        return {
            "success": False,
            "message": "Erro ao salvar perfil. Verifique os dados e tente novamente."
        }


def get_profile(user_id: str, access_token: str):
    supabase = get_authenticated_client(access_token)

    try:
        response = (
            supabase
            .table("profiles")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        profile = response.data[0]

        if not profile.get("full_name"):
            fallback_name = normalize_full_name(
                f"{profile.get('first_name', '')} {profile.get('last_name', '')}"
            )
            profile["full_name"] = fallback_name

        return profile

    except Exception:
        return None


def profile_exists(user_id: str, access_token: str) -> bool:
    return get_profile(user_id, access_token) is not None