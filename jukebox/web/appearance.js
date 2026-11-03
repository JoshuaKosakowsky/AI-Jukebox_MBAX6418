"use strict";

// Apply before paint. Only these two visual preferences enter local storage.
(() => {
  const choices = {design: ["sleeve", "gallery", "console"], theme: ["dark", "light"]};
  const defaults = {design: "sleeve", theme: "dark"};
  const root = document.documentElement;
  const params = new URLSearchParams(window.location.search);
  for (const key of Object.keys(choices)) {
    let saved;
    try { saved = localStorage.getItem(`jukebox.${key}`); } catch { /* Private browser storage may be unavailable. */ }
    const supplied = params.get(key);
    root.dataset[key] = choices[key].includes(supplied) ? supplied
      : choices[key].includes(saved) ? saved : defaults[key];
  }

  document.addEventListener("DOMContentLoaded", () => {
    for (const key of Object.keys(choices)) {
      const select = document.querySelector(`#${key}-choice`);
      select.value = root.dataset[key];
      select.addEventListener("change", () => {
        if (!choices[key].includes(select.value)) return;
        root.dataset[key] = select.value;
        try { localStorage.setItem(`jukebox.${key}`, select.value); } catch { /* Keep the current page usable. */ }
        // Shareable links retain the current section. No navigation or media rebuild.
        const url = new URL(window.location.href);
        for (const preference of Object.keys(choices)) url.searchParams.set(preference, root.dataset[preference]);
        try { window.history.replaceState(null, "", url); } catch { /* Preferences still work without history access. */ }
      });
    }
  }, {once: true});
})();
