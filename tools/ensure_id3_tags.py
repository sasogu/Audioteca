#!/usr/bin/env python3

from __future__ import annotations

import re
from pathlib import Path

import yaml
from mutagen.id3 import ID3, ID3NoHeaderError, TALB, TDRC, TIT2, TPE1


def _read_front_matter(md: str) -> dict:
    # Extrae YAML entre --- ... --- al principio
    if not md.startswith("---"):
        return {}
    parts = md.split("---", 2)
    if len(parts) < 3:
        return {}
    fm = parts[1]
    data = yaml.safe_load(fm) or {}
    if not isinstance(data, dict):
        return {}
    return data


def _normalize_audio_url(audio_url: str) -> str:
    audio_url = audio_url.strip()
    # quitamos posible baseurl absoluto
    audio_url = re.sub(r"^https?://[^/]+", "", audio_url)
    return audio_url


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    config = yaml.safe_load((repo_root / "_config.yml").read_text(encoding="utf-8")) or {}
    podcast = (config.get("podcast") or {}) if isinstance(config, dict) else {}

    default_artist = podcast.get("author") or config.get("title") or "Audioteca"
    default_album = config.get("title") or "Audioteca"

    # Mapea filename -> metadata desde posts
    meta_by_filename: dict[str, dict] = {}
    posts_dir = repo_root / "_posts"
    for post_path in sorted(posts_dir.glob("*.md")):
        fm = _read_front_matter(post_path.read_text(encoding="utf-8"))
        audio_url = fm.get("audio_url")
        if not isinstance(audio_url, str) or not audio_url:
            continue
        audio_url = _normalize_audio_url(audio_url)
        if not audio_url.startswith("/assets/mp3/"):
            continue
        filename = Path(audio_url).name
        meta_by_filename[filename] = {
            "title": fm.get("title"),
            "date": fm.get("date"),
        }

    mp3_dir = repo_root / "assets" / "mp3"
    changed = 0
    skipped = 0

    for mp3_path in sorted(mp3_dir.glob("*.mp3")):
        filename = mp3_path.name
        meta = meta_by_filename.get(filename, {})
        title = meta.get("title") or filename
        date = meta.get("date")

        try:
            tags = ID3(mp3_path)
        except ID3NoHeaderError:
            tags = ID3()

        # Si ya hay cabecera ID3, no pisamos; solo completamos mínimos.
        before_keys = set(tags.keys())

        if "TIT2" not in tags:
            tags.add(TIT2(encoding=3, text=str(title)))
        if "TPE1" not in tags:
            tags.add(TPE1(encoding=3, text=str(default_artist)))
        if "TALB" not in tags:
            tags.add(TALB(encoding=3, text=str(default_album)))
        if date and "TDRC" not in tags:
            tags.add(TDRC(encoding=3, text=str(date)))

        after_keys = set(tags.keys())
        if after_keys != before_keys:
            tags.save(mp3_path)
            changed += 1
        else:
            skipped += 1

    print(f"ID3 actualizados: {changed} | sin cambios: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
