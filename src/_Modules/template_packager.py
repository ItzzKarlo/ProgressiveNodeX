import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any


MANIFEST_FILE_NAME = "pnx.template.json"
PNX_PROJECT_FILE_NAME = "pnx.json"

IGNORED_DIRS = {
    ".git", ".idea", ".vscode", ".vs", ".venv", "venv",
    "env", "__pycache__", "node_modules", "dist", "build", "_Out",
    "bin", "obj",
}

IGNORED_FILES = {
    ".env", ".spec", ".db", ".secret", ".token", ".pyc", ".pyo"
}


def validate_zip_has_manifest(zip_path: Path) -> None:
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            names = archive.namelist()
    except zipfile.BadZipFile:
        raise ValueError("Template file is not a valid zip archive.")

    if MANIFEST_FILE_NAME not in names:
        raise ValueError(f"Template zip must contain {MANIFEST_FILE_NAME} at the zip root.")


def should_ignore(path: Path) -> bool:
    if path.name in IGNORED_FILES:
        return True

    return any(part in IGNORED_DIRS for part in path.parts)


def read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def find_first_value(data: Any, possible_keys: list[str]) -> str | None:
    if isinstance(data, dict):
        for key in possible_keys:
            value = data.get(key)

            if isinstance(value, str) and value.strip():
                return value.strip()

        for value in data.values():
            found = find_first_value(value, possible_keys)

            if found:
                return found

    if isinstance(data, list):
        for value in data:
            found = find_first_value(value, possible_keys)

            if found:
                return found

    return None


def prettify_name(value: str) -> str:
    return (
        value.replace("-", " ")
        .replace("_", " ")
        .strip()
        .title()
    )


def detect_language(source_dir: Path, pnx_data: dict[str, Any]) -> str:
    from_pnx = find_first_value(
        pnx_data,
        ["language", "LANGUAGE", "project_language"],
    )

    if from_pnx:
        return from_pnx

    checks = [
        ("Python", ["*.py", "requirements.txt", "pyproject.toml"]),
        ("JavaScript", ["*.js", "package.json"]),
        ("TypeScript", ["*.ts", "tsconfig.json"]),
        ("C#", ["*.cs", "*.csproj"]),
        ("Java", ["*.java", "pom.xml", "build.gradle"]),
        ("Go", ["*.go", "go.mod"]),
        ("Rust", ["*.rs", "Cargo.toml"]),
    ]

    for language, patterns in checks:
        for pattern in patterns:
            if list(source_dir.rglob(pattern)):
                return language

    return "Unknown"


def detect_entrypoint(source_dir: Path, pnx_data: dict[str, Any]) -> str:
    from_pnx = find_first_value(
        pnx_data,
        ["entrypoint", "entry", "ENTRYPOINT", "main"],
    )

    if from_pnx:
        return from_pnx

    candidates = [
        "main.py",
        "app.py",
        "server.py",
        "index.js",
        "main.js",
        "src/main.py",
        "src/app.py",
        "src/index.js",
        "package.json",
    ]

    for candidate in candidates:
        if (source_dir / candidate).exists():
            return candidate

    return "."


def create_generated_manifest(source_dir: Path) -> dict[str, Any]:
    pnx_data = read_json_file(source_dir / PNX_PROJECT_FILE_NAME)

    fallback_name = source_dir.name

    name = find_first_value(
        pnx_data,
        ["name", "NAME", "project_name"],
    ) or fallback_name

    description = find_first_value(
        pnx_data,
        ["description", "DESCRIPTION", "project_description"],
    ) or f"Marketplace template generated from {prettify_name(fallback_name)}."

    framework = find_first_value(
        pnx_data,
        ["framework", "FRAMEWORK"],
    )

    language = detect_language(source_dir, pnx_data)
    entrypoint = detect_entrypoint(source_dir, pnx_data)

    tags = ["progressivenodex", "template"]

    if language and language != "Unknown":
        tags.append(language.lower())

    if framework:
        tags.append(framework.lower())

    return {
        "name": fallback_name,
        "display_name": prettify_name(fallback_name),
        "description": description,
        "language": language,
        "version": "1.0.0",
        "entrypoint": entrypoint,
        "framework": framework or "",
        "tags": tags,
        "generated_by": "ProgressiveNodeX CLI",
        "pnx_template_version": "1",
    }


def create_template_zip_from_folder(source_dir: Path) -> Path:
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".zip",
        prefix="pnx-template-",
    )

    temp_zip_path = Path(temp_file.name)
    temp_file.close()

    existing_manifest_path = source_dir / MANIFEST_FILE_NAME
    should_generate_manifest = not existing_manifest_path.exists()

    with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        if should_generate_manifest:
            generated_manifest = create_generated_manifest(source_dir)

            archive.writestr(
                MANIFEST_FILE_NAME,
                json.dumps(generated_manifest, indent=4),
            )

        for path in source_dir.rglob("*"):
            relative_path = path.relative_to(source_dir)

            if should_ignore(relative_path):
                continue

            if path.is_file():
                archive.write(path, relative_path.as_posix())

    validate_zip_has_manifest(temp_zip_path)

    return temp_zip_path


def prepare_template_archive(source_path: Path) -> tuple[Path, bool]:
    if not source_path.exists():
        raise ValueError(f"Template path does not exist: {source_path}")

    if source_path.is_file():
        if source_path.suffix.lower() != ".zip":
            raise ValueError("Template file must be a .zip archive.")

        validate_zip_has_manifest(source_path)
        return source_path, False

    if source_path.is_dir():
        return create_template_zip_from_folder(source_path), True

    raise ValueError("Template path must be either a folder or a .zip file.")