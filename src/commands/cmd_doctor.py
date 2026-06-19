import json
import shutil
import subprocess
from pathlib import Path

from src.assets.headers import header_small
from src._Modules.meta_data import Metadata, CommandHelp, CommandVersion
from src._Modules.command_registry import CommandRegistry


@CommandRegistry.register
class DoctorCommand(Metadata):
    name = "doctor"
    aliases = ["--doctor"]

    category = "Diagnostics"
    description = "Check project health"

    version = CommandVersion.DEV
    command_help = CommandHelp(
        syntax="ProgressiveNodeX doctor [--file <pnx.json>]",
        usage="Checks project configuration, runtime tools, entrypoint, and scripts.",
        output="Prints warnings and errors found in the project setup."
    )

    def __init__(self, args: list[str] | None = None):
        self.args = args or []
        self.errors = []
        self.warnings = []

    def run(self):
        print(header_small)
        print()
        print("═══════════════════════════════════════════════════════════════")
        print("ProgressiveNodeX Doctor")
        print("═══════════════════════════════════════════════════════════════")
        print()

        pnx_file = self.get_pnx_file()

        if not pnx_file.exists():
            self.error(f"pnx.json not found: {pnx_file}")
            self.finish()
            return

        data = self.load_json(pnx_file)

        if data is None:
            self.finish()
            return

        project_dir = pnx_file.parent

        self.check_required_sections(data)
        self.check_entrypoint(data, project_dir)
        self.check_runtime_tools(data)
        self.check_build_config(data)
        self.check_serve_config(data)
        self.check_scripts(data)

        self.finish()

    def get_pnx_file(self) -> Path:
        if "--file" in self.args:
            index = self.args.index("--file")

            if index + 1 < len(self.args):
                return Path(self.args[index + 1])

        return Path.cwd() / "pnx.json"

    def load_json(self, path: Path) -> dict | None:
        try:
            self.ok(f"Loaded config: {path}")
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self.error(f"Invalid JSON: {path}")
            return None
        except Exception as error:
            self.error(f"Could not read pnx.json: {error}")
            return None

    def check_required_sections(self, data: dict):
        required = ["project", "runtime", "build", "serve", "scripts"]

        for section in required:
            if section in data:
                self.ok(f"Section found: {section}")
            else:
                self.warn(f"Missing section: {section}")

    def check_entrypoint(self, data: dict, project_dir: Path):
        runtime = data.get("runtime", {})
        entrypoint = runtime.get("entrypoint")

        if not entrypoint:
            self.warn("No runtime.entrypoint defined.")
            return

        entrypoint_path = project_dir / entrypoint

        if entrypoint_path.exists():
            self.ok(f"Entrypoint exists: {entrypoint}")
        else:
            self.error(f"Entrypoint missing: {entrypoint}")

    def check_runtime_tools(self, data: dict):
        runtime = data.get("runtime", {})
        language = str(runtime.get("language", "")).lower()
        framework = str(runtime.get("framework", "")).lower()

        if language == "python":
            self.check_tool("python")
            self.check_tool("pip")

            if framework == "fastapi":
                self.check_python_module("fastapi")
                self.check_python_module("uvicorn")

            if framework == "flask":
                self.check_python_module("flask")

        elif language in ["javascript", "javascript/js", "node", "typescript"]:
            self.check_tool("node")
            self.check_tool("npm")

        elif language in ["csharp", "cs", "c#"]:
            self.check_tool("dotnet")

        else:
            self.warn(f"Unknown runtime language: {language}")

    def check_build_config(self, data: dict):
        build = data.get("build", {})

        output = build.get("output")
        targets = build.get("targets", [])

        if output:
            self.ok(f"Build output configured: {output}")
        else:
            self.warn("No build.output configured.")

        if targets:
            self.ok(f"Build targets: {', '.join(targets)}")
        else:
            self.warn("No build.targets configured.")

    def check_serve_config(self, data: dict):
        serve = data.get("serve", {})

        host = serve.get("host")
        port = serve.get("port")

        if host:
            self.ok(f"Serve host: {host}")
        else:
            self.warn("No serve.host configured.")

        if port:
            self.ok(f"Serve port: {port}")
        else:
            self.warn("No serve.port configured.")

    def check_scripts(self, data: dict):
        scripts = data.get("scripts", {})

        if not scripts:
            self.warn("No scripts configured.")
            return

        for name, command in scripts.items():
            if command:
                self.ok(f"Script configured: {name}")
            else:
                self.warn(f"Empty script: {name}")

    def check_tool(self, tool: str):
        if shutil.which(tool):
            self.ok(f"Tool available: {tool}")
        else:
            self.error(f"Tool missing: {tool}")

    def check_python_module(self, module: str):
        result = subprocess.run(
            ["python", "-c", f"import {module}"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            self.ok(f"Python module available: {module}")
        else:
            self.warn(f"Python module missing: {module}")

    def ok(self, message: str):
        print(f"[OK]      {message}")

    def warn(self, message: str):
        self.warnings.append(message)
        print(f"[WARN]    {message}")

    def error(self, message: str):
        self.errors.append(message)
        print(f"[ERROR]   {message}")

    def finish(self):
        print()
        print("═══════════════════════════════════════════════════════════════")

        if not self.errors and not self.warnings:
            print("Status: Healthy")
        elif self.errors:
            print(f"Status: Problems found - {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        else:
            print(f"Status: Mostly healthy - {len(self.warnings)} warning(s)")

        print("═══════════════════════════════════════════════════════════════")