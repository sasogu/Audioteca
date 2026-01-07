#!/usr/bin/env python3
import re
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"
IMAGES = ROOT / "assets" / "images"

IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
SRC_ATTR_RE = re.compile(r"src=(['\"])(?P<src>.*?)(\1)", re.IGNORECASE)
SRCSET_ATTR_RE = re.compile(r"\s+srcset=(['\"]).*?(\1)", re.IGNORECASE | re.DOTALL)
REMOTE_RE = re.compile(r"https?://(www\.)?daizansoriano\.com/", re.IGNORECASE)

ALLOWED_EXTS = {'.jpg', '.jpeg', '.png', '.webp'}
SIZE_SUFFIX_RE = re.compile(r"-(\d+)x(\d+)(?=\.[A-Za-z0-9]+$)")


def download(url: str, dest: Path) -> bool:
    try:
        with urlopen(url) as resp:
            data = resp.read()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"WARN: failed to download {url}: {e}")
        return False

def candidate_urls(original: str) -> list[str]:
    urls = [original]
    # with www
    p = urlparse(original)
    if p.netloc == 'daizansoriano.com':
        urls.append(urlunparse(p._replace(netloc='www.daizansoriano.com')))
    # remove size suffix like -1024x768
    def unsize(u: str) -> str:
        pu = urlparse(u)
        new_path = SIZE_SUFFIX_RE.sub('', pu.path)
        return urlunparse(pu._replace(path=new_path))
    urls.append(unsize(original))
    if p.netloc == 'daizansoriano.com':
        urls.append(unsize(urlunparse(p._replace(netloc='www.daizansoriano.com'))))
    # de-duplicate while preserving order
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def process_post(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    year = path.parts[-2]
    fname = path.stem
    # slug is everything after YYYY-MM-DD-
    parts = fname.split('-', 3)
    slug = parts[-1] if len(parts) >= 4 else fname

    changed = False
    img_index = 1

    def repl_img(match: re.Match) -> str:
        nonlocal changed, img_index
        tag = match.group(0)
        sm = SRC_ATTR_RE.search(tag)
        if not sm:
            return tag
        src_val = sm.group('src')
        if not REMOTE_RE.search(src_val):
            return tag
        # determine extension
        path_url = urlparse(src_val).path
        ext = Path(path_url).suffix.lower()
        if ext not in ALLOWED_EXTS:
            # keep original if unsupported
            return tag
        # build local path
        while True:
            candidate = IMAGES / year / f"{slug}-img{img_index}{ext}"
            if not candidate.exists():
                break
            img_index += 1
        for cand_url in candidate_urls(src_val):
            if download(cand_url, candidate):
                src_val = cand_url
                break
        if candidate.exists():
            local_url = f"/assets/images/{year}/{candidate.name}"
            # replace src
            new_tag = SRC_ATTR_RE.sub(lambda mm: f"src=\"{local_url}\"", tag, count=1)
            # drop srcset entirely (remote sizes)
            new_tag = SRCSET_ATTR_RE.sub('', new_tag)
            changed = True
            return new_tag
        return tag

    new_text = IMG_TAG_RE.sub(repl_img, text)
    if changed:
        path.write_text(new_text, encoding='utf-8')
    return changed


def main():
    changed_files = 0
    for post in sorted(POSTS.rglob('*.md')):
        if process_post(post):
            changed_files += 1
            print(f"Updated: {post.relative_to(ROOT)}")
    print(f"Done. Files updated: {changed_files}")

if __name__ == '__main__':
    main()
