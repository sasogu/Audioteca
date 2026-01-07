#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"

IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
FIGURE_TAG_OPEN_RE = re.compile(r"<figure\b[^>]*>", re.IGNORECASE)
FIGURE_TAG_CLOSE_RE = re.compile(r"</figure>", re.IGNORECASE)
ATTR_RE = re.compile(r"(\w+)=([\"\'])(.*?)\2", re.IGNORECASE)

# Atributos permitidos en <img> (sin width/height para evitar forzar tamaño)
ALLOWED_IMG_ATTRS = {"src", "srcset", "sizes", "alt", "loading"}


def parse_attrs(tag: str) -> dict:
    attrs = {}
    for m in ATTR_RE.finditer(tag):
        key = m.group(1).lower()
        quote = m.group(2)
        val = m.group(3)
        attrs[key] = (quote, val)
    return attrs


def build_img(attrs: dict) -> str:
    parts = ["<img"]
    for k in ["src","srcset","sizes","alt","loading"]:
        if k in attrs:
            q, v = attrs[k]
            parts.append(f" {k}={q}{v}{q}")
    parts.append(">")
    return "".join(parts)


def simplify_img_tags(text: str) -> str:
    def repl_img(m: re.Match) -> str:
        tag = m.group(0)
        attrs = parse_attrs(tag)
        # Mantener solo atributos permitidos
        kept = {k: v for k, v in attrs.items() if k in ALLOWED_IMG_ATTRS}
        # Asegurar loading="lazy"
        if "loading" not in kept:
            kept["loading"] = ('"', 'lazy')
        return build_img(kept)

    return IMG_TAG_RE.sub(repl_img, text)


def simplify_figure_tags(text: str) -> str:
    # Eliminar clases/estilos en <figure ...> dejando <figure>
    text = FIGURE_TAG_OPEN_RE.sub("<figure>", text)
    return text


def process_file(path: Path) -> bool:
    original = path.read_text(encoding='utf-8')
    updated = simplify_img_tags(original)
    updated = simplify_figure_tags(updated)
    if updated != original:
        path.write_text(updated, encoding='utf-8')
        return True
    return False


def main():
    changed = 0
    files = sorted(POSTS.rglob('*.md'))
    for f in files:
        if process_file(f):
            changed += 1
            print(f"Updated: {f.relative_to(ROOT)}")
    print(f"Done. Files updated: {changed}")

if __name__ == '__main__':
    main()
