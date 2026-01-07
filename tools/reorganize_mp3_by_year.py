#!/usr/bin/env python3

from __future__ import annotations

import re
import shutil
from pathlib import Path


def _read_front_matter(md: str) -> tuple[dict, str, str]:
    """Devuelve (front_matter_dict, front_matter_text, body)"""
    if not md.startswith("---"):
        return {}, "", md
    parts = md.split("---", 2)
    if len(parts) < 3:
        return {}, "", md
    
    fm_text = parts[1]
    body = parts[2]
    
    # Parse manual simple del YAML
    fm_dict = {}
    for line in fm_text.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            fm_dict[key] = val
    
    return fm_dict, fm_text, body


def _update_front_matter(fm_text: str, key: str, new_value: str) -> str:
    """Actualiza un campo en el texto YAML del front matter"""
    lines = fm_text.splitlines()
    updated = []
    found = False
    
    for line in lines:
        if line.strip().startswith(f"{key}:"):
            # Mantener la indentación original
            indent = len(line) - len(line.lstrip())
            updated.append(" " * indent + f'{key}: "{new_value}"')
            found = True
        else:
            updated.append(line)
    
    return "\n".join(updated)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    posts_dir = repo_root / "_posts"
    mp3_dir = repo_root / "assets" / "mp3"
    
    moves = []  # (post_path, old_mp3_path, new_mp3_path, new_audio_url, year)
    
    # 1. Analizar posts y determinar movimientos
    for post_path in sorted(posts_dir.glob("*.md")):
        content = post_path.read_text(encoding="utf-8")
        fm_dict, fm_text, body = _read_front_matter(content)
        
        audio_url = fm_dict.get("audio_url", "")
        date = fm_dict.get("date", "")
        
        if not audio_url or not audio_url.startswith("/assets/mp3/"):
            continue
        
        # Extraer año de la fecha
        year_match = re.match(r"(\d{4})", date)
        if not year_match:
            print(f"SKIP: {post_path.name} - no se pudo extraer año de '{date}'")
            continue
        
        year = year_match.group(1)
        
        # Si ya está en una subcarpeta de año, skip
        if f"/assets/mp3/{year}/" in audio_url:
            continue
        
        # Determinar paths
        filename = Path(audio_url).name
        old_mp3_path = repo_root / audio_url.lstrip("/")
        new_mp3_path = mp3_dir / year / filename
        new_audio_url = f"/assets/mp3/{year}/{filename}"
        
        if not old_mp3_path.exists():
            print(f"SKIP: {post_path.name} - MP3 no existe: {old_mp3_path}")
            continue
        
        moves.append((post_path, old_mp3_path, new_mp3_path, new_audio_url, year, fm_text, body))
    
    if not moves:
        print("No hay archivos para reorganizar.")
        return 0
    
    print(f"\nSe moverán {len(moves)} archivos:\n")
    
    # 2. Ejecutar movimientos y actualizaciones
    for post_path, old_mp3_path, new_mp3_path, new_audio_url, year, fm_text, body in moves:
        # Crear directorio del año
        new_mp3_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Mover MP3
        shutil.move(str(old_mp3_path), str(new_mp3_path))
        print(f"✓ {old_mp3_path.name} → {year}/{old_mp3_path.name}")
        
        # Actualizar post
        new_fm_text = _update_front_matter(fm_text, "audio_url", new_audio_url)
        new_content = f"---{new_fm_text}---{body}"
        post_path.write_text(new_content, encoding="utf-8")
    
    print(f"\n✓ Reorganizados {len(moves)} MP3 por año")
    print("✓ Actualizados los posts con las nuevas rutas")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
