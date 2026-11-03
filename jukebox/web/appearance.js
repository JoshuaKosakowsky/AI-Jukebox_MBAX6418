"use strict";

// Apply before paint. Only these two visual preferences enter local storage.
(() => {
  const choices = {design: ["sleeve", "gallery", "console", "room", "shop", "workbench"], theme: ["dark", "light"]};
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
    const studio = document.querySelector(".create-panel");
    let studioBeforeWorkbench;
    function arrangeStudio() {
      if (root.dataset.design === "workbench" && studioBeforeWorkbench === undefined) {
        studioBeforeWorkbench = studio.open;
        studio.open = true;
      } else if (root.dataset.design !== "workbench" && studioBeforeWorkbench !== undefined) {
        studio.open = studioBeforeWorkbench;
        studioBeforeWorkbench = undefined;
      }
    }
    arrangeStudio();
    // Keep focused controls fully visible in the sideways record rack.
    document.querySelector("#tracks").addEventListener("focusin", (event) => {
      if (root.dataset.design !== "shop") return;
      const card = event.target.closest(".track");
      if (card) card.scrollIntoView({block: "nearest", inline: "nearest", behavior: "instant"});
    });
    for (const key of Object.keys(choices)) {
      const select = document.querySelector(`#${key}-choice`);
      select.value = root.dataset[key];
      select.addEventListener("change", () => {
        if (!choices[key].includes(select.value)) return;
        root.dataset[key] = select.value;
        if (key === "design") arrangeStudio();
        try { localStorage.setItem(`jukebox.${key}`, select.value); } catch { /* Keep the current page usable. */ }
        // Shareable links retain the current section. No navigation or media rebuild.
        const url = new URL(window.location.href);
        for (const preference of Object.keys(choices)) url.searchParams.set(preference, root.dataset[preference]);
        try { window.history.replaceState(null, "", url); } catch { /* Preferences still work without history access. */ }
      });
    }
  }, {once: true});
})();
