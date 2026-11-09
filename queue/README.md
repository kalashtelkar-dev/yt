# Image-to-video queue (BullMQ + Redis)

Runs outside Claude, so it uses no Claude credits. Reads `BASE_URL` and `AUTH_KEY` from `../.env` (the REST API is the origin of BASE_URL).

1. Redis: `brew services start redis`
2. Worker (leave running): `node worker.mjs` — submits to EngineX, polls every 30 s, saves `../ayodhya_film/clips/<shot>.mp4`. Retries 3x. Concurrency 4 (`CONCURRENCY=n` to change).
3. Add jobs: `node add.mjs shots.json 4` queues the next 4 shots not yet queued or downloaded. Omit the number for all.
4. Check: `node status.mjs`, or `tail -f worker.log`.

`shots.json` entries: `{shot, image, idea, jobId?}`. A `jobId` means already submitted, so the worker only polls and downloads (no new generation). Re-running add is safe; finished clips are skipped.
5. UI: `node ui.mjs` then open http://localhost:3939 (progress bar, per-shot status, play finished clips).
