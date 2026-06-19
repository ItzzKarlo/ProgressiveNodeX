from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]

version_py = ROOT / "src" / "assets" / "version_info_file.py"
version_txt = ROOT / "src" / "assets" / "version.txt"

spec = importlib.util.spec_from_file_location("version_info_file", version_py)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

version = module.__version__
year, month, build = map(int, version.split("."))

content = f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({year}, {month}, {build}, 1),
    prodvers=({year}, {month}, {build}, 1),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('CompanyName', 'KarloDevelopingStudios'),
          StringStruct('FileDescription', 'ProgressiveNodeX5 Application File'),
          StringStruct('FileVersion', '{version}'),
          StringStruct('InternalName', 'ProgressiveNodeX5'),
          StringStruct('OriginalFilename', 'ProgressiveNodeX.exe'),
          StringStruct('ProductName', 'ProgressiveNodeX V5'),
          StringStruct('ProductVersion', '{version}')
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""

version_txt.write_text(content, encoding="utf-8")