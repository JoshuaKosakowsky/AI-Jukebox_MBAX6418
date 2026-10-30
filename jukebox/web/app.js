"use strict";
const labels = {text: "Lyrics & DJ text", art: "Cover artwork", music: "Music", speech: "DJ speech"};
const button = document.querySelector("#refresh");
const form = document.querySelector("#cover-form");
const createButton = document.querySelector("#create-cover");
const notice = document.querySelector("#cover-notice");
let artConfigured = false;
let musicConfigured = false;
let textConfigured = false;
let submitting = false;
let polling;
// Auto-chained vocal steps: a lyrics job id lands here once its success has
// already started the follow-up music request. Seeded from the first snapshot
// so a page reload NEVER auto-submits music (README: reloads do not generate).
const autoChained = new Set();
let seeded = false;
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

function musicStatusText(job, hasAudio, vocal) {
  const kind = vocal ? "Vocal" : "Instrumental";
  if (!job) return hasAudio ? `${kind} track ready` : `No ${kind.toLowerCase()} yet`;
  if (job.state === "failed") return job.error?.message || `${kind} generation failed.`;
  if (job.state === "succeeded") return `${kind} track ready`;
  if (job.progress >= 0.8) return "Downloading and validating audio…";
  if (vocal && job.progress >= 0.35) return "Generating vocal music…";
  if (job.progress >= 0.35) return "Generating instrumental music…";
  if (job.progress > 0) return "Submitting music request…";
  return "Waiting to start…";
}

function trackCardInput(track, jobs) {
  return JSON.stringify({track, jobs: jobs.filter(job => job.track_id === track.id)});
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
  const vocal = track.settings.mode === "vocal";
  const musicJobs = jobs.filter(job => job.track_id === track.id && job.kind === "music");
  const musicJob = musicJobs.at(-1);
  const musicActive = musicJob && ["queued", "running"].includes(musicJob.state);
  const musicStatus = node("p", musicStatusText(musicJob, Boolean(track.audio), vocal), "cover-status");
  musicStatus.setAttribute("role", "status");
  detail.append(musicStatus);
  const textJobs = jobs.filter(job => job.track_id === track.id && job.kind === "text");
  const lyricsJob = textJobs.at(-1);
  const textActive = lyricsJob && ["queued", "running"].includes(lyricsJob.state);
  if (vocal) {
    const lyricsStatus = node("p", textActive ? "Writing lyrics…" : lyricsJob?.state === "failed" ? lyricsJob.error.message : track.lyrics ? "AI lyrics ready" : "No lyrics yet", "cover-status");
    lyricsStatus.setAttribute("role", "status");
    detail.append(lyricsStatus);
    if (track.lyrics) {
      const lyricsBlock = node("details", undefined, "lyrics");
      lyricsBlock.append(node("summary", "Lyrics"));
      lyricsBlock.append(node("pre", track.lyrics));
      detail.append(lyricsBlock);
    }
    const retryLyrics = node("button", textActive ? "Generating…" : lyricsJob?.state === "failed" ? "Retry lyrics" : track.lyrics ? "Generate new lyrics" : "Generate lyrics");
    retryLyrics.type = "button";
    retryLyrics.disabled = textActive || !textConfigured;
    retryLyrics.addEventListener("click", async () => {
      retryLyrics.disabled = true;
      const previousLabel = retryLyrics.textContent;
      retryLyrics.textContent = "Requesting…";
      try {
        await request(`/api/tracks/${track.id}/lyrics`, {});
        notice.textContent = `Lyrics requested for ${track.title}.`;
      } catch (error) {
        // A rejected request (429 while another lyrics job holds the single
        // text slot, 502 not configured, ...) creates NO job, so the next
        // refresh sees identical card data and would skip rebuilding this
        // card — the disabled state set above would persist until reload.
        // Restore the button explicitly so the control stays usable.
        retryLyrics.disabled = !textConfigured;
        retryLyrics.textContent = previousLabel;
        notice.textContent = error.message;
      }
      await syncAfterMutation();
    });
    detail.append(retryLyrics);
  }
  if (track.audio) {
    const audio = node("audio");
    audio.controls = true;
    audio.preload = "none";
    audio.src = track.audio.url;
    audio.setAttribute("aria-label", `Play ${track.title}`);
    detail.append(audio);
  } else {
    detail.append(node("p", vocal ? "Song draft · lyrics and vocal generation pending." : "Song draft · instrumental generation pending.", "note"));
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
      // A rejected POST creates no job, so the unchanged card may not redraw.
      retryCover.disabled = artActive || !artConfigured;
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
        // A rejected POST creates no job, so the unchanged card may not redraw.
        resume.disabled = !musicConfigured;
        notice.textContent = error.message;
      }
      await syncAfterMutation();
    });
    detail.append(resume);
  }
  const retryMusic = node("button", musicActive ? "Generating…" : (track.audio || failedMusic) ? (vocal ? "Generate new vocal song" : "Generate new instrumental") : (vocal ? "Generate vocal song" : "Generate instrumental"));
  retryMusic.type = "button";
  retryMusic.disabled = musicActive || !musicConfigured;
  retryMusic.addEventListener("click", async () => {
    retryMusic.disabled = true;
    try {
      await request(`/api/tracks/${track.id}/music`, {});
      notice.textContent = `Instrumental requested for ${track.title}.`;
    } catch (error) {
      // A rejected POST creates no job, so the unchanged card may not redraw.
      retryMusic.disabled = musicActive || !musicConfigured;
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
      const oldAudio = existing.querySelector("audio");
      const newAudio = card.querySelector("audio");
      if (oldAudio && newAudio && track.audio && oldAudio.getAttribute("src") === track.audio.url) {
        // Same underlying media: move the original element into the rebuilt card
        // so playback continues without interruption (the node never leaves the
        // document). A deliberate media replacement below instead gets a fresh
        // stopped element, which is never auto-played here.
        newAudio.replaceWith(oldAudio);
      }
      existing.replaceWith(card);
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

function vocalMode() {
  return new FormData(form).get("mode") === "vocal";
}

function refreshConfigurationCopy() {
  const vocal = vocalMode();
  if (artConfigured && musicConfigured) {
    createButton.textContent = vocal ? "Create vocal song & generate" : "Create song & generate instrumental";
    document.querySelector("#cover-help").textContent = vocal
      ? (textConfigured
          ? "Generates original AI lyrics (Qwen), a sung vocal track (ACE-Step) and matching cover art (FLUX) from the song title, style, mood and duration. Songs stay in this browser session."
          : "Vocal songs need the text service configured for AI lyrics — add it to the server’s .env and restart the app. Covers and instrumentals are already ready.")
      : "Each request generates original instrumental music and matching cover art from the song title, style, mood and duration. Songs stay in this browser session.";
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
    const changedConfig = artConfigured !== status.cover_generation_available || musicConfigured !== status.music_generation_available || textConfigured !== status.lyrics_generation_available;
    artConfigured = status.cover_generation_available;
    musicConfigured = status.music_generation_available;
    textConfigured = status.lyrics_generation_available;
    if (changedConfig) previousTracks.clear();
    if (!seeded) {
      // First snapshot: EVERY text job that is not terminal-failed (pending
      // or succeeded) is treated as already chained, so a page reload — even
      // mid-chain — never starts a new music submission. Only a lyrics job
      // observed reaching success WHILE this document is open can start the
      // vocal request; a reloaded vocal draft waits for a deliberate button.
      for (const job of session.jobs) {
        if (job.kind === "text" && job.state !== "failed") autoChained.add(job.id);
      }
      seeded = true;
    }
    // One-click vocal chain: when a lyrics job observed ALIVE reaches success,
    // start the vocal music job on the same track exactly once. Never after a
    // reload (seeded above) and never when a music job already exists, so a
    // failed vocal request stays a deliberate button click away.
    for (const track of session.tracks) {
      if (track.settings.mode !== "vocal" || track.audio) continue;
      const lyricsJob = session.jobs.filter(job => job.track_id === track.id && job.kind === "text").at(-1);
      if (!lyricsJob || lyricsJob.state !== "succeeded" || autoChained.has(lyricsJob.id)) continue;
      if (session.jobs.some(job => job.track_id === track.id && job.kind === "music")) continue;
      autoChained.add(lyricsJob.id);
      if (!musicConfigured) {
        notice.textContent = `Lyrics ready for ${track.title} — the music service is not configured, so the vocal track was not requested. Add it to the server’s .env, restart, then use Generate vocal song.`;
        continue;
      }
      request(`/api/tracks/${track.id}/music`, {}).then(async () => {
        notice.textContent = `Lyrics ready — generating the vocal track for ${track.title}…`;
        await syncAfterMutation();
      }).catch(error => { notice.textContent = error.message; });
    }
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
  // Deliberately do NOT clear the per-track cache: the next snapshot diff
  // rebuilds only cards whose own data changed, leaving unrelated players
  // (and their audio elements) untouched.
  return refresh();
}

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (submitting || !artConfigured) return;
  submitting = true;
  createButton.disabled = true;
  try {
    const values = new FormData(form);
    const mode = values.get("mode") === "vocal" ? "vocal" : "instrumental";
    const job = await request("/api/tracks", {title: values.get("title"), settings: {
      style: values.get("style"), mood: values.get("mood"),
      duration_seconds: Number(values.get("duration")), mode
    }});
    // The returned art job carries the new track id; the follow-up step differs
    // by mode: vocals chain lyrics first (the poll loop starts the vocal music
    // job when the lyrics succeed), instrumentals start music immediately.
    if (mode === "vocal") {
      try {
        await request(`/api/tracks/${job.track_id}/lyrics`, {});
        notice.textContent = "Song created. Writing lyrics, then generating its vocal track and cover…";
      } catch (error) {
        if (error.code === "not_configured") {
          notice.textContent = "Song draft and cover created. AI lyrics need the text service configured — add it to the server’s .env and restart the app.";
        } else {
          notice.textContent = `Song draft created, but the lyrics request failed: ${error.message}`;
        }
      }
    } else {
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
    }
    form.reset();
    refreshConfigurationCopy();
  } catch (error) {
    notice.textContent = error.message;
  } finally {
    submitting = false;
    await syncAfterMutation();
  }
});
for (const input of form.querySelectorAll('input[name="mode"]')) {
  input.addEventListener("change", refreshConfigurationCopy);
}
button.addEventListener("click", refresh);
refresh();
