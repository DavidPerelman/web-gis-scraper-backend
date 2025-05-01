# server/utils/paths.py

from pathlib import Path


def get_project_root(marker_file: str = "requirements.txt") -> Path:
    path = Path(__file__).resolve()
    for parent in path.parents:
        print(f"🔍 Looking for {marker_file} in: {parent}")
        if (parent / marker_file).exists():
            print(f"✅ Found {marker_file} in: {parent}")
            return parent
    raise FileNotFoundError(f"Project root with '{marker_file}' not found.")
