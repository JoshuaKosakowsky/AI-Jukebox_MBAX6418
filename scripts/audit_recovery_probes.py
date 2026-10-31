"""Offline exploratory probes; does not modify source or use class credentials."""
from pathlib import Path
import json
import sys
from audit_fault_harness import Wire, app_context, load_source

load_source(sys.argv[1])
from fastapi.testclient import TestClient
from jukebox.sessions import SESSION_COOKIE

BODY = {"title": "OFFLINE recovery probe", "settings": {
    "style": "Offline fixture", "mood": "Audit", "duration_seconds": 10, "mode": "instrumental"}}
results = []


def start(client):
    response = client.post("/api/tracks", json=BODY)
    assert response.status_code == 202
    return response.json()["track_id"]


def latest(client):
    return client.get("/api/session").json()["jobs"][-1]


def resume(client, track, job):
    return client.post(f"/api/tracks/{track}/music/resume?from={job['id']}", json={})


for options, stage, failures in [({"poll_timeouts": 2}, "poll", 2),
                                  ({"download_timeouts": 1}, "download", 1)]:
    wire = Wire(options)
    with app_context(wire) as app, TestClient(app, base_url="http://localhost") as client:
        track = start(client)
        assert client.post(f"/api/tracks/{track}/music", json={}).status_code == 202
        for attempt in range(failures):
            job = latest(client)
            assert job["state"] == "failed" and job["error"]["retryable"]
            assert resume(client, track, job).status_code == 202
        assert latest(client)["state"] == "succeeded"
        session = app.state.sessions.sessions[client.cookies.get(SESSION_COOKIE)]
        assert not session.active and not session.tickets
        snapshot = client.get("/api/session").text
        assert "offline-private" not in snapshot and "synthetic-marker" not in snapshot
        assert wire.counts["/release_task"] == 1
        results.append({"case": f"{stage}_timeout_resume", "result": "PASS", "submissions": 1,
                        "failed_attempts": failures, "counts": dict(wire.counts), "private_state_cleaned": True})

wire = Wire({"submit_timeouts": 1})
with app_context(wire) as app, TestClient(app, base_url="http://localhost") as client:
    track = start(client)
    client.post(f"/api/tracks/{track}/music", json={})
    before = client.get("/api/session").json()
    response = resume(client, track, latest(client))
    assert response.status_code == 409 and "never confirmed" in response.text
    assert client.get("/api/session").json() == before
    assert wire.counts["/release_task"] == 1
    assert client.post(f"/api/tracks/{track}/music", json={}).status_code == 202
    assert latest(client)["state"] == "succeeded" and wire.counts["/release_task"] == 2
    results.append({"case": "uncertain_submit", "result": "PASS", "resume_status": 409,
                    "rejection_side_effects": False, "submissions_after_explicit_new_request": 2})

wire = Wire()
with app_context(wire) as app, TestClient(app, base_url="http://localhost") as client:
    track = start(client)
    client.post(f"/api/tracks/{track}/music", json={})
    old = client.get("/api/session").json()["tracks"][0]
    wire.options = {"bad_audio": True}
    client.post(f"/api/tracks/{track}/music", json={})
    assert latest(client)["state"] == "failed" and latest(client)["error"]["code"] == "invalid_response"
    assert client.get("/api/session").json()["tracks"][0] == old
    wire.options = {"cover_fail": True}
    client.post(f"/api/tracks/{track}/cover", json={})
    assert latest(client)["state"] == "failed"
    assert client.get("/api/session").json()["tracks"][0] == old
    wire.options = {}
    client.post(f"/api/tracks/{track}/cover", json={})
    assert latest(client)["state"] == "succeeded"
    new = client.get("/api/session").json()["tracks"][0]
    assert new["audio"] == old["audio"] and new["cover"] != old["cover"]
    assert client.get(old["audio"]["url"]).status_code == 200
    results.append({"case": "failed_replacements_preserve_assets", "result": "PASS",
                    "invalid_audio_keeps_track": True, "cover_503_keeps_track": True,
                    "explicit_cover_retry_succeeds": True, "audio_still_available": True})

wire = Wire({"foreign_download": True})
with app_context(wire) as app, TestClient(app, base_url="http://localhost") as client:
    track = start(client)
    client.post(f"/api/tracks/{track}/music", json={})
    assert latest(client)["state"] == "failed" and latest(client)["error"]["code"] == "invalid_response"
    assert wire.counts["/v1/audio"] == 0
    results.append({"case": "foreign_download_rejected_before_request", "result": "PASS", "downloads": 0})

wire = Wire()
with app_context(wire) as app, TestClient(app, base_url="http://localhost") as client:
    a, b, target = [start(client) for _ in range(3)]
    store = app.state.sessions
    session = store.sessions[client.cookies.get(SESSION_COOKIE)]
    store.queue_music(session, next(key for key in session.tracks if str(key) == a))
    store.queue_music(session, next(key for key in session.tracks if str(key) == b))
    before = client.get("/api/session").json()
    rejection = client.post(f"/api/tracks/{target}/music", json={})
    assert rejection.status_code == 429 and client.get("/api/session").json() == before
    with store.lock:
        session.active.clear()
    assert client.post(f"/api/tracks/{target}/music", json={}).status_code == 202
    assert latest(client)["state"] == "succeeded"
    results.append({"case": "capacity_rejection_then_api_retry", "result": "PASS",
                    "busy_status": 429, "rejection_side_effects": False, "retry_after_capacity_freed": 202})

wire = Wire({"poll_timeouts": 1})
with app_context(wire) as app, TestClient(app, base_url="http://localhost") as owner, \
     TestClient(app, base_url="http://localhost") as other:
    track = start(owner)
    owner.post(f"/api/tracks/{track}/music", json={})
    job = latest(owner)
    before = other.get("/api/session").json()
    assert resume(other, track, job).status_code == 404
    assert other.get("/api/session").json() == before
    snapshot = owner.get("/api/session").json()
    assert other.get(snapshot["tracks"][0]["cover"]["url"]).status_code == 404
    assert owner.post(f"/api/tracks/{track}/music", json={}, headers={"origin": "http://outside.invalid"}).status_code == 403
    for path in ["/.env", "/.git/config", "/class-endpoints.txt", "/static/../.env"]:
        assert owner.get(path).status_code == 404
    assert "offline-private" not in owner.get("/api/session").text
    results.append({"case": "session_and_public_file_boundaries", "result": "PASS",
                    "foreign_resume_and_media": 404, "cross_origin_post": 403, "private_files": 404})

record = {"reference_base_sha": "7b9dd2b2702d7280a231cdcbfbd1afad136f3f56", "mode": "offline MockTransport exploratory probes",
          "real_provider_requests": 0, "cases": results}
output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("results/raw/a3-08-backend-results.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(record, indent=2)+"\n", encoding="utf-8")
print(json.dumps(record, indent=2))
