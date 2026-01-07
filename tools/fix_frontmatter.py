#!/usr/bin/env python3
"""
Corrige el front matter de los posts que tienen --- pegado sin salto de línea
"""

import re
from pathlib import Path

def fix_frontmatter(file_path):
    """Corrige el front matter de un archivo"""
    content = file_path.read_text(encoding='utf-8')
    
    # Buscar patrón: source_url seguido de ---sin salto de línea
    pattern = r'(source_url:\s*"[^"]+")---'
    
    if re.search(pattern, content):
        # Reemplazar con salto de línea antes de ---
        fixed_content = re.sub(pattern, r'\1\n---', content)
        file_path.write_text(fixed_content, encoding='utf-8')
        return True
    return False

def main():
    posts_dir = Path(__file__).parent.parent / '_posts'
    fixed_count = 0
    
    for md_file in posts_dir.rglob('*.md'):
        if fix_frontmatter(md_file):
            fixed_count += 1
            print(f"✓ {md_file.relative_to(posts_dir.parent)}")
    
    print(f"\n✅ {fixed_count} archivos corregidos")

if __name__ == '__main__':
    main()
