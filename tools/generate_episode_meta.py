#!/usr/bin/env python3
import argparse
import os
import shutil
import sys
import subprocess
from pathlib import Path


def human_duration_hms(seconds: float) -> str:
    s = int(round(seconds))
    h = s // 3600
    m = (s % 3600) // 60
    sec = s % 60
    return f"{h}:{m:02d}:{sec:02d}"


def get_duration_seconds_ffprobe(path: str):
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        out = subprocess.check_output([
            ffprobe, "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=nk=1:nw=1",
            path
        ], stderr=subprocess.STDOUT, text=True).strip()
        return float(out)
    except Exception:
        return None


def get_duration_seconds_mutagen(path: str):
    try:
        from mutagen.mp3 import MP3  # type: ignore
    except Exception:
        return None
    try:
        audio = MP3(path)
        return float(audio.info.length)
    except Exception:
        return None


def derive_audio_url(mp3_path: Path, repo_root: Path) -> str | None:
    try:
        rel = mp3_path.resolve().relative_to(repo_root.resolve())
    except Exception:
        rel = Path(os.path.normpath(mp3_path))
    parts = rel.as_posix()
    if "/assets/mp3/" in "/" + parts:
        # ensure leading slash
        url = "/" + parts.lstrip("/")
        return url
    return None


def main():
    parser = argparse.ArgumentParser(description="Genera snippet YAML con audio_length y duration para un MP3.")
    parser.add_argument("mp3", help="Ruta al archivo MP3, p.ej. assets/mp3/2026/2026-01-07-mi-episodio.mp3")
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1], help="Raíz del repo para derivar audio_url (por defecto, dos niveles arriba de este script)")
    args = parser.parse_args()

    mp3_path = Path(args.mp3)
    if not mp3_path.exists():
        print(f"ERROR: No existe el archivo: {mp3_path}", file=sys.stderr)
        sys.exit(2)

    # Bytes
    size = os.path.getsize(mp3_path)

    # Duración
    duration_seconds = get_duration_seconds_ffprobe(str(mp3_path))
    if duration_seconds is None:
        duration_seconds = get_duration_seconds_mutagen(str(mp3_path))
    duration_hms = human_duration_hms(duration_seconds) if duration_seconds is not None else None

    # audio_url derivado si el path está bajo assets/mp3
    repo_root = Path(args.repo_root)
    audio_url = derive_audio_url(mp3_path, repo_root)

    # Emitir snippet YAML listo para pegar
    print("# --- Pega esto en el front matter del post ---")
    if audio_url:
        print(f"audio_url: \"{audio_url}\"")
    else:
        print("# audio_url: \"/assets/mp3/YYYY/YYYY-MM-DD-slug.mp3\"  # ajusta la ruta según corresponda")
    print("audio_type: \"audio/mpeg\"")
    print(f"audio_length: {size}")
    if duration_hms:
        print(f"duration: \"{duration_hms}\"")
    else:
        print("# duration: \"H:MM:SS\"  # instala ffmpeg (ffprobe) o la librería mutagen para calcularla")

    # Información auxiliar a stderr
    if duration_seconds is None:
        print("Nota: no pude calcular la duración. Instala ffmpeg (ffprobe) o 'pip install mutagen'.", file=sys.stderr)


if __name__ == "__main__":
    main()
