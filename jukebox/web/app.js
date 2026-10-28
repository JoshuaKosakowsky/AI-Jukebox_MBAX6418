"use strict";
const labels = {text: "Lyrics & DJ text", art: "Cover artwork", music: "Music", speech: "DJ speech"};
const button = document.querySelector("#refresh");
const form = document.querySelector("#cover-form");
const createButton = document.querySelector("#create-cover");
const notice = document.querySelector("#cover-notice");
let artConfigured = false;
let submitting = false;
let polling;
let previousLibrary;
let refreshInFlight;

async function request(path, data) {
  const response = await fetch(path, data === undefined ? {} : {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)
  });
  if (!response.ok) {
    // Only fixed server SafeError messages are displayed, never raw responses.
    const result = await response.json().catch(() => ({}));
    throw new Error(result.error?.message || "The request could not be confirmed. Refresh before trying again.");
  }
  return response.json();
}

function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
}

function renderLibrary(session) {
  document.querySelector("#track-count").textContent = `${session.tracks.length} tracks`;
  document.querySelector("#empty-library").hidden = session.tracks.length > 0;
  const serialized = JSON.stringify(session);
  if (previousLibrary === serialized) return;
  previousLibrary = serialized;
  const library = document.querySelector("#tracks");
  library.replaceChildren();
  for (const track of session.tracks) {
    const card = node("article", undefined, "track");
    card.dataset.trackId = track.id;
    const picture = node("div", undefined, "cover");
    if (track.cover) {
      const image = node("img");
      image.src = track.cover.url;
      image.alt = `Generated cover for ${track.title}`;
      image.width = image.height = 512;
      picture.append(image);
    } else {
      picture.append(node("p", "No cover yet"));
    }
    const detail = node("div", undefined, "track-detail");
    detail.append(node("h3", track.title), node("p", `${track.settings.style} · ${track.settings.mood}`, "track-settings"));
    const jobs = session.jobs.filter(job => job.track_id === track.id && job.kind === "art");
    const job = jobs.at(-1);
    const active = job && ["queued", "running"].includes(job.state);
    const message = node("p", active ? "Generating new cover…" : job?.state === "failed" ? job.error.message : track.cover ? "New matching cover ready" : "Ready to generate a cover", "cover-status");
    message.setAttribute("role", "status");
    detail.append(message);
    if (track.audio) {
      const audio = node("audio");
      audio.controls = true;
      audio.preload = "none";
      audio.src = track.audio.url;
      audio.setAttribute("aria-label", `Play ${track.title}`);
      detail.append(audio);
    } else {
      detail.append(node("p", "Song draft · audio generation is not available yet.", "note"));
    }
    const retry = node("button", active ? "Generating…" : job?.state === "failed" ? "Retry cover" : track.cover ? "Generate new cover" : "Generate cover");
    retry.type = "button";
    retry.disabled = active || !artConfigured;
    retry.addEventListener("click", async () => {
      retry.disabled = true;
      try {
        await request(`/api/tracks/${track.id}/cover`, {});
        notice.textContent = `Cover requested for ${track.title}.`;
      } catch (error) {
        notice.textContent = error.message;
      }
      await syncAfterMutation();
    });
    detail.append(retry);
    card.append(picture, detail);
    library.append(card);
  }
}

async function load() {
  clearTimeout(polling);
  button.disabled = true;
  try {
    const [status, session] = await Promise.all([request("/api/status"), request("/api/session")]);
    const changedConfig = artConfigured !== status.cover_generation_available;
    artConfigured = status.cover_generation_available;
    if (changedConfig) previousLibrary = undefined;
    const list = document.querySelector("#services");
    list.replaceChildren();
    for (const [role, label] of Object.entries(labels)) {
      const ready = status.services[role] === "configured";
      const item = node("li");
      item.append(node("span", label), node("strong", ready ? "Configured" : "Missing settings", ready ? "ready" : "missing"));
      list.append(item);
    }
    document.querySelector("#summary").textContent = status.configured ? "All four services are configured." : "The app is running. Some service settings are missing.";
    document.querySelector("#cover-help").textContent = artConfigured ? "Each request generates original art from the song title, style and mood. Covers stay with their track in this browser session." : "Configure the server’s art service and restart the app to generate covers.";
    createButton.disabled = submitting || !artConfigured;
    renderLibrary(session);
    document.querySelector("#app-status").textContent = "App connected";
    if (session.jobs.some(job => ["queued", "running"].includes(job.state))) {
      polling = setTimeout(refresh, 1000);
    }
  } catch {
    createButton.disabled = true;
    document.querySelector("#summary").textContent = "Could not read local app status. Check the terminal and refresh. Accepted jobs are not resubmitted.";
    document.querySelector("#app-status").textContent = "App unavailable";
  } finally {
    button.disabled = false;
  }
}

function refresh() {
  if (!refreshInFlight) refreshInFlight = load().finally(() => { refreshInFlight = undefined; });
  return refreshInFlight;
}

async function syncAfterMutation() {
  // A poll started before this POST must not hide the newly accepted job.
  if (refreshInFlight) await refreshInFlight;
  previousLibrary = undefined;
  return refresh();
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (submitting || !artConfigured) return;
  submitting = true;
  createButton.disabled = true;
  try {
    const values = new FormData(form);
    await request("/api/tracks", {title: values.get("title"), settings: {
      style: values.get("style"), mood: values.get("mood"),
      duration_seconds: Number(values.get("duration")), mode: "instrumental"
    }});
    notice.textContent = "Song draft created. Generating its new cover…";
    form.reset();
  } catch (error) {
    notice.textContent = error.message;
  } finally {
    submitting = false;
    await syncAfterMutation();
  }
});
button.addEventListener("click", refresh);
refresh();
