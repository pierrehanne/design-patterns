# Maintaining the field guide

The book is a static GitHub Pages site generated with the Python standard library. Every pattern chapter is authored in `book.json`, the five longer guides are HTML fragments in `guides/`, and shared presentation lives in `assets/`.

## Build and preview

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Open http://127.0.0.1:8000. Rebuild after changing prose, assets, or examples; this is a static server without live rebuilding.

The build generates 23 chapters, five guides, a home page, a 404 page, a search index, and 92 source downloads. Each chapter embeds all four source files directly from the repository. Do not edit `_site/`; it is regenerated and ignored by Git.

## Edit a chapter

Each entry in `book.json` has a stable slug, display title, category, and source path without an extension. The prose fields describe the problem, design, actual demo, decision criteria, costs, language differences, useful tests, and an exercise. `flow` gives the three participants shown in the collaboration diagram; `related` links to other chapter slugs.

Text in JSON is escaped during rendering. Write plain text there, not HTML. Guide fragments are trusted author-maintained HTML and can include headings, lists, tables, and code blocks. Give each guide heading a unique ID so the build can generate its table of contents.

The builder fails if chapter coverage and source coverage disagree. The validator checks every internal link and fragment, duplicate IDs, search coverage, all embedded source text, and byte-for-byte download fidelity. External URLs are not fetched by that validator.

## Publish on GitHub Pages

1. Push the changes to the repository's `main` branch.
2. In **Settings → Pages → Build and deployment**, set **Source** to **GitHub Actions**.
3. Run **Verify examples and publish the book** from the Actions tab if the initial push occurred before Pages was enabled.
4. Wait for the four example jobs, book validation, and deployment to pass. The deployment environment reports the published URL.

For this repository, the expected URL is https://pierrehanne.github.io/design-patterns/. The workflow builds and checks pull requests without publishing them; pushes to `main` and manual runs on `main` deploy after every required check succeeds.

The implementation follows [GitHub's custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). Deployment grants `pages: write` and `id-token: write` only to the deployment job. Actions are pinned to commits and Dependabot proposes updates.

On a fork, `GITHUB_REPOSITORY` automatically sets source links during Actions builds. For a local fork preview, set that environment variable to `owner/repository`. Update the public book link in the root README if the repository is renamed.

## Reader experience

All chapters and all four implementations are readable without JavaScript. JavaScript adds search, filtering, source-language selection, copying, mobile navigation, and saved theme/language preferences. Search matches all chapter prose and guides, but does not index the full source listings. Preferences remain in the reader's browser. No analytics, cookies, or backend is required.

Typography uses Google Fonts with system fallbacks; text and navigation remain usable if fonts cannot load. Links and assets are relative so normal pages work under a GitHub project subpath. The 404 page sets an absolute base to the repository’s Pages URL so navigation works even for an unknown nested path. Print styles expose every language and remove navigation.

Before publishing a presentation change, check desktop and narrow mobile widths, keyboard navigation, dark mode, search and empty results, source selection, download/copy behavior, and a page with JavaScript disabled. The Python link validator complements those checks; it does not replace browser verification.
