#!/usr/bin/env python3
"""
Actualiza los audio_url de posts para usar archivos locales en lugar de URLs remotas
"""

import re
from pathlib import Path

def update_audio_url(post_path: Path, repo_root: Path) -> bool:
    """Actualiza el audio_url de un post si el archivo local existe"""
    content = post_path.read_text(encoding='utf-8')
    
    # Buscar audio_url remoto
    match = re.search(r'audio_url:\s*"(https://[^"]+)"', content)
    if not match:
        return False
    
    remote_url = match.group(1)
    
    # Extraer nombre del archivo de la URL
    filename = remote_url.split('/')[-1]
    
    # Extraer año del nombre del archivo del post
    post_filename = post_path.name
    year = post_filename[:4]
    
    # Construir ruta local esperada
    local_path = repo_root / 'assets' / 'mp3' / year / f"{post_filename[:10]}-{filename}"
    
    # Si el archivo local no existe, intentar sin el prefijo de fecha
    if not local_path.exists():
        # Buscar cualquier archivo que coincida con el nombre base
        year_dir = repo_root / 'assets' / 'mp3' / year
        if year_dir.exists():
            for mp3_file in year_dir.glob('*.mp3'):
                if filename in mp3_file.name or mp3_file.name.endswith(filename):
                    local_path = mp3_file
                    break
    
    if not local_path.exists():
        print(f"  WARNING: archivo no encontrado para {post_path.name}")
        return False
    
    # Construir URL local
    local_url = f"/assets/mp3/{year}/{local_path.name}"
    
    # Reemplazar en el contenido
    new_content = content.replace(f'audio_url: "{remote_url}"', f'audio_url: "{local_url}"')
    
    if new_content != content:
        post_path.write_text(new_content, encoding='utf-8')
        return True
    
    return False

def main():
    repo_root = Path(__file__).parent.parent
    posts_dir = repo_root / '_posts'
    
    updated = 0
    not_found = 0
    
    for post_path in posts_dir.rglob('*.md'):
        if update_audio_url(post_path, repo_root):
            updated += 1
            print(f"✓ {post_path.relative_to(repo_root)}")
        elif 'media.blubrry.com' in post_path.read_text(encoding='utf-8'):
            not_found += 1
    
    print(f"\n✅ {updated} posts actualizados")
    if not_found > 0:
        print(f"⚠️  {not_found} posts con URLs remotas (archivos no encontrados localmente)")

if __name__ == '__main__':
    main()
