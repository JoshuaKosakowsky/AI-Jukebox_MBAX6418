"use strict";

// Submission uses Cover Gallery. Only the theme is a stored preference.
(() => {
  const themes = ["dark", "light"];
  const root = document.documentElement;
  const params = new URLSearchParams(window.location.search);
  root.dataset.design = "gallery";
  let saved;
  try { saved = localStorage.getItem("jukebox.theme"); } catch { /* Storage may be unavailable. */ }
  const supplied = params.get("theme");
  root.dataset.theme = themes.includes(supplied) ? supplied
    : themes.includes(saved) ? saved : "dark";

  document.addEventListener("DOMContentLoaded", () => {
    const select = document.querySelector("#theme-choice");
    select.value = root.dataset.theme;
    function updateUrl() {
      const url = new URL(window.location.href);
      url.searchParams.delete("design");
      url.searchParams.set("theme", root.dataset.theme);
      try { window.history.replaceState(null, "", url); } catch { /* Theme still works. */ }
    }
    if (params.has("design")) updateUrl();
    select.addEventListener("change", () => {
      if (!themes.includes(select.value)) return;
      root.dataset.theme = select.value;
      try { localStorage.setItem("jukebox.theme", select.value); } catch { /* Keep the current page usable. */ }
      updateUrl();
    });
  }, {once: true});
})();
