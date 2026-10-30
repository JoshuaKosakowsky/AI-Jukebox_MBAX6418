"use strict";
const labels = {text: "Lyrics & DJ text", art: "Cover artwork", music: "Music", speech: "DJ speech"};
const button = document.querySelector("#refresh");
const form = document.querySelector("#cover-form");
const createButton = document.querySelector("#create-cover");
const notice = document.querySelector("#cover-notice");
let artConfigured = false;
let musicConfigured = false;
let textConfigured = false;
let speechConfigured = false;
let submitting = false;
let polling;
// DJ queue controller state: one persistent audio element, one timeline.
// djEpoch is bumped by every user action (play/pause/resume/skip); any async
// continuation from an older epoch bails, so late speech/music callbacks can
// never restart the wrong phase. Speech always precedes music; the single
// element plays at most one source at a time (no overlap by construction).
const djAudio = document.querySelector("#dj-audio");
let latestSession = null;
let djEpoch = 0;
let djHalted = false;
let djAdvanceInFlight = null;
let djPhase = "idle";
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

function trackCardInput(track, jobs, queued) {
  return JSON.stringify({track, jobs: jobs.filter(job => job.track_id === track.id), queued});
}

function buildTrackCard(track, jobs, queued) {
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
  const addQueue = node("button", queued ? "In DJ queue" : "Add to DJ queue");
  addQueue.type = "button";
  addQueue.disabled = !djReady() || !track.audio || queued;
  addQueue.addEventListener("click", async () => {
    addQueue.disabled = true;
    try {
      await request("/api/playback/queue", {track_id: track.id});
      notice.textContent = `${track.title} added to the DJ queue.`;
    } catch (error) {
      notice.textContent = error.message;
      addQueue.disabled = !djReady() || !track.audio || queued;
    }
    await syncAfterMutation();
  });
  detail.append(addQueue);
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
    const queued = session.playback.queue.includes(track.id);
    const input = trackCardInput(track, session.jobs, queued);
    if (previousTracks.get(track.id) === input) continue;
    previousTracks.set(track.id, input);
    const card = buildTrackCard(track, session.jobs, queued);
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
    const changedConfig = artConfigured !== status.cover_generation_available || musicConfigured !== status.music_generation_available || textConfigured !== status.lyrics_generation_available || speechConfigured !== (status.services?.speech === "configured");
    artConfigured = status.cover_generation_available;
    musicConfigured = status.music_generation_available;
    textConfigured = status.lyrics_generation_available;
    speechConfigured = status.services?.speech === "configured";
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
    renderDj(session);
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

// ---------------------------------------------------------------------------
// Default AI DJ: ONE persistent audio element, ONE persistent engine loop, and
// one monotonic token (djEpoch). Every user action bumps djEpoch and fires a
// 'dj-interrupt' on the element, which unblocks the engine's pending phase.
// The engine then re-reads the server state and plays exactly the right phase —
// a stale speech/music 'ended' callback can never restart the wrong audio
// because every continuation checks its captured epoch. Speech always precedes
// music on the SAME element, so the two can never overlap. Commentary is
// best-effort: missing speech (still generating or failed) just plays music.
// The engine NEVER POSTs start/advance on its own, so polling and reloads can
// never trigger generation or duplicates.
// ---------------------------------------------------------------------------

function djReady() {
  return textConfigured && speechConfigured;
}

function djSleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function djInterrupt() {
  djEpoch += 1;
  djAudio.dispatchEvent(new Event("dj-interrupt"));
}

function djStopLocal() {
  djAudio.pause();
  djAudio.onended = null;
  djAudio.onerror = null;
  try {
    djAudio.removeAttribute("src");
    djAudio.load();
  } catch {
    // Element may already be idle; nothing to abort.
  }
}

function djPlayOnce(epoch, url) {
  // Resolves when this source ends, errors, or the player is interrupted
  // (skip/pause/start/resume). The engine re-checks the epoch after every
  // await and abandons stale phases there.
  return new Promise((resolve) => {
    const finish = () => { if (epoch === djEpoch) resolve(); };
    const interrupt = () => resolve();
    djAudio.addEventListener("dj-interrupt", interrupt, {once: true});
    djAudio.onended = finish;
    djAudio.onerror = () => {
      if (epoch !== djEpoch) return;
      djAudio.onended = null;
      resolve();
    };
    if (djAudio.getAttribute("src") !== url) djAudio.src = url;
    // A transient play() rejection (navigation teardown during a reload,
    // media still buffering) must NOT be mistaken for the segment finishing:
    // resolving here lets the engine post the phase transition and advance
    // the whole queue in seconds while nothing was audible. Retry briefly.
    // Every scheduled retry re-checks its CAPTURED epoch (a pause/skip/start
    // may have advanced the epoch while keeping the element's src for
    // resume) and the element's src before touching the player.
    // A play-PERMISSION rejection (autoplay policy) is different: retrying
    // cannot succeed without a user gesture, so retries stop and the segment
    // stays pending — the queue does not advance over unplayed audio, and
    // any DJ control (pause/skip/resume) resumes/recovers it. Only genuine
    // non-permission rejections keep the bounded best-effort path.
    let attempts = 0;
    const startPlay = () => {
      if (epoch !== djEpoch) { resolve(); return; }  // stale retry: abort
      if (djAudio.getAttribute("src") !== url) { resolve(); return; }
      djAudio.play().catch((err) => {
        if (epoch !== djEpoch) return;
        if (err && err.name === "NotAllowedError") {
          // Autoplay permission: wait for a user action instead of treating
          // the segment as over; the next DJ control interrupts and recovers.
          const status = document.querySelector("#dj-status");
          if (status) status.textContent =
            "Audio playback is blocked by this browser — use a DJ control to continue.";
          return;
        }
        if (++attempts >= 6) {
          djAudio.onended = null;
          resolve();
          return;
        }
        setTimeout(startPlay, 350);
      });
    };
    startPlay();
  });
}

async function djAdvanceOnce(currentTrackId, automatic) {
  const prior = djAdvanceInFlight;
  if (prior && prior.automatic && prior.trackId === currentTrackId) {
    // An automatic advance past THIS track is already on the wire (its
    // music just ended); a user Skip for the same track is the SAME
    // transition — coalesce so a single Skip advances at most once.
    return prior.promise;
  }
  const promise = (async () => {
    try {
      // Any earlier advance must land first, so server-side arrival order
      // matches intent order even though fetches use separate connections.
      // This await sits INSIDE the try: if the prior advance REJECTS, this
      // promise still reaches its finally and clears the in-flight slot —
      // otherwise the slot stays occupied by this rejected promise and
      // every subsequent advance rejects forever (poisoned).
      if (prior) await prior.promise;
      const response = await request("/api/playback/advance", {});
      await syncAfterMutation();
      return response.state;
    } finally {
      // Clear INSIDE the promise: a separate chained finally call would be
      // an orphan whose rejection nobody observes (unhandled rejection any
      // time the advance fails — e.g. a straggler advance after the queue
      // already ended).
      if (djAdvanceInFlight && djAdvanceInFlight.promise === promise) {
        djAdvanceInFlight = null;
      }
    }
  })();
  djAdvanceInFlight = {promise, trackId: currentTrackId, automatic};
  return promise;
}

// User intents (Play/Pause/Resume/Skip) travel through one FIFO so the server
// applies them in the exact order the user issued them; otherwise separate
// connections could deliver a later action first.
let djUserChain = Promise.resolve();

function djUserQueue(task) {
  const next = djUserChain.then(task);
  djUserChain = next.catch(() => {});
  return next;
}

async function djEngine() {
  while (true) {
    try {
      // User actions set djHalted so the engine never re-enters playback in the
      // window between the interrupt and the server's acknowledgement of the
      // new state (pause/skip), which previously resumed playback mid-pause.
      if (djHalted) {
        await djSleep(100);
        continue;
      }
      const session = latestSession;
      const pb = session && session.playback;
      if (!pb || pb.state === "idle" || pb.state === "paused") {
        await djSleep(250);
        continue;
      }
      const epoch = djEpoch;
      const track = session.tracks.find(item => item.id === pb.current_track_id);
      if (!track) {
        await djSleep(250);
        continue;
      }
      if (!track.audio) {
        // Current entry is not playable (still generating): move along.
        await djAdvanceOnce(track.id, true);
        continue;
      }
      const speech = track.speech;
      if (pb.state === "speaking" && speech) {
        djPhase = "speaking";
        await djPlayOnce(epoch, speech.url);
        if (epoch === djEpoch) {
          djPhase = "playing";
          // Refresh the snapshot: polling may have stopped (no jobs pending)
          // and the engine must never replay speech against stale state.
          await request("/api/playback/phase", {phase: "playing", track_id: track.id}).catch(() => {});
          await syncAfterMutation();
        }
        continue;
      }
      if (pb.state === "speaking" && !track.speech) {
        const speechJob = session.jobs
          .filter(job => job.track_id === track.id && job.kind === "speech").at(-1);
        if (speechJob && ["queued", "running"].includes(speechJob.state)) {
          // Introduction is still being written/voiced; wait for a poll.
          await djSleep(250);
          continue;
        }
        if (epoch === djEpoch) {
          // No introduction will come; record that music actually started.
          await request("/api/playback/phase", {phase: "playing", track_id: track.id}).catch(() => {});
          await syncAfterMutation();
        }
      }
      djPhase = "playing";
      await djPlayOnce(epoch, track.audio.url);
      if (epoch === djEpoch) {
        await djAdvanceOnce(track.id, true);
      }
    } catch (error) {
      // A transient network/409 failure must never kill the timeline loop;
      // surface it and keep observing the server state.
      document.querySelector("#dj-status").textContent = error.message;
      await djSleep(250);
    }
  }
}
djEngine();

async function djStart() {
  djHalted = false;
  djInterrupt();
  djStopLocal();
  djPhase = "speaking";
  try {
    await djUserQueue(async () => {
      await request("/api/playback/start", {});
      await syncAfterMutation();
    });
  } catch (error) {
    document.querySelector("#dj-status").textContent = error.message;
  }
}

async function djPause() {
  const phase = djPhase === "playing" ? "playing" : "speaking";
  const trackId = latestSession && latestSession.playback.current_track_id;
  djHalted = true;
  djInterrupt();
  // Keep the element's src and position so Resume continues where it stopped;
  // only the timeline and its handlers are frozen.
  djAudio.pause();
  djAudio.onended = null;
  djAudio.onerror = null;
  djPhase = "idle";
  try {
    await djUserQueue(async () => {
      await request("/api/playback/pause", {phase, track_id: trackId});
      await syncAfterMutation();
    });
  } catch (error) {
    // A failed pause (network error) must not leave the controller halted.
    djHalted = false;
    document.querySelector("#dj-status").textContent = error.message;
    await syncAfterMutation();
  }
}

async function djResume() {
  djHalted = false;
  djInterrupt();
  djPhase = "idle";
  try {
    await djUserQueue(async () => {
      await request("/api/playback/resume", {});
      await syncAfterMutation();
    });
  } catch (error) {
    document.querySelector("#dj-status").textContent = error.message;
  }
}

async function djSkip() {
  if (!latestSession || latestSession.playback.state === "idle") return;
  const current = latestSession.playback.current_track_id
    ? latestSession.tracks.find(t => t.id === latestSession.playback.current_track_id) : null;
  djHalted = true;
  djInterrupt();
  djStopLocal();
  djPhase = "speaking";
  try {
    const state = await djUserQueue(async () =>
      djAdvanceOnce(current ? current.id : null, false));
    if (state === "idle") {
      djStatusIdleDone();
    }
    // The advance landed; the engine may resume watching the new state.
    djHalted = false;
  } catch (error) {
    djPhase = "idle";
    djHalted = false;
    document.querySelector("#dj-status").textContent = error.message;
    await syncAfterMutation();
  }
}

function djStatusIdleDone() {
  djPhase = "idle";
  const status = document.querySelector("#dj-status");
  status.textContent = "Queue finished. Press Play to hear it again.";
}

function renderDj(session) {
  latestSession = session;
  const pb = session.playback;
  const list = document.querySelector("#dj-queue");
  list.replaceChildren();
  if (pb.queue.length === 0) {
    list.append(node("li", "Queue is empty"));
  }
  session.tracks.forEach(track => {
    const position = pb.queue.indexOf(track.id);
    if (position < 0) return;
    const item = node("li", `${position + 1}. ${track.title}`);
    if (position === pb.index && pb.state !== "idle") {
      item.className = "current";
    }
    list.append(item);
  });
  const status = document.querySelector("#dj-status");
  const play = document.querySelector("#dj-play");
  const pause = document.querySelector("#dj-pause");
  const resume = document.querySelector("#dj-resume");
  const skip = document.querySelector("#dj-skip");
  const available = djReady();
  play.disabled = !available || pb.queue.length === 0 || pb.state !== "idle";
  pause.disabled = !(pb.state === "speaking" || pb.state === "playing");
  resume.disabled = pb.state !== "paused";
  skip.disabled = pb.state === "idle" || !available;
  const current = pb.current_track_id
    ? session.tracks.find(track => track.id === pb.current_track_id) : null;
  if (!available) {
    status.textContent = "DJ commentary needs the Qwen text and Chatterbox speech services configured.";
  } else if (pb.state === "idle") {
    status.textContent = pb.queue.length
      ? `Ready. ${pb.queue.length} song${pb.queue.length === 1 ? "" : "s"} queued — press Play.`
      : "Add playable songs from your library to the queue, then press Play.";
  } else if (pb.state === "paused") {
    status.textContent = `Paused during ${pb.paused_from === "speaking" ? "DJ speech" : "music"}`
      + (current ? ` (${current.title})` : "") + ".";
  } else if (pb.state === "speaking") {
    const speechJob = current && session.jobs
      .filter(job => job.track_id === current.id && job.kind === "speech").at(-1);
    status.textContent = current && speechJob && ["queued", "running"].includes(speechJob.state)
      ? `DJ is writing the introduction for ${current.title}…`
      : `DJ is speaking about ${current.title}…`;
  } else {
    status.textContent = `Now playing ${current ? current.title : "…"}`;
  }
  // The persistent engine loop below picks up any active queue by itself on
  // the next tick — including right after a reload — so there is nothing to
  // restart here.
}

document.querySelector("#dj-play").addEventListener("click", djStart);
document.querySelector("#dj-pause").addEventListener("click", djPause);
document.querySelector("#dj-resume").addEventListener("click", djResume);
document.querySelector("#dj-skip").addEventListener("click", djSkip);
