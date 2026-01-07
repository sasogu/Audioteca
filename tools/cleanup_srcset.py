#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSTS = ROOT / "_posts"

def clean_srcset_attrs(text: str) -> str:
    # Remove srcset entries that reference daizansoriano.com (http or https, with/without www)
    def repl(match: re.Match) -> str:
        quote = match.group(1)
        content = match.group(2)
        parts = [p.strip() for p in content.split(',') if p.strip()]
        kept = []
        for p in parts:
            url = p.split()[0]
            if re.search(r"https?://(www\.)?daizansoriano\.com/", url, re.IGNORECASE):
                continue
            kept.append(p)
        if not kept:
            return ''  # remove entire srcset attribute
        new_content = ', '.join(kept)
        return f" srcset={quote}{new_content}{quote}"

    # Pattern matches srcset="..." or srcset='...'
    pattern = re.compile(r"\s+srcset=(['\"])(.*?)(\1)", re.IGNORECASE | re.DOTALL)
    return pattern.sub(repl, text)


def process_file(path: Path) -> bool:
    original = path.read_text(encoding='utf-8')
    updated = clean_srcset_attrs(original)
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
