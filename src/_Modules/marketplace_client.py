import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from src._Modules.marketplace_auth import get_api_base_url


class MarketplaceApiError(Exception):
    pass


def extract_template_slug(template_ref: str) -> str:
    value = template_ref.strip()

    if not value:
        raise MarketplaceApiError("Template name or URL cannot be empty.")

    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        parts = [part for part in parsed.path.split("/") if part]

        if not parts:
            raise MarketplaceApiError("Could not find template slug in URL.")

        return parts[-1]

    return value


def _build_url(path: str) -> str:
    base_url = get_api_base_url()
    clean_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url}{clean_path}"


def _read_error_message(error: HTTPError) -> str:
    try:
        raw = error.read().decode("utf-8")
        payload = json.loads(raw)

        if isinstance(payload, dict):
            return str(payload.get("detail") or raw)

        return raw
    except Exception:
        return str(error)


def request_json(
    method: str,
    path: str,
    data: dict | None = None,
    token: str | None = None,
) -> dict | list:
    headers = {
        "Accept": "application/json",
    }

    body = None

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(
        _build_url(path),
        data=body,
        headers=headers,
        method=method.upper(),
    )

    try:
        with urlopen(request, timeout=30) as response:
            raw = response.read()

            if not raw:
                return {}

            return json.loads(raw.decode("utf-8"))

    except HTTPError as error:
        raise MarketplaceApiError(_read_error_message(error))
    except URLError as error:
        raise MarketplaceApiError(f"Could not reach marketplace API: {error.reason}")


def login(username_or_email: str, password: str) -> dict:
    return request_json(
        "POST",
        "/auth/login",
        data={
            "username_or_email": username_or_email,
            "password": password,
        },
    )


def get_me(token: str) -> dict:
    return request_json(
        "GET",
        "/auth/me",
        token=token,
    )


def search_templates(query: str) -> dict:
    return request_json(
        "GET",
        f"/templates/search?q={quote(query)}",
    )


def get_template(template_ref: str) -> dict:
    slug = extract_template_slug(template_ref)

    return request_json(
        "GET",
        f"/templates/{quote(slug)}",
    )


def download_template(template_ref: str, output_path: Path) -> Path:
    slug = extract_template_slug(template_ref)

    request = Request(
        _build_url(f"/templates/{quote(slug)}/download"),
        method="GET",
    )

    try:
        with urlopen(request, timeout=60) as response:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(response.read())
            return output_path

    except HTTPError as error:
        raise MarketplaceApiError(_read_error_message(error))
    except URLError as error:
        raise MarketplaceApiError(f"Could not reach marketplace API: {error.reason}")


def upload_template(zip_path: Path, template_name: str, token: str) -> dict:
    if not zip_path.exists() or not zip_path.is_file():
        raise MarketplaceApiError(f"Template archive not found: {zip_path}")

    boundary = f"----PNXMarketplaceBoundary{uuid4().hex}"
    line_break = "\r\n"

    body = bytearray()

    def add_text_field(name: str, value: str) -> None:
        body.extend(f"--{boundary}{line_break}".encode("utf-8"))
        body.extend(
            f'Content-Disposition: form-data; name="{name}"{line_break}{line_break}'.encode("utf-8")
        )
        body.extend(value.encode("utf-8"))
        body.extend(line_break.encode("utf-8"))

    def add_file_field(name: str, path: Path) -> None:
        filename = path.name

        body.extend(f"--{boundary}{line_break}".encode("utf-8"))
        body.extend(
            (
                f'Content-Disposition: form-data; name="{name}"; '
                f'filename="{filename}"{line_break}'
            ).encode("utf-8")
        )
        body.extend(f"Content-Type: application/zip{line_break}{line_break}".encode("utf-8"))
        body.extend(path.read_bytes())
        body.extend(line_break.encode("utf-8"))

    add_text_field("template_name", template_name)
    add_file_field("template_archive", zip_path)
    body.extend(f"--{boundary}--{line_break}".encode("utf-8"))

    request = Request(
        _build_url("/templates"),
        data=bytes(body),
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            raw = response.read()
            return json.loads(raw.decode("utf-8"))

    except HTTPError as error:
        raise MarketplaceApiError(_read_error_message(error))
    except URLError as error:
        raise MarketplaceApiError(f"Could not reach marketplace API: {error.reason}")
    
def delete_marketplace_template(template_ref: str, token: str) -> dict:
    slug = extract_template_slug(template_ref)

    return request_json(
        "DELETE",
        f"/templates/{quote(slug)}",
        token=token,
    )


def rename_marketplace_template(template_ref: str, new_template_name: str, token: str) -> dict:
    slug = extract_template_slug(template_ref)

    return request_json(
        "PATCH",
        f"/templates/{quote(slug)}",
        data={"template_name": new_template_name},
        token=token,
    )