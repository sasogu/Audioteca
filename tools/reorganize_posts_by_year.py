#!/usr/bin/env python3

from __future__ import annotations

import re
import shutil
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    posts_dir = repo_root / "_posts"
    
    # Solo procesar archivos .md directamente en _posts/, no en subdirectorios
    posts_to_move = []
    
    for post_path in sorted(posts_dir.glob("*.md")):
        if not post_path.is_file():
            continue
        
        # Extraer año del nombre del archivo (formato: YYYY-MM-DD-titulo.md)
        filename = post_path.name
        year_match = re.match(r"(\d{4})-", filename)
        
        if not year_match:
            print(f"SKIP: {filename} - no tiene formato YYYY-MM-DD-...")
            continue
        
        year = year_match.group(1)
        year_dir = posts_dir / year
        new_path = year_dir / filename
        
        posts_to_move.append((post_path, new_path, year))
    
    if not posts_to_move:
        print("No hay posts para reorganizar.")
        return 0
    
    print(f"\nSe moverán {len(posts_to_move)} posts a carpetas por año:\n")
    
    # Agrupar por año para el resumen
    by_year = {}
    for _, _, year in posts_to_move:
        by_year[year] = by_year.get(year, 0) + 1
    
    for year in sorted(by_year.keys()):
        print(f"  {year}/  ({by_year[year]} posts)")
    
    print()
    
    # Ejecutar movimientos
    for post_path, new_path, year in posts_to_move:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(post_path), str(new_path))
    
    print(f"✓ Reorganizados {len(posts_to_move)} posts por año en _posts/YYYY/")
    print("✓ Jekyll los detectará automáticamente en los subdirectorios")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
