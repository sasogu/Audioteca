#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
IMAGES = ROOT / "assets" / "images"

IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
SRC_ATTR_RE = re.compile(r"src=(['\"])(?P<src>.*?)(\1)", re.IGNORECASE)
REMOTE_RE = re.compile(r"https?://(www\.)?daizansoriano\.com/", re.IGNORECASE)

EXTS = (".jpg", ".jpeg", ".png", ".webp")

def find_local_candidate(year: str, slug: str) -> Path | None:
    year_dir = IMAGES / year
    if not year_dir.exists():
        return None
    # Look for files like slug-img1.*, slug-img2.*; pick img1 first
    candidates = []
    for p in sorted(year_dir.glob(f"{slug}-img*")):
        if p.suffix.lower() in EXTS:
            candidates.append(p)
    return candidates[0] if candidates else None


def replace_in_post(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    # Count img tags
    imgs = list(IMG_TAG_RE.finditer(text))
    if not imgs:
        return False

    # Determine year and slug from filename path
    try:
        year = path.parts[-2]
        fname = path.stem  # e.g., 2022-05-10-slug
        slug = fname.split('-', 3)[-1]
    except Exception:
        return False

    changed = False

    # If exactly one <img> tag and its src is remote, try to map to local
    if len(imgs) == 1:
        m = imgs[0]
        tag = m.group(0)
        sm = SRC_ATTR_RE.search(tag)
        if sm:
            src_val = sm.group('src')
            if REMOTE_RE.search(src_val):
                local = find_local_candidate(year, slug)
                if local and local.exists():
                    local_url = f"/assets/images/{year}/{local.name}"
                    new_tag = SRC_ATTR_RE.sub(lambda mm: f"src=\"{local_url}\"", tag, count=1)
                    text = text[:m.start()] + new_tag + text[m.end():]
                    changed = True
    
    if changed:
        path.write_text(text, encoding='utf-8')
    return changed


def main():
    changed_files = 0
    for post in sorted(POSTS.rglob('*.md')):
        if replace_in_post(post):
            changed_files += 1
            print(f"Updated: {post.relative_to(ROOT)}")
    print(f"Done. Files updated: {changed_files}")

if __name__ == '__main__':
    main()
