#!/usr/bin/env python3
"""Validate every local page, anchor, asset, source download, and search entry."""
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.links, self.sources = path, set(), [], {}
        self.errors = []
        self.h1_count = 0
        self.current_code = None
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.errors.append(f'duplicate id: {attrs["id"]}')
            self.ids.add(attrs['id'])
        if tag == 'h1':
            self.h1_count += 1
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if tag == 'code' and attrs.get('id', '').startswith('source-'):
            self.current_code = attrs['id'].removeprefix('source-')
            self.sources[self.current_code] = ''

    def handle_endtag(self, tag):
        if tag == 'code':
            self.current_code = None

    def handle_data(self, data):
        if self.current_code:
            self.sources[self.current_code] += data


def main():
    if not (SITE / 'index.html').exists():
        raise SystemExit('Build the site first: python3 scripts/build_site.py')
    pages = {path.resolve(): Page(path) for path in SITE.glob('*.html')}
    errors = []
    for path, page in pages.items():
        errors.extend(f'{path.name}: {error}' for error in page.errors)
        if page.h1_count != 1:
            errors.append(f'{path.name}: expected one h1')
        for link in page.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc:
                continue
            if parsed.path.startswith('/'):
                errors.append(f'{path.name}: root-relative link breaks project Pages: {link}')
            target = (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            if not target.is_relative_to(SITE.resolve()) or not target.exists():
                errors.append(f'{path.name}: missing local target {link}')
            elif parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                errors.append(f'{path.name}: missing anchor {link}')
    book = json.loads((ROOT / 'docs/book.json').read_text())
    for chapter in book:
        page = pages[(SITE / f"{chapter['slug']}.html").resolve()]
        for ext in ('py', 'ts', 'rs', 'go'):
            path = f"{chapter['path']}.{ext}"
            original = (ROOT / path).read_text()
            if page.sources.get(ext) != original:
                errors.append(f'{chapter["slug"]}: embedded {ext} source differs from repository')
            if (SITE / 'examples' / path).read_bytes() != (ROOT / path).read_bytes():
                errors.append(f'{path}: download differs from repository')
    index = json.loads((SITE / 'search-index.json').read_text())
    urls = {entry['url'] for entry in index}
    expected = {f"{c['slug']}.html" for c in book} | {f'{p.stem}.html' for p in (ROOT / 'docs/guides').glob('*.html')}
    if urls != expected or len(index) != len(expected):
        errors.append('Search index must include each chapter and guide exactly once')
    for entry in index:
        if not (SITE / entry['url']).is_file():
            errors.append(f'Missing search destination: {entry["url"]}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(pages)} pages; all local links and anchors; 92 embedded sources and downloads; {len(index)} search entries')


if __name__ == '__main__':
    main()
