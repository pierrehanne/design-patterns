/* Progressive enhancement: every chapter and source is readable without JS. */
(() => {
  document.documentElement.classList.add("js");
  const readPreference = (key) => {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  };
  const savePreference = (key, value) => {
    try {
      localStorage.setItem(key, value);
    } catch {
      /* Reading still works. */
    }
  };
  const theme = document.querySelector(".theme-toggle");
  const setTheme = (value) => {
    document.documentElement.dataset.theme = value;
    document.querySelector('meta[name="theme-color"]').content =
      value === "dark" ? "#0e1422" : "#f6f8fc";
    theme.setAttribute(
      "aria-label",
      `Switch to ${value === "dark" ? "light" : "dark"} theme`,
    );
  };
  setTheme(
    readPreference("dp-theme") ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"),
  );
  theme.addEventListener("click", () => {
    const next =
      document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    setTheme(next);
    savePreference("dp-theme", next);
  });

  const menu = document.querySelector(".menu-toggle");
  menu.addEventListener("click", () => {
    const open = menu.getAttribute("aria-expanded") !== "true";
    menu.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("nav-open", open);
  });
  document.addEventListener("keydown", (event) => {
    const searchDialog = document.querySelector("#search-dialog");
    if (event.key === "Escape" && searchDialog.open) {
      event.preventDefault();
      searchDialog.close();
      return;
    }
    if (
      event.key === "Escape" &&
      menu.getAttribute("aria-expanded") === "true"
    ) {
      menu.click();
      menu.focus();
    }
  });

  const languageButtons = [...document.querySelectorAll("[data-language]")];
  const selectLanguage = (language) => {
    languageButtons.forEach((button) =>
      button.setAttribute(
        "aria-pressed",
        String(button.dataset.language === language),
      ),
    );
    document.querySelectorAll("[data-panel]").forEach((panel) => {
      panel.hidden = panel.dataset.panel !== language;
    });
  };
  if (languageButtons.length) {
    const preferred = readPreference("dp-language");
    selectLanguage(
      languageButtons.some((button) => button.dataset.language === preferred)
        ? preferred
        : "py",
    );
    languageButtons.forEach((button) =>
      button.addEventListener("click", () => {
        selectLanguage(button.dataset.language);
        savePreference("dp-language", button.dataset.language);
      }),
    );
  }
  document.querySelectorAll("[data-copy]").forEach((button) =>
    button.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(
          document.getElementById(button.dataset.copy).textContent,
        );
        button.textContent = "Copied";
      } catch {
        button.textContent = "Select code to copy";
      }
      setTimeout(() => {
        button.textContent = "Copy";
      }, 2500);
    }),
  );

  const catalogInput = document.querySelector("#catalog-search");
  if (catalogInput) {
    let category = "All";
    const cards = [...document.querySelectorAll(".pattern-card")];
    const filter = () => {
      const terms = catalogInput.value
        .toLowerCase()
        .trim()
        .split(/\s+/)
        .filter(Boolean);
      let count = 0;
      cards.forEach((card) => {
        const visible =
          (category === "All" || card.dataset.family === category) &&
          terms.every((term) =>
            card.dataset.search.toLowerCase().includes(term),
          );
        card.hidden = !visible;
        if (visible) count++;
      });
      document.querySelector("#catalog-status").textContent =
        `${count} ${count === 1 ? "pattern" : "patterns"}`;
      document.querySelector("#catalog-empty").hidden = count > 0;
    };
    catalogInput.addEventListener("input", filter);
    document.querySelectorAll("[data-filter]").forEach((button) =>
      button.addEventListener("click", () => {
        category = button.dataset.filter;
        document
          .querySelectorAll("[data-filter]")
          .forEach((item) =>
            item.setAttribute("aria-pressed", String(item === button)),
          );
        filter();
      }),
    );
  }

  const dialog = document.querySelector("#search-dialog");
  const input = document.querySelector("#search-input");
  const results = document.querySelector("#search-results");
  const status = document.querySelector("#search-status");
  let searchIndex;
  let loading;
  const renderSearch = () => {
    if (!searchIndex) return;
    const terms = input.value.toLowerCase().trim().split(/\s+/).filter(Boolean);
    const matches = searchIndex.filter((item) =>
      terms.every((term) =>
        `${item.title} ${item.summary} ${item.text}`
          .toLowerCase()
          .includes(term),
      ),
    );
    matches.sort(
      (a, b) =>
        Number(terms.every((term) => b.title.toLowerCase().includes(term))) -
        Number(terms.every((term) => a.title.toLowerCase().includes(term))),
    );
    results.replaceChildren();
    status.textContent = terms.length
      ? `${matches.length} results`
      : "Browse all chapters and guides";
    matches.forEach((item) => {
      const link = document.createElement("a");
      link.href = item.url;
      const label = document.createElement("strong");
      label.textContent = item.title;
      const summary = document.createElement("span");
      summary.textContent = `${item.category} · ${item.summary}`;
      link.append(label, summary);
      results.append(link);
    });
    if (!matches.length)
      status.textContent =
        "No results. Try another word, such as “state” or “undo”.";
  };
  const openSearch = async () => {
    if (!dialog.open) dialog.showModal();
    input.focus();
    if (!searchIndex) {
      status.textContent = "Loading the book index…";
      try {
        loading ||= fetch("search-index.json").then((response) => {
          if (!response.ok) throw new Error("Search unavailable");
          return response.json();
        });
        searchIndex = await loading;
      } catch {
        loading = null;
        status.textContent =
          "Search could not load. Close this window and use the book contents, or try again.";
        return;
      }
    }
    renderSearch();
  };
  document.querySelector(".search-open").addEventListener("click", openSearch);
  document
    .querySelector(".search-close")
    .addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  input.addEventListener("input", renderSearch);
  document.addEventListener("keydown", (event) => {
    const editing = event.target.closest(
      'input, textarea, select, [contenteditable="true"]',
    );
    if (
      event.key === "/" &&
      !editing &&
      !event.ctrlKey &&
      !event.metaKey &&
      !event.altKey
    ) {
      event.preventDefault();
      openSearch();
    }
  });
})();
