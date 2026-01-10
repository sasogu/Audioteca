#!/usr/bin/env python3
"""
Actualiza los source_url de posts para que apunten a la nueva ubicación en GitHub Pages
"""

import re
from pathlib import Path

def update_source_url(post_path: Path, base_url: str) -> bool:
    """Actualiza el source_url de un post para que apunte a GitHub Pages"""
    content = post_path.read_text(encoding='utf-8')
    
    # Extraer información del nombre del archivo
    # Formato: YYYY-MM-DD-titulo-slug.md
    post_filename = post_path.stem  # sin .md
    parts = post_filename.split('-', 3)
    
    if len(parts) < 4:
        return False
    
    year, month, day, slug = parts[0], parts[1], parts[2], parts[3]
    
    # Construir nueva URL según el permalink configurado
    # permalink: /episodios/:year/:month/:day/:title/
    new_url = f"{base_url}/episodios/{year}/{month}/{day}/{slug}/"
    
    # Buscar y reemplazar source_url
    pattern = r'source_url:\s*"[^"]*"'
    replacement = f'source_url: "{new_url}"'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        post_path.write_text(new_content, encoding='utf-8')
        return True
    
    return False

def main():
    repo_root = Path(__file__).parent.parent
    posts_dir = repo_root / '_posts'
    
    # URL base del sitio
    base_url = "https://cszcm.github.io/Audioteca"
    
    updated = 0
    
    for post_path in posts_dir.rglob('*.md'):
        if update_source_url(post_path, base_url):
            updated += 1
            print(f"✓ {post_path.relative_to(repo_root)}")
    
    print(f"\n✅ {updated} posts actualizados")

if __name__ == '__main__':
    main()
