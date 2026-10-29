"use strict";
const labels = {text: "Lyrics & DJ text", art: "Cover artwork", music: "Music", speech: "DJ speech"};
const button = document.querySelector("#refresh");
const form = document.querySelector("#cover-form");
const createButton = document.querySelector("#create-cover");
const notice = document.querySelector("#cover-notice");
let artConfigured = false;
let musicConfigured = false;
let submitting = false;
let polling;
// Serialized card inputs per track id; a card is rebuilt only when its own data
// changes, so playing audio on other tracks is never destroyed by a poll update.
const previousTracks = new Map();
let refreshInFlight;

async function request(path, data) {
  const response = await fetch(path, data === undefined ? {} : {
    method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)
  });
  if (!response.ok) {
    // Only fixed server SafeError messages are displayed, never raw responses.
    const result = await response.json().catch(() => ({}));
    const error = new Error(result.error?.message || "The request could not be confirmed. Refresh before trying again.");
    error.code = result.error?.code;
    throw error;
  }
  return response.json();
}

function node(tag, text, className) {
  const element = document.createElement(tag);
  if (text !== undefined) element.textContent = text;
  if (className) element.className = className;
  return element;
}

function musicStatusText(job, hasAudio) {
  if (!job) return hasAudio ? "Instrumental ready" : "No instrumental yet";
  if (job.state === "failed") return job.error?.message || "Instrumental generation failed.";
  if (job.state === "succeeded") return "Instrumental ready";
  if (job.progress >= 0.8) return "Downloading and validating audio…";
  if (job.progress >= 0.35) return "Generating instrumental music…";
  if (job.progress > 0) return "Submitting music request…";
  return "Waiting to start…";
}

function trackCardInput(track, jobs) {
  return JSON.stringify({track, jobs: jobs.filter(job => job.track_id === track.id)});
}

function restoreAudio(card, saved) {
  // Carry an in-progress playback position across a rebuild of THIS card only.
  if (!saved) return;
  const audio = card.querySelector("audio");
  if (!audio) return;
  audio.currentTime = saved.time;
  const play = () => { audio.play().catch(() => {}); };
  if (audio.readyState >= 2) play();
  else audio.addEventListener("canplay", play, {once: true});
}

function buildTrackCard(track, jobs) {
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
  const artJobs = jobs.filter(job => job.track_id === track.id && job.kind === "art");
  const artJob = artJobs.at(-1);
  const artActive = artJob && ["queued", "running"].includes(artJob.state);
  const coverStatus = node("p", artActive ? "Generating new cover…" : artJob?.state === "failed" ? artJob.error.message : track.cover ? "New matching cover ready" : "Ready to generate a cover", "cover-status");
  coverStatus.setAttribute("role", "status");
  detail.append(coverStatus);
  const musicJobs = jobs.filter(job => job.track_id === track.id && job.kind === "music");
  const musicJob = musicJobs.at(-1);
  const musicActive = musicJob && ["queued", "running"].includes(musicJob.state);
  const musicStatus = node("p", musicStatusText(musicJob, Boolean(track.audio)), "cover-status");
  musicStatus.setAttribute("role", "status");
  detail.append(musicStatus);
  if (track.audio) {
    const audio = node("audio");
    audio.controls = true;
    audio.preload = "none";
    audio.src = track.audio.url;
    audio.setAttribute("aria-label", `Play ${track.title}`);
    detail.append(audio);
  } else {
    detail.append(node("p", "Song draft · instrumental generation pending.", "note"));
  }
  const retryCover = node("button", artActive ? "Generating…" : artJob?.state === "failed" ? "Retry cover" : track.cover ? "Generate new cover" : "Generate cover");
  retryCover.type = "button";
  retryCover.disabled = artActive || !artConfigured;
  retryCover.addEventListener("click", async () => {
    retryCover.disabled = true;
    try {
      await request(`/api/tracks/${track.id}/cover`, {});
      notice.textContent = `Cover requested for ${track.title}.`;
    } catch (error) {
      notice.textContent = error.message;
    }
    await syncAfterMutation();
  });
  detail.append(retryCover);
  const failedMusic = musicJob?.state === "failed";
  if (failedMusic && musicJob?.error?.retryable) {
    // Resume continues polling/downloading the SAME class-service task; it never
    // submits a new generation request. Generate new instrumental is the
    // explicit path to start a brand-new task.
    const resume = node("button", "Resume check");
    resume.type = "button";
    resume.disabled = !musicConfigured;
    resume.addEventListener("click", async () => {
      resume.disabled = true;
      try {
        await request(`/api/tracks/${track.id}/music/resume?from=${musicJob.id}`, {});
        notice.textContent = `Resumed the previous generation check for ${track.title}. No new music request was submitted.`;
      } catch (error) {
        notice.textContent = error.message;
      }
      await syncAfterMutation();
    });
    detail.append(resume);
  }
  const retryMusic = node("button", musicActive ? "Generating…" : (track.audio || failedMusic) ? "Generate new instrumental" : "Generate instrumental");
  retryMusic.type = "button";
  retryMusic.disabled = musicActive || !musicConfigured;
  retryMusic.addEventListener("click", async () => {
    retryMusic.disabled = true;
    try {
      await request(`/api/tracks/${track.id}/music`, {});
      notice.textContent = `Instrumental requested for ${track.title}.`;
    } catch (error) {
      notice.textContent = error.message;
    }
    await syncAfterMutation();
  });
  detail.append(retryMusic);
  card.append(picture, detail);
  return card;
}

function renderLibrary(session) {
  document.querySelector("#track-count").textContent = `${session.tracks.length} tracks`;
  document.querySelector("#empty-library").hidden = session.tracks.length > 0;
  const library = document.querySelector("#tracks");
  const seen = new Set();
  for (const track of session.tracks) {
    seen.add(track.id);
    const input = trackCardInput(track, session.jobs);
    if (previousTracks.get(track.id) === input) continue;
    previousTracks.set(track.id, input);
    const card = buildTrackCard(track, session.jobs);
    const existing = library.querySelector(`[data-track-id="${track.id}"]`);
    if (existing) {
      const audio = existing.querySelector("audio");
      const saved = audio && !audio.paused ? {time: audio.currentTime} : null;
      existing.replaceWith(card);
      restoreAudio(card, saved);
    } else {
      library.append(card);
    }
  }
  for (const existing of [...library.querySelectorAll(".track")]) {
    if (!seen.has(existing.dataset.trackId)) {
      previousTracks.delete(existing.dataset.trackId);
      existing.remove();
    }
  }
}

function refreshConfigurationCopy() {
  if (artConfigured && musicConfigured) {
    createButton.textContent = "Create song & generate instrumental";
    document.querySelector("#cover-help").textContent = "Each request generates original instrumental music and matching cover art from the song title, style, mood and duration. Songs stay in this browser session.";
    return;
  }
  if (artConfigured) {
    createButton.textContent = "Create song draft & cover";
    document.querySelector("#cover-help").textContent = "Covers are ready. Add the music service to the server’s .env and restart the app to generate instrumentals.";
    return;
  }
  createButton.textContent = "Create song & generate instrumental";
  document.querySelector("#cover-help").textContent = musicConfigured
    ? "The music service is ready. Configure the art service for covers (needed to create tracks) and restart the app."
    : "Configure the server’s music service and art service, then restart the app to generate songs.";
}

async function load() {
  clearTimeout(polling);
  button.disabled = true;
  try {
    const [status, session] = await Promise.all([request("/api/status"), request("/api/session")]);
    const changedConfig = artConfigured !== status.cover_generation_available || musicConfigured !== status.music_generation_available;
    artConfigured = status.cover_generation_available;
    musicConfigured = status.music_generation_available;
    if (changedConfig) previousTracks.clear();
    const list = document.querySelector("#services");
    list.replaceChildren();
    for (const [role, label] of Object.entries(labels)) {
      const ready = status.services[role] === "configured";
      const item = node("li");
      item.append(node("span", label), node("strong", ready ? "Configured" : "Missing settings", ready ? "ready" : "missing"));
      list.append(item);
    }
    document.querySelector("#summary").textContent = status.configured ? "All four services are configured." : "The app is running. Some service settings are missing.";
    refreshConfigurationCopy();
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
  previousTracks.clear();
  return refresh();
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (submitting || !artConfigured) return;
  submitting = true;
  createButton.disabled = true;
  try {
    const values = new FormData(form);
    const job = await request("/api/tracks", {title: values.get("title"), settings: {
      style: values.get("style"), mood: values.get("mood"),
      duration_seconds: Number(values.get("duration")), mode: "instrumental"
    }});
    // The returned art job carries the new track id; use it to start music on the same track.
    try {
      await request(`/api/tracks/${job.track_id}/music`, {});
      notice.textContent = "Song created. Generating its instrumental and matching cover…";
    } catch (error) {
      if (error.code === "not_configured") {
        notice.textContent = "Song draft and cover created. Instrumental generation needs the music service configured — add it to the server’s .env and restart the app.";
      } else {
        notice.textContent = `Song draft created, but the instrumental request failed: ${error.message}`;
      }
    }
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
