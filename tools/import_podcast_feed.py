#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any


NS = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
}


@dataclass(frozen=True)
class Episode:
    title: str
    link: str | None
    guid: str | None
    pub_date: dt.datetime | None
    description_html: str | None
    content_html: str | None
    enclosure_url: str | None
    enclosure_length: int | None
    enclosure_type: str | None
    itunes_duration: str | None
    itunes_explicit: str | None


def _slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "episodio"


def _strip_html(value: str) -> str:
    # Muy simple: suficiente para un resumen corto.
    value = re.sub(r"<script.*?>.*?</script>", "", value, flags=re.DOTALL | re.IGNORECASE)
    value = re.sub(r"<style.*?>.*?</style>", "", value, flags=re.DOTALL | re.IGNORECASE)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _remove_embedded_audio(html: str) -> str:
    # Quita reproductores embebidos en el HTML original.
    # En el sitio nuevo ya mostramos un <audio> consistente desde front matter.
    html = re.sub(r"<audio\b.*?</audio>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!--\[if\s+lt\s+IE\s+9\]>.*?<!\[endif\]-->", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"\s+", " ", html).strip()
    return html


def _parse_rfc822_date(value: str) -> dt.datetime | None:
    value = (value or "").strip()
    if not value:
        return None

    # Ej: Sat, 29 Nov 2025 07:17:57 +0000
    try:
        parsed = dt.datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %z")
        return parsed
    except ValueError:
        pass

    # Algunos feeds omiten segundos
    try:
        parsed = dt.datetime.strptime(value, "%a, %d %b %Y %H:%M %z")
        return parsed
    except ValueError:
        return None


def _safe_filename(name: str) -> str:
    name = name.replace("/", "-")
    name = re.sub(r"\s+", "-", name.strip())
    name = re.sub(r"[^A-Za-z0-9._-]", "", name)
    name = re.sub(r"-+", "-", name)
    return name or "audio.mp3"


def _basename_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    base = os.path.basename(parsed.path)
    base = _safe_filename(base)
    if not base.lower().endswith(".mp3"):
        # No siempre será mp3, pero en este caso lo esperamos.
        base = base + ".mp3"
    return base


def _download(url: str, dest: Path, *, overwrite: bool) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and not overwrite:
        return dest.stat().st_size

    tmp = dest.with_suffix(dest.suffix + ".part")
    if tmp.exists():
        tmp.unlink()

    req = urllib.request.Request(url, headers={"User-Agent": "AudiotecaImporter/1.0"})
    try:
        with urllib.request.urlopen(req) as resp:
            with open(tmp, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
        tmp.replace(dest)
        return dest.stat().st_size
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise


def _write_failures(path: Path, failures: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z")

    lines: list[str] = []
    lines.append(f"Reporte de fallos de descarga (UTC): {now}")
    lines.append(f"Total fallos: {len(failures)}")
    lines.append("")
    lines.append("fecha\ttitulo\turl\terror")
    for f in failures:
        date_prefix = f.get("date") or ""
        title = (f.get("title") or "").replace("\t", " ").replace("\n", " ")
        url = (f.get("url") or "").replace("\t", " ").replace("\n", " ")
        error = (f.get("error") or "").replace("\t", " ").replace("\n", " ")
        lines.append(f"{date_prefix}\t{title}\t{url}\t{error}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_feed_xml(xml_bytes: bytes) -> list[Episode]:
    root = ET.fromstring(xml_bytes)
    channel = root.find("channel")
    if channel is None:
        raise ValueError("No se encontró <channel> en el RSS")

    episodes: list[Episode] = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip() or None
        guid = (item.findtext("guid") or "").strip() or None
        pub_date = _parse_rfc822_date(item.findtext("pubDate") or "")

        desc_el = item.find("description")
        description_html = desc_el.text if desc_el is not None else None

        content_el = item.find("content:encoded", NS)
        content_html = content_el.text if content_el is not None else None

        enclosure = item.find("enclosure")
        enclosure_url = enclosure.get("url") if enclosure is not None else None
        enclosure_type = enclosure.get("type") if enclosure is not None else None
        enclosure_length_raw = enclosure.get("length") if enclosure is not None else None
        enclosure_length = None
        if enclosure_length_raw:
            try:
                enclosure_length = int(enclosure_length_raw)
            except ValueError:
                enclosure_length = None

        itunes_duration = (item.findtext("itunes:duration", default="", namespaces=NS) or "").strip() or None
        itunes_explicit = (item.findtext("itunes:explicit", default="", namespaces=NS) or "").strip() or None

        if not title:
            # Evita entradas vacías.
            continue

        episodes.append(
            Episode(
                title=title,
                link=link,
                guid=guid,
                pub_date=pub_date,
                description_html=description_html,
                content_html=content_html,
                enclosure_url=enclosure_url,
                enclosure_length=enclosure_length,
                enclosure_type=enclosure_type,
                itunes_duration=itunes_duration,
                itunes_explicit=itunes_explicit,
            )
        )

    return episodes


def _yaml_bool(value: str | None, default: bool = False) -> str:
    if value is None:
        return "true" if default else "false"
    value = value.strip().lower()
    if value in {"true", "yes", "explicit"}:
        return "true"
    if value in {"false", "no", "clean", "not explicit"}:
        return "false"
    return "true" if default else "false"


def _format_post(
    ep: Episode,
    *,
    local_audio_url: str | None,
    audio_length: int | None,
    audio_type: str | None,
) -> str:
    pub = ep.pub_date
    if pub is None:
        pub = dt.datetime.now(dt.timezone.utc)

    description = None
    if ep.description_html:
        description = _strip_html(ep.description_html)
        description = (description[:240] + "…") if len(description) > 240 else description

    audio_url = local_audio_url or ep.enclosure_url

    lines: list[str] = []
    lines.append("---")
    lines.append(f'title: "{ep.title.replace("\"", "\\\"")}"')
    lines.append(f"date: {pub.strftime('%Y-%m-%d %H:%M:%S %z')}")
    lines.append('categories: ["podcast"]')
    if description:
        lines.append(f'description: "{description.replace("\"", "\\\"")}"')

    if audio_url:
        # En el sitio, preferimos rutas relativas a baseurl (empiezan por /)
        lines.append(f'audio_url: "{audio_url}"')
        lines.append(f'audio_type: "{(audio_type or ep.enclosure_type or "audio/mpeg")}"')
        lines.append(f"audio_length: {audio_length if audio_length is not None else (ep.enclosure_length or 0)}")

    if ep.itunes_duration:
        lines.append(f'duration: "{ep.itunes_duration}"')

    lines.append(f"explicit: {_yaml_bool(ep.itunes_explicit, default=False)}")

    if ep.link:
        lines.append(f'source_url: "{ep.link}"')

    lines.append("---")
    lines.append("")

    # Contenido
    if ep.description_html:
        lines.append("## Notas (importadas)")
        lines.append("")
        # Mantener HTML: Jekyll lo renderiza bien.
        lines.append(_remove_embedded_audio(ep.description_html.strip()))
        lines.append("")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Importa un feed RSS de podcast y genera posts para Jekyll.")
    parser.add_argument("--feed-url", default="https://www.daizansoriano.com/feed/podcast/", help="URL del feed RSS")
    parser.add_argument("--limit", type=int, default=0, help="Límite de episodios (0 = todos)")
    parser.add_argument("--download", action="store_true", help="Descargar MP3 a assets/mp3/")
    parser.add_argument("--overwrite", action="store_true", help="Sobrescribir mp3 existentes")
    parser.add_argument("--overwrite-posts", action="store_true", help="Sobrescribir posts existentes")
    parser.add_argument(
        "--failures-file",
        default="tools/import_failures.txt",
        help="Ruta del reporte de fallos de descarga (tab-separado).",
    )
    parser.add_argument("--dry-run", action="store_true", help="No escribe archivos")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    posts_dir = repo_root / "_posts"
    mp3_dir = repo_root / "assets" / "mp3"

    req = urllib.request.Request(args.feed_url, headers={"User-Agent": "AudiotecaImporter/1.0"})
    with urllib.request.urlopen(req) as resp:
        xml_bytes = resp.read()

    episodes = parse_feed_xml(xml_bytes)
    if args.limit and args.limit > 0:
        episodes = episodes[: args.limit]

    print(f"Episodios detectados: {len(episodes)}")

    failures: list[dict[str, Any]] = []
    seen_failure_keys: set[tuple[str, str, str]] = set()

    for ep in episodes:
        pub = ep.pub_date or dt.datetime.now(dt.timezone.utc)
        date_prefix = pub.strftime("%Y-%m-%d")
        slug = _slugify(ep.title)
        post_path = posts_dir / f"{date_prefix}-{slug}.md"

        # Si se pide descarga, intentamos asegurar el mp3 local aunque el post ya exista.
        if args.download and ep.enclosure_url:
            base = _basename_from_url(ep.enclosure_url)
            mp3_name = f"{date_prefix}-{base}"
            mp3_path = mp3_dir / mp3_name
            if not args.dry_run:
                try:
                    _download(ep.enclosure_url, mp3_path, overwrite=args.overwrite)
                except Exception as e:
                    key = (date_prefix, ep.title, ep.enclosure_url)
                    if key not in seen_failure_keys:
                        seen_failure_keys.add(key)
                        failures.append(
                            {
                                "date": date_prefix,
                                "title": ep.title,
                                "url": ep.enclosure_url,
                                "error": f"{type(e).__name__}: {e}",
                            }
                        )
                    print(f"  WARNING: no se pudo descargar: {ep.enclosure_url}")
                    print(f"  WARNING: {type(e).__name__}: {e}")

        if post_path.exists() and not args.overwrite_posts:
            print(f"- {ep.title} -> {post_path.relative_to(repo_root)} (ya existe, skip)")
            continue

        local_audio_url = None
        audio_length = None
        audio_type = ep.enclosure_type

        if args.download and ep.enclosure_url:
            base = _basename_from_url(ep.enclosure_url)
            # Evita colisiones: añade fecha delante
            mp3_name = f"{date_prefix}-{base}"
            mp3_path = mp3_dir / mp3_name
            if not args.dry_run:
                try:
                    size = _download(ep.enclosure_url, mp3_path, overwrite=args.overwrite)
                    audio_length = size
                    local_audio_url = f"/assets/mp3/{mp3_name}"
                except Exception as e:
                    key = (date_prefix, ep.title, ep.enclosure_url)
                    if key not in seen_failure_keys:
                        seen_failure_keys.add(key)
                        failures.append(
                            {
                                "date": date_prefix,
                                "title": ep.title,
                                "url": ep.enclosure_url,
                                "error": f"{type(e).__name__}: {e}",
                            }
                        )
                    print(f"  WARNING: no se pudo descargar: {ep.enclosure_url}")
                    print(f"  WARNING: {type(e).__name__}: {e}")
                    # Fallback: usar URL remota en el post
                    local_audio_url = None
                    audio_length = ep.enclosure_length
            else:
                audio_length = ep.enclosure_length
                local_audio_url = f"/assets/mp3/{mp3_name}"

        post_content = _format_post(
            ep,
            local_audio_url=local_audio_url,
            audio_length=audio_length,
            audio_type=audio_type,
        )

        print(f"- {ep.title} -> {post_path.relative_to(repo_root)}")
        if ep.enclosure_url:
            print(f"  audio: {local_audio_url or ep.enclosure_url}")

        if not args.dry_run:
            posts_dir.mkdir(parents=True, exist_ok=True)
            post_path.write_text(post_content, encoding="utf-8")

    # Reporte final de fallos (siempre que no sea dry-run)
    if not args.dry_run and args.failures_file:
        report_path = (repo_root / args.failures_file).resolve() if not os.path.isabs(args.failures_file) else Path(args.failures_file)
        _write_failures(report_path, failures)
        print(f"\nReporte de fallos escrito en: {report_path.relative_to(repo_root) if report_path.is_relative_to(repo_root) else report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
