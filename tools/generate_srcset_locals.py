#!/usr/bin/env python3
import re
import sys
from pathlib import Path

try:
    from PIL import Image
except Exception as e:
    print("ERROR: Pillow no está instalado (pip install Pillow)")
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
IMAGES = ROOT / "assets" / "images"

IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(r"(\w+)=([\"\'])(.*?)\2", re.IGNORECASE)

TARGET_WIDTHS = [300, 768, 1024, 1536, 2048]


def parse_attrs(tag: str) -> dict:
    attrs = {}
    for m in ATTR_RE.finditer(tag):
        attrs[m.group(1).lower()] = (m.group(2), m.group(3))  # quote, value
    return attrs


def build_tag(attrs: dict) -> str:
    parts = ["<img"]
    for k, (q, v) in attrs.items():
        parts.append(f" {k}={q}{v}{q}")
    parts.append(">")
    return "".join(parts)


def ensure_variants(image_path: Path) -> tuple[list[tuple[str,int]], int]:
    """Return (entries, orig_width) where entries are list of (url, width)."""
    if not image_path.exists():
        return ([], 0)
    with Image.open(image_path) as im:
        orig_w, orig_h = im.size
        ext = image_path.suffix.lower()
        year = image_path.parent.name
        base = image_path.stem
        entries = []
        # original included at the end
        for w in TARGET_WIDTHS:
            if w >= orig_w:
                continue
            variant = image_path.with_name(f"{base}-{w}w{ext}")
            if not variant.exists():
                ratio = w / float(orig_w)
                h = max(1, int(round(orig_h * ratio)))
                im_resized = im.resize((w, h), Image.LANCZOS)
                save_kwargs = {}
                if ext in ('.jpg', '.jpeg'):
                    save_kwargs = {"quality": 85, "optimize": True}
                im_resized.save(variant, **save_kwargs)
            entries.append((f"/assets/images/{year}/{variant.name}", w))
        # add original
        entries.append((f"/assets/images/{year}/{image_path.name}", orig_w))
        return (entries, orig_w)


def process_post(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    changed = False

    def repl_img(m: re.Match) -> str:
        nonlocal changed
        tag = m.group(0)
        attrs = parse_attrs(tag)
        src = attrs.get('src')
        if not src:
            return tag
        q, val = src
        if not val.startswith('/assets/images/'):
            return tag
        # resolve image file
        try:
            # expected /assets/images/YYYY/filename.ext
            parts = Path(val).parts
            year = parts[-2]
            filename = parts[-1]
            image_path = IMAGES / year / filename
        except Exception:
            return tag
        entries, orig_w = ensure_variants(image_path)
        if not entries:
            return tag
        # build srcset "url widthw" entries
        srcset_val = ", ".join([f"{u} {w}w" for (u, w) in entries])
        attrs['srcset'] = ( '"', srcset_val )
        # choose src as best <= 1024 if available
        best = None
        for u,w in entries:
            if w <= 1024:
                best = (u,w)
        if best is None:
            best = entries[-1]
        attrs['src'] = ( '"', best[0] )
        # sizes: default responsive rule
        attrs['sizes'] = ( '"', f"(max-width: {min(1024, orig_w)}px) 100vw, {min(1024, orig_w)}px" )
        changed = True
        return build_tag(attrs)

    new_text = IMG_TAG_RE.sub(repl_img, text)
    if changed:
        path.write_text(new_text, encoding='utf-8')
    return changed


def main():
    updated = 0
    for post in sorted(POSTS.rglob('*.md')):
        if process_post(post):
            updated += 1
            print(f"Updated: {post.relative_to(ROOT)}")
    print(f"Done. Files updated: {updated}")

if __name__ == '__main__':
    main()
