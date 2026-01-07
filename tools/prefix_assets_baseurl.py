#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"

SRC_RE = re.compile(r"(\ssrc=)([\"'])(/assets/[^\"']+)([\"'])", re.IGNORECASE)
SRCSET_RE = re.compile(r"(\ssrcset=)([\"'])([^\"']+)([\"'])", re.IGNORECASE)


def fix_src(text: str) -> str:
    def repl(m: re.Match) -> str:
        prefix, quote1, path, quote2 = m.groups()
        if path.startswith('/assets/'):
            return f"{prefix}{quote1}{{{{ site.baseurl }}}}{path}{quote2}"
        return m.group(0)
    return SRC_RE.sub(repl, text)


def fix_srcset(text: str) -> str:
    def repl(m: re.Match) -> str:
        prefix, quote1, content, quote2 = m.groups()
        parts = [p.strip() for p in content.split(',') if p.strip()]
        new_parts = []
        for p in parts:
            tokens = p.split()
            if not tokens:
                continue
            url = tokens[0]
            rest = ' '.join(tokens[1:])
            if url.startswith('/assets/'):
                url = f"{{{{ site.baseurl }}}}{url}"
            new_parts.append(' '.join([url, rest]).strip())
        new_content = ', '.join(new_parts)
        return f"{prefix}{quote1}{new_content}{quote2}"
    return SRCSET_RE.sub(repl, text)


def process_file(path: Path) -> bool:
    original = path.read_text(encoding='utf-8')
    updated = fix_src(original)
    updated = fix_srcset(updated)
    if updated != original:
        path.write_text(updated, encoding='utf-8')
        print(f"Updated: {path.relative_to(ROOT)}")
        return True
    return False


def main():
    changed = 0
    for f in sorted(POSTS.rglob('*.md')):
        if process_file(f):
            changed += 1
    print(f"Done. Files updated: {changed}")

if __name__ == '__main__':
    main()
