#!/usr/bin/env python3
"""Build the book from curated prose and the actual examples. No dependencies."""
from __future__ import annotations

import html
import json
import os
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
REPOSITORY = os.environ.get('GITHUB_REPOSITORY', 'pierrehanne/design-patterns')
REPO = f'https://github.com/{REPOSITORY}'
OWNER, REPO_NAME = REPOSITORY.split('/', 1)
SITE_URL = f'https://{OWNER}.github.io/' + ('' if REPO_NAME.lower() == f'{OWNER}.github.io'.lower() else f'{REPO_NAME}/')
LANGUAGES = {'py': 'Python', 'ts': 'TypeScript', 'rs': 'Rust', 'go': 'Go'}
GUIDES = [
    ('foundations', 'Think in boundaries', 'Principles before patterns'),
    ('choosing', 'Choose a pattern', 'Decisions and comparisons'),
    ('production', 'Beyond the example', 'Failure, ownership, and testing'),
    ('languages', 'Across four languages', 'Same intent, different idioms'),
    ('learning-path', 'Your learning path', 'Practice with a purpose'),
]
SECTIONS = [
    ('problem', 'The design pressure'), ('design', 'How the pattern works'),
    ('trace', 'Walk through the implementation'), ('decision', 'When it earns its place'),
    ('cost', 'Tradeoffs and production limits'), ('language', 'Across the languages'),
    ('tests', 'What to test'), ('exercise', 'Try it yourself'),
]
e = html.escape


def load_book():
    book = json.loads((ROOT / 'docs/book.json').read_text())
    slugs = {c['slug'] for c in book}
    if len(book) != 23 or len(slugs) != len(book):
        raise ValueError('Expected 23 distinct pattern chapters')
    declared = set()
    for c in book:
        for key in ['title', 'family', 'path', 'intent', 'flow', *[s[0] for s in SECTIONS]]:
            if not c.get(key):
                raise ValueError(f"Missing {key}: {c['slug']}")
        if not set(c['related']) <= slugs:
            raise ValueError(f"Unknown related chapter: {c['slug']}")
        for ext in LANGUAGES:
            source = ROOT / f"{c['path']}.{ext}"
            if not source.is_file():
                raise ValueError(f'Missing source: {source}')
            declared.add(source)
    actual = {p for ext in LANGUAGES for p in ROOT.glob(f'*-design-pattern/*/*.{ext}')}
    if actual != declared:
        raise ValueError(f'Book/source coverage mismatch: {actual ^ declared}')
    return book


def sidebar(book, active):
    def link(slug, label, number=''):
        current = ' aria-current="page"' if slug == active else ''
        return f'<a href="{slug}.html"{current}><span class="nav-number">{number}</span>{e(label)}</a>'
    result = '<nav class="sidebar" id="book-nav" aria-label="Book contents"><div class="sidebar-inner"><p class="nav-label">THE FIELD GUIDE</p>'
    result += link('index', 'Introduction', '↗')
    result += ''.join(link(slug, title) for slug, title, _ in GUIDES)
    for family in ('Creational', 'Structural', 'Behavioral'):
        result += f'<p class="nav-label">{family}</p>'
        for i, c in enumerate(book, 1):
            if c['family'] == family:
                result += link(c['slug'], c['title'], f'{i:02}')
    return result + f'<a class="repo-link" href="{REPO}">View repository ↗</a></div></nav>'


def layout(book, slug, title, description, content, toc=()):
    base = f'<base href="{e(SITE_URL, quote=True)}">' if slug == '404' else ''
    toc_html = ''.join(f'<a href="#{key}">{e(label)}</a>' for key, label in toc)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
{base}<title>{e(title)} · Design Patterns Field Guide</title><meta name="description" content="{e(description, quote=True)}">
<meta name="theme-color" content="#f6f8fc"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a>
<header class="topbar"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">dp.</span><span>DESIGN PATTERNS<small>A FIELD GUIDE FOR ENGINEERS</small></span></a>
<div class="header-actions"><button class="search-open js-only" type="button">Search the book <kbd>/</kbd></button><button class="theme-toggle js-only" type="button" aria-label="Switch color theme">◐</button><button class="menu-toggle js-only" type="button" aria-controls="book-nav" aria-expanded="false">Contents</button><a class="github-link" href="{REPO}">GitHub ↗</a></div></header>
<div class="layout">{sidebar(book, slug)}<main id="main" tabindex="-1">{content}<footer><span>Design Patterns Field Guide · MIT licensed</span><a href="{REPO}/blob/main/docs/README.md">About this book ↗</a></footer></main>
<aside class="on-this-page" aria-label="On this page"><p class="nav-label">ON THIS PAGE</p>{toc_html}<a class="back-top" href="#main">Back to top ↑</a></aside></div>
<dialog id="search-dialog" aria-labelledby="search-title"><div class="search-heading"><h2 id="search-title">Find a pattern or idea</h2><button type="button" class="search-close" aria-label="Close search">✕</button></div><label for="search-input">Search chapters, tradeoffs, and guidance</label><input id="search-input" type="search" placeholder="Try ‘undo’, ‘cache’, or ‘ownership’" autocomplete="off"><p id="search-status" role="status"></p><div id="search-results"></div></dialog>
</body></html>'''


def sources(c):
    controls = ''.join(f'<button type="button" data-language="{ext}" aria-pressed="{str(ext == "py").lower()}">{label}</button>' for ext, label in LANGUAGES.items())
    result = f'<section id="implementation"><h2>Read the implementation</h2><p>Complete source from the repository. Choose a language, trace the call path, then run it locally.</p><div class="language-controls js-only" role="group" aria-label="Source language">{controls}</div>'
    for ext, label in LANGUAGES.items():
        path = f"{c['path']}.{ext}"
        code = (ROOT / path).read_text()
        stem = Path(path).stem
        commands = {
            'py': f'python3 {path}',
            'ts': f'npm ci\nnpx tsc --strict --target ES2022 --module commonjs --outDir /tmp/pattern-demo {path}\nnode /tmp/pattern-demo/{stem}.js',
            'rs': f'rustc --edition=2021 {path} -o /tmp/pattern-demo\n/tmp/pattern-demo',
            'go': f'go run {path}',
        }
        # Each language gets a separate download copied directly from the source.
        download = OUT / 'examples' / path
        download.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, download)
        result += f'''<div class="source-panel" data-panel="{ext}"><div class="source-heading"><span>{label} <small>{e(Path(path).name)}</small></span><div><a href="{REPO}/blob/main/{path}">GitHub ↗</a><a href="examples/{path}" download>Download</a><button class="copy-button js-only" data-copy="source-{ext}" type="button">Copy</button></div></div>
<pre class="source-code" role="region" tabindex="0" aria-label="{label} source"><code id="source-{ext}">{e(code)}</code></pre><p class="run-label">Run from the repository root</p><pre class="run-command" role="region" tabindex="0" aria-label="Run {label} example"><code>{e(commands[ext])}</code></pre></div>'''
    return result + '</section>'


def chapter_page(book, c, index):
    title = c['title']
    body = f'<div class="chapter-header"><p class="eyebrow">{c["family"].upper()} / CHAPTER {index + 1:02}</p><h1>{e(title)}</h1><p class="lead">{e(c["intent"])}</p><div class="chapter-meta"><span>4 implementations</span><span>Design · tradeoffs · practice</span></div></div>'
    body += '<div class="flow" role="group" aria-label="Pattern collaboration">' + '<span class="flow-arrow" aria-hidden="true">→</span>'.join(f'<span class="flow-node">{e(node)}</span>' for node in c['flow']) + '</div>'
    for key, heading in SECTIONS:
        body += f'<section id="{key}" class="{"exercise" if key == "exercise" else "prose-section"}"><h2>{heading}</h2><p>{e(c[key])}</p></section>'
    body += sources(c)
    names = {item['slug']: item['title'] for item in book}
    body += '<section id="related"><h2>Connect the ideas</h2><div class="related">' + ''.join(f'<a href="{s}.html">{e(names[s])} <span>↗</span></a>' for s in c['related']) + '</div></section>'
    previous = book[index - 1] if index else None
    following = book[index + 1] if index + 1 < len(book) else None
    body += '<nav class="chapter-pagination" aria-label="Chapter navigation">'
    body += f'<a href="{previous["slug"] if previous else "foundations"}.html"><small>← PREVIOUS</small>{e(previous["title"] if previous else "Think in boundaries")}</a>'
    body += f'<a href="{following["slug"] if following else "learning-path"}.html"><small>NEXT →</small>{e(following["title"] if following else "Your learning path")}</a></nav>'
    return layout(book, c['slug'], title, c['intent'], body, [*SECTIONS, ('implementation', 'Source code'), ('related', 'Related patterns')])


def home(book):
    body = '''<section class="hero"><p class="eyebrow"><span class="status-dot"></span> AN OPEN-SOURCE ENGINEERING BOOK</p><h1>Good design starts<br>with <em>better decisions.</em></h1><p class="hero-description">Learn the patterns. Understand the tradeoffs. Know when to keep it simple.</p><p class="hero-detail">A practical guide to all 23 classic design patterns, grounded in runnable Python, TypeScript, Rust, and Go.</p><div class="hero-actions"><a class="primary-button" href="foundations.html">Start reading <span>→</span></a><a class="text-link" href="#patterns">Explore the patterns ↓</a></div>
<div class="book-stats"><div><strong>23</strong><span>DESIGN PATTERNS</span></div><div><strong>04</strong><span>LANGUAGES</span></div><div><strong>92</strong><span>RUNNABLE EXAMPLES</span></div></div></section>
<section class="editor-note" id="approach"><div><span class="eyebrow">THE APPROACH</span><h2>Beyond the class diagram.</h2></div><div><p>A pattern is a decision about where change belongs. This book follows that decision from the original problem to the code, then asks what happens under real constraints.</p><p>Every chapter includes a walkthrough, alternatives, production limits, tests worth writing, and an exercise to make the idea your own.</p></div></section>
<section id="reading"><div class="section-heading"><div><p class="eyebrow">BUILD YOUR JUDGMENT</p><h2>A guide, not just a catalog.</h2></div><span class="muted">Five essays to connect the ideas</span></div><div class="guide-grid">'''
    for i, (slug, title, subtitle) in enumerate(GUIDES, 1):
        body += f'<a class="guide-card" href="{slug}.html"><span class="guide-number">0{i} /</span><h3>{title}</h3><p>{subtitle}</p><span class="card-arrow" aria-hidden="true">↗</span></a>'
    body += '</div></section><section id="patterns"><div class="section-heading"><div><p class="eyebrow">THE PATTERN ATLAS</p><h2>One problem. A clearer design.</h2></div></div><div class="catalog-controls js-only"><label class="catalog-search">Find a pattern<input type="search" id="catalog-search" placeholder="Name, intent, or keyword…"></label><div class="filter-buttons" role="group" aria-label="Pattern category">'
    for family in ('All', 'Creational', 'Structural', 'Behavioral'):
        body += f'<button type="button" data-filter="{family}" aria-pressed="{str(family == "All").lower()}">{family}</button>'
    body += '</div></div><p id="catalog-status" class="js-only muted" role="status">23 patterns</p><div class="pattern-grid">'
    for i, c in enumerate(book, 1):
        keywords = e(' '.join(str(c[k]) for k in ('title', 'intent', 'problem', 'family')), quote=True)
        body += f'<a class="pattern-card" data-family="{c["family"]}" data-search="{keywords}" href="{c["slug"]}.html"><div class="card-meta"><span>{i:02}</span><span class="category {c["family"].lower()}">{c["family"]}</span></div><h3>{e(c["title"])}</h3><p>{e(c["intent"])}</p><span class="card-bottom">Read chapter <span aria-hidden="true">↗</span></span></a>'
    body += '</div><p id="catalog-empty" hidden>No patterns match. Try a broader term or another category.</p></section><section class="closing-note"><p class="eyebrow">A PRINCIPLE TO TAKE WITH YOU</p><h2>Use a pattern to explain a decision.<br>Never to justify complexity.</h2><a href="learning-path.html">Find your learning path →</a></section>'
    return layout(book, 'index', 'Good design starts with better decisions', 'A practical book on 23 design patterns with 92 examples in Python, TypeScript, Rust, and Go.', body, [('approach', 'Our approach'), ('reading', 'Engineering guides'), ('patterns', 'All 23 patterns')])


def main():
    book = load_book()
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / 'docs/assets', OUT / 'assets')
    (OUT / '.nojekyll').touch()
    (OUT / 'index.html').write_text(home(book))
    search = []
    for i, c in enumerate(book):
        (OUT / f"{c['slug']}.html").write_text(chapter_page(book, c, i))
        search.append(dict(title=c['title'], url=f"{c['slug']}.html", category=c['family'], summary=c['intent'], text=' '.join(c[key] for key, _ in SECTIONS)))
    for slug, title, subtitle in GUIDES:
        prose = (ROOT / f'docs/guides/{slug}.html').read_text().replace('<pre>', '<pre tabindex="0" role="region" aria-label="Example commands or decision record">')
        toc = re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', prose)
        content = f'<div class="chapter-header"><p class="eyebrow">ENGINEERING GUIDE</p><h1>{title}</h1></div><article class="guide-prose">{prose}</article>'
        (OUT / f'{slug}.html').write_text(layout(book, slug, title, subtitle, content, toc))
        search.append(dict(title=title, url=f'{slug}.html', category='Guide', summary=subtitle, text=html.unescape(re.sub('<[^>]+>', ' ', prose))))
    (OUT / 'search-index.json').write_text(json.dumps(search, ensure_ascii=False))
    (OUT / '404.html').write_text(layout(book, '404', 'Page not found', 'This chapter could not be found.', '<div class="chapter-header"><p class="eyebrow">404</p><h1>A page out of place.</h1><p class="lead">This chapter could not be found.</p><a href="index.html">Return to the field guide →</a></div>'))
    print(f'Built {len(book)} chapters, {len(GUIDES)} guides, and 92 source downloads in {OUT}')


if __name__ == '__main__':
    main()
