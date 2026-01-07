#!/usr/bin/env python3
"""Recalcula audio_length leyendo el MP3 local y actualiza el front matter.

- Busca posts en _posts/**/*.md
- Lee audio_url del front matter
- Si audio_url apunta a /assets/mp3/... calcula bytes del archivo local
- Actualiza (o inserta) audio_length: <bytes>

Uso:
  python3 tools/recompute_audio_length.py
  python3 tools/recompute_audio_length.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n(.*)\Z", re.DOTALL)
KEY_RE = re.compile(r"^(?P<key>[A-Za-z0-9_\-]+):\s*(?P<value>.*)\s*$")


def parse_front_matter(text: str) -> tuple[list[str], str] | None:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return None
    fm = m.group(1)
    body = m.group(2)
    fm_lines = fm.splitlines()
    return fm_lines, body


def find_key_line(fm_lines: list[str], key: str) -> int | None:
    for i, line in enumerate(fm_lines):
        km = KEY_RE.match(line)
        if not km:
            continue
        if km.group("key") == key:
            return i
    return None


def get_key_value(fm_lines: list[str], key: str) -> str | None:
    idx = find_key_line(fm_lines, key)
    if idx is None:
        return None
    km = KEY_RE.match(fm_lines[idx])
    if not km:
        return None
    raw = km.group("value").strip()
    if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
        return raw[1:-1]
    if raw.startswith("'") and raw.endswith("'") and len(raw) >= 2:
        return raw[1:-1]
    return raw


def set_key_value(fm_lines: list[str], key: str, value: str) -> None:
    line = f"{key}: {value}"
    idx = find_key_line(fm_lines, key)
    if idx is not None:
        fm_lines[idx] = line
        return

    # Insertar cerca de audio_type/audio_url si existen; si no, al final.
    insert_after = None
    for anchor in ("audio_type", "audio_url", "description", "categories", "date", "title"):
        aidx = find_key_line(fm_lines, anchor)
        if aidx is not None:
            insert_after = aidx
            break

    if insert_after is None:
        fm_lines.append(line)
    else:
        fm_lines.insert(insert_after + 1, line)


def main() -> int:
    parser = argparse.ArgumentParser(description="Recalcula audio_length de todos los episodios con MP3 local.")
    parser.add_argument("--dry-run", action="store_true", help="No escribe archivos; solo muestra lo que cambiaría")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    posts_root = repo_root / "_posts"
    assets_root = repo_root / "assets"

    changed = 0
    missing = 0
    skipped = 0

    for md in sorted(posts_root.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        parsed = parse_front_matter(text)
        if not parsed:
            skipped += 1
            continue

        fm_lines, body = parsed
        audio_url = get_key_value(fm_lines, "audio_url")
        if not audio_url:
            skipped += 1
            continue

        # Solo recalcular para paths locales bajo /assets/
        if not audio_url.startswith("/"):
            skipped += 1
            continue
        if not audio_url.startswith("/assets/"):
            skipped += 1
            continue

        audio_path = (repo_root / audio_url.lstrip("/")).resolve()
        try:
            audio_path.relative_to(assets_root.resolve())
        except Exception:
            # Seguridad: solo tocar si cae dentro de assets/
            skipped += 1
            continue

        if not audio_path.exists():
            missing += 1
            continue

        size = os.path.getsize(audio_path)
        current = get_key_value(fm_lines, "audio_length")
        current_int = None
        if current is not None:
            try:
                current_int = int(current)
            except Exception:
                current_int = None

        if current_int == size:
            continue

        set_key_value(fm_lines, "audio_length", str(size))
        new_text = "---\n" + "\n".join(fm_lines) + "\n---\n\n" + body

        changed += 1
        if args.dry_run:
            print(f"Would update: {md.relative_to(repo_root)} (audio_length {current_int} -> {size})")
        else:
            md.write_text(new_text, encoding="utf-8")
            print(f"Updated: {md.relative_to(repo_root)} (audio_length {current_int} -> {size})")

    print("\nResumen")
    print(f"- Cambiados: {changed}")
    print(f"- MP3 faltante: {missing}")
    print(f"- Omitidos: {skipped}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
