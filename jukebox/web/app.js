"use strict";
const labels = {text: "Lyrics & DJ text", art: "Cover artwork", music: "Music", speech: "DJ speech"};
const button = document.querySelector("#refresh");
async function refresh() {
  button.disabled = true;
  try {
    const [statusResponse, sessionResponse] = await Promise.all([fetch("/api/status"), fetch("/api/session")]);
    if (!statusResponse.ok || !sessionResponse.ok) throw new Error("Local app unavailable");
    const status = await statusResponse.json();
    const session = await sessionResponse.json();
    const list = document.querySelector("#services");
    list.replaceChildren();
    for (const [role, label] of Object.entries(labels)) {
      const item = document.createElement("li");
      const title = document.createElement("span");
      title.textContent = label;
      const badge = document.createElement("strong");
      const ready = status.services[role] === "configured";
      badge.className = ready ? "ready" : "missing";
      badge.textContent = ready ? "Configured" : "Missing settings";
      item.append(title, badge);
      list.append(item);
    }
    document.querySelector("#summary").textContent = status.configured ? "All four services are configured." : "The app is running. Some service settings are missing.";
    document.querySelector("#track-count").textContent = `${session.tracks.length} tracks`;
    document.querySelector("#app-status").textContent = "App connected";
  } catch {
    document.querySelector("#summary").textContent = "Could not read local app status. Check the terminal and try again.";
    document.querySelector("#app-status").textContent = "App unavailable";
  } finally {
    button.disabled = false;
  }
}
button.addEventListener("click", refresh);
refresh();
