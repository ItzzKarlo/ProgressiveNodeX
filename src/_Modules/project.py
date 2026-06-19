import json
from pathlib import Path

class Project:
    def __init__(self, data: dict, file_path: Path):
        self.data = data
        self.file_path = file_path
        self.root_dir = file_path.parent
    
    @staticmethod
    def load(path: Path | None = None):
        if path is None:
            path = Path.cwd() / "pnx.json"
        
        if path.is_dir():
            path = path / "pnx.json"
        
        if not path.exists():
            raise FileNotFoundError(f'pnx.json not found: {path}')
        
        data = json.loads(path.read_text(encoding='utf-8'))

        return Project(data, path)
    
    @property
    def name(self):
        return self.data.get("project", {}).get("name", "Unknown")

    @property
    def version(self):
        return self.data.get("project", {}).get("version", "Unknown")

    @property
    def language(self):
        return self.data.get("runtime", {}).get("language", "unknown")

    @property
    def framework(self):
        return self.data.get("runtime", {}).get("framework", "unknown")

    @property
    def entrypoint(self):
        return self.data.get("runtime", {}).get("entrypoint", "")

    @property
    def scripts(self):
        return self.data.get("scripts", {})

    def get_script(self, name: str):
        return self.scripts.get(name)