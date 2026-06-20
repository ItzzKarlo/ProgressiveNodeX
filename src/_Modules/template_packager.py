import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any


MANIFEST_FILE_NAME = "pnx.template.json"
PNX_PROJECT_FILE_NAME = "pnx.json"

IGNORED_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    ".vs",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "_Out",
    "bin",
    "obj",
}

IGNORED_FILES = {
    ".env",
    ".spec",
    ".db",
    ".secret",
    ".token",
    ".pyc",
    ".pyo",
}


def validate_zip_has_manifest(zip_path: Path) -> None:
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            names = archive.namelist()
    except zipfile.BadZipFile:
        raise ValueError("Template file is not a valid zip archive.")

    if MANIFEST_FILE_NAME not in names:
        raise ValueError(
            f"Template zip must contain {MANIFEST_FILE_NAME} at the zip root."
        )


def read_manifest_from_zip(zip_path: Path) -> dict[str, Any]:
    validate_zip_has_manifest(zip_path)

    with zipfile.ZipFile(zip_path, "r") as archive:
        try:
            raw_manifest = archive.read(MANIFEST_FILE_NAME)
            manifest = json.loads(raw_manifest.decode("utf-8"))
        except json.JSONDecodeError:
            raise ValueError(f"{MANIFEST_FILE_NAME} must contain valid JSON.")

    if not isinstance(manifest, dict):
        raise ValueError(f"{MANIFEST_FILE_NAME} must be a JSON object.")

    return manifest


def zip_has_pnx_json(zip_path: Path) -> bool:
    with zipfile.ZipFile(zip_path, "r") as archive:
        return PNX_PROJECT_FILE_NAME in archive.namelist()


def should_ignore(path: Path) -> bool:
    if path.name in IGNORED_FILES:
        return True

    if path.suffix in IGNORED_FILES:
        return True

    return any(part in IGNORED_DIRS for part in path.parts)


def read_json_file(path: Path) -> dict[str, Any]:
    if not path.exists() or not path.is_file():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if not isinstance(data, dict):
        return {}

    return data


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
        ("TypeScript", ["*.ts", "tsconfig.json"]),
        ("JavaScript", ["*.js", "package.json"]),
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


def detect_framework(source_dir: Path, pnx_data: dict[str, Any]) -> str:
    from_pnx = find_first_value(
        pnx_data,
        ["framework", "FRAMEWORK"],
    )

    if from_pnx:
        return from_pnx

    package_json = source_dir / "package.json"

    if package_json.exists():
        package_data = read_json_file(package_json)
        dependencies = {
            **package_data.get("dependencies", {}),
            **package_data.get("devDependencies", {}),
        }

        if "next" in dependencies:
            return "Next.js"

        if "react" in dependencies:
            return "React"

        if "vue" in dependencies:
            return "Vue"

        if "svelte" in dependencies:
            return "Svelte"

        return "Node"

    if (source_dir / "manage.py").exists():
        return "Django"

    if list(source_dir.rglob("app.py")):
        return "Python"

    if list(source_dir.rglob("*.csproj")):
        return "C#"

    return "unknown"


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

    return "main.py"


def default_start_command(manifest: dict[str, Any]) -> str:
    language = str(manifest.get("language") or "").lower()
    framework = str(manifest.get("framework") or "").lower()
    entrypoint = str(
        manifest.get("entrypoint") or manifest.get("entry") or "main.py"
    ).strip()

    if entrypoint in {"", ".", "./"}:
        entrypoint = "main.py"

    if (
        entrypoint == "package.json"
        or framework in {"react", "vue", "svelte", "next", "next.js", "nextjs", "node"}
        or language in {"javascript", "typescript"}
    ):
        return "npm run dev"

    if language in {"c#", "csharp"} or framework in {"cs-desktop", "csharp-desktop"}:
        return "dotnet run"

    if framework == "fastapi" and entrypoint.endswith(".py"):
        module_name = (
            entrypoint
            .removesuffix(".py")
            .replace("/", ".")
            .replace("\\", ".")
        )

        return f"uvicorn {module_name}:app --reload"

    if language == "python" or entrypoint.endswith(".py"):
        return f"python {entrypoint}"

    return f"python {entrypoint}"


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

    language = detect_language(source_dir, pnx_data)
    framework = detect_framework(source_dir, pnx_data)
    entrypoint = detect_entrypoint(source_dir, pnx_data)

    tags = ["progressivenodex", "template"]

    if language and language.lower() != "unknown":
        tags.append(language.lower())

    if framework and framework.lower() != "unknown":
        tags.append(framework.lower())

    return {
        "name": name,
        "display_name": prettify_name(name),
        "description": description,
        "language": language,
        "version": "1.0.0",
        "entrypoint": entrypoint,
        "framework": framework,
        "tags": tags,
        "generated_by": "ProgressiveNodeX CLI",
        "pnx_template_version": "1",
    }


def create_generated_pnx_json(manifest: dict[str, Any]) -> dict[str, Any]:
    name = str(manifest.get("name") or "pnx-template").strip()
    description = str(
        manifest.get("description") or "ProgressiveNodeX marketplace template."
    ).strip()
    version = str(manifest.get("version") or "1.0.0").strip()
    language = str(manifest.get("language") or "unknown").strip()
    framework = str(manifest.get("framework") or "marketplace").strip()
    entrypoint = str(
        manifest.get("entrypoint") or manifest.get("entry") or "main.py"
    ).strip()

    if entrypoint in {"", ".", "./"}:
        entrypoint = "main.py"

    return {
        "project": {
            "name": name,
            "description": description,
            "version": version,
            "mode": {
                "debug": True,
                "development": True,
                "release": False,
            },
            "template_info": {
                "template_used": True,
                "template_name": name,
                "template_version": version,
            },
        },
        "runtime": {
            "language": language,
            "framework": framework,
            "entrypoint": entrypoint,
        },
        "build": {
            "targets": ["windows", "linux", "macos"],
            "output": "dist",
        },
        "serve": {
            "host": "127.0.0.1",
            "port": 3000,
            "reload": True,
        },
        "scripts": {
            "start": default_start_command(manifest),
            "test": "python -m pytest",
            "version": "ProgressiveNodeX --version",
            "help": "ProgressiveNodeX --help",
        },
    }


def create_temp_zip_path() -> Path:
    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".zip",
        prefix="pnx-template-",
    )

    temp_zip_path = Path(temp_file.name)
    temp_file.close()

    return temp_zip_path


def ensure_zip_has_pnx_json(zip_path: Path) -> tuple[Path, bool]:
    manifest = read_manifest_from_zip(zip_path)

    if zip_has_pnx_json(zip_path):
        return zip_path, False

    temp_zip_path = create_temp_zip_path()

    with zipfile.ZipFile(zip_path, "r") as source_archive:
        with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED) as output_archive:
            for item in source_archive.infolist():
                normalized_name = item.filename.replace("\\", "/")

                if normalized_name.startswith("/") or ".." in normalized_name.split("/"):
                    raise ValueError(f"Unsafe file path in template archive: {item.filename}")

                if item.is_dir():
                    output_archive.writestr(item, b"")
                    continue

                output_archive.writestr(
                    item,
                    source_archive.read(item.filename),
                )

            output_archive.writestr(
                PNX_PROJECT_FILE_NAME,
                json.dumps(create_generated_pnx_json(manifest), indent=4),
            )

    validate_zip_has_manifest(temp_zip_path)

    return temp_zip_path, True


def create_template_zip_from_folder(source_dir: Path) -> Path:
    temp_zip_path = create_temp_zip_path()

    existing_manifest_path = source_dir / MANIFEST_FILE_NAME
    existing_pnx_path = source_dir / PNX_PROJECT_FILE_NAME

    should_generate_manifest = not existing_manifest_path.exists()

    if should_generate_manifest:
        manifest = create_generated_manifest(source_dir)
    else:
        manifest = read_json_file(existing_manifest_path)

        if not manifest:
            manifest = create_generated_manifest(source_dir)

    with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        if should_generate_manifest:
            archive.writestr(
                MANIFEST_FILE_NAME,
                json.dumps(manifest, indent=4),
            )

        if not existing_pnx_path.exists():
            archive.writestr(
                PNX_PROJECT_FILE_NAME,
                json.dumps(create_generated_pnx_json(manifest), indent=4),
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

        return ensure_zip_has_pnx_json(source_path)

    if source_path.is_dir():
        return create_template_zip_from_folder(source_path), True

    raise ValueError("Template path must be either a folder or a .zip file.")