from pathlib import Path

from src._Modules.meta_data import Metadata, CommandVersion, CommandHelp
from src._Modules.command_registry import CommandRegistry


@CommandRegistry.register
class SearchCommand(Metadata):
    name = "search"
    aliases = ["--search"]
    description = "Searches available project templates."
    version = CommandVersion.RELEASE
    command_help = CommandHelp(
        syntax="ProgressiveNodeX search [template]",
        usage="Lists all templates or searches for a specific template.",
        output="Displays matching template information and structure."
    )

    def run(self):
        templates_dir = self.get_templates_dir()

        if not templates_dir.exists():
            print("Templates folder not found.")
            return

        query = self.get_query()

        if query is None:
            self.list_all_templates(templates_dir)
            return

        self.search_template(templates_dir, query)

    def get_templates_dir(self) -> Path:
        return Path(__file__).resolve().parents[1] / "templates" / "apps"

    def get_query(self) -> str | None:
        for index, arg in enumerate(self.args):
            if arg in [self.name, *self.aliases]:
                if index + 1 < len(self.args):
                    return self.args[index + 1].lower()

        return None

    def list_all_templates(self, templates_dir: Path):
        templates = [
            item.name
            for item in templates_dir.iterdir()
            if item.is_dir()
        ]

        if not templates:
            print("No templates available.")
            return

        print("Available templates:")
        print()

        for template in templates:
            print(f"- {template}")

    def search_template(self, templates_dir: Path, query: str):
        matches = [
            item
            for item in templates_dir.iterdir()
            if item.is_dir() and query in item.name.lower()
        ]

        if not matches:
            print(f"No template found for: {query}")
            return

        for template_path in matches:
            self.print_template_info(template_path)

    def print_template_info(self, template_path: Path):
        print()
        print(f"Template: {template_path.name}")
        print(f"Path: {template_path}")
        print()

        print("Structure:")
        self.print_tree(template_path)

        print()
        print("Info:")
        print(f"- Files: {self.count_files(template_path)}")
        print(f"- Folders: {self.count_folders(template_path)}")
        print(f"- Main language: {self.detect_language(template_path)}")

    def print_tree(self, root: Path, prefix: str = ""):
        items = sorted(root.iterdir(), key=lambda path: (path.is_file(), path.name.lower()))

        for index, path in enumerate(items):
            connector = "└── " if index == len(items) - 1 else "├── "
            print(prefix + connector + path.name)

            if path.is_dir():
                extension = "    " if index == len(items) - 1 else "│   "
                self.print_tree(path, prefix + extension)

    def count_files(self, root: Path) -> int:
        return sum(1 for item in root.rglob("*") if item.is_file())

    def count_folders(self, root: Path) -> int:
        return sum(1 for item in root.rglob("*") if item.is_dir())

    def detect_language(self, template_path: Path) -> str:
        extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".cs": "C#",
            ".html": "HTML",
            ".css": "CSS",
            ".vue": "Vue",
            ".rs": "Rust",
            ".go": "Go",
            ".java": "Java"
        }

        found = {}

        for file in template_path.rglob("*"):
            if file.is_file() and file.suffix in extensions:
                language = extensions[file.suffix]
                found[language] = found.get(language, 0) + 1

        if not found:
            return "Unknown"

        return max(found, key=found.get)