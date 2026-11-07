import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MUSIC_DIR = ROOT / "assets" / "music"
CHOICE_FILE = ROOT / "config" / "music_choice.json"
SUPPORTED = {".mp3", ".wav", ".m4a", ".aac", ".ogg"}

def get_daily_music():
    MUSIC_DIR.mkdir(parents=True, exist_ok=True)
    if CHOICE_FILE.exists():
        saved = json.loads(CHOICE_FILE.read_text(encoding="utf-8"))
        path = ROOT / saved["path"]
        if path.is_file():
            return path
    tracks = sorted(p for p in MUSIC_DIR.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED)
    if not tracks:
        raise FileNotFoundError("Add a music track to assets/music.")
    selected = tracks[0]
    CHOICE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHOICE_FILE.write_text(json.dumps({"path": selected.relative_to(ROOT).as_posix()}, indent=2), encoding="utf-8")
    return selected
