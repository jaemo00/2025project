from pathlib import Path

BASE_DIR=Path(__file__).resolve().parent
TEMP_DIR = BASE_DIR / "temp"
FRONTEND_DIR = BASE_DIR / "frontend" # frontend 폴더 위치
DIST_DIR = FRONTEND_DIR / "dist"
ASSETS_DIR = DIST_DIR / "assets"