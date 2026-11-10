# Deploy: UI on Vercel, worker on Render (all free tiers)

```
Mac (Claude pipeline) ──adds jobs──▶ Redis (Redis Cloud free) ◀── Render web service: workers + publisher
                                                                     │ uploads clips/stills
Browser ──login──▶ Vercel (web/) ──reads snapshots──▶ Redis          ▼
                                  ──302 signed link──▶ Vercel Blob (private)
```
Secrets: EngineX `AUTH_KEY` lives only on Render. Vercel never sees it.

## 1. Redis (free)
Create a free database at redis.io/cloud (30 MB, TLS). Copy the URL as `rediss://default:PASSWORD@HOST:PORT`. Must be reachable from the internet, because Vercel, Render and your Mac all connect.

## 2. Vercel Blob + UI
1. Vercel dashboard → Storage → create a **Blob** store, **Private**. Copy its `BLOB_READ_WRITE_TOKEN`.
2. New Project → import this repo → **Root Directory: `web`**.
3. Environment variables (Production):
   - `UI_PASSWORD` a long passphrase
   - `COOKIE_SECRET` `openssl rand -hex 32`
   - `REDIS_URL` from step 1
   - `BLOB_READ_WRITE_TOKEN` from step 1
4. Deploy.

## 3. Render worker
New → **Web Service** (not Background Worker, which is paid) → this repo → Root Directory `queue`, Build `npm install`, Start `npm start`, Instance type **Free**.
Env vars: `REDIS_URL`, `BLOB_READ_WRITE_TOKEN`, `BASE_URL`, `AUTH_KEY` (the two from your local `.env`).
Then add a free UptimeRobot HTTP monitor on the Render URL every 5 min so it never sleeps.

## 4. Move the finished Dhanushkodi film up (once, from the Mac)
Put `REDIS_URL` and `BLOB_READ_WRITE_TOKEN` in `../.env`, then:
```
cd queue
node media.mjs push        # uploads existing clips and stills to Blob
node push_build.mjs --watch   # keeps the Build tab fresh (leave running while the pipeline runs)
```
Stop the local `dhanu_worker` / `dhshort_worker` so they don't compete with Render for the same queue.

## Daily use
- Queue jobs from the Mac as before (`node dhanu_add.mjs`); with `REDIS_URL` set they land on the shared Redis.
- `node media.mjs pull` brings what Render made back to the Mac for assembly.

## Known limits
- Free Render disk is wiped on restart. Files are safe in Blob; an in-flight step re-downloads from EngineX.
- Shots with a local `photo` path need that file on the worker, so upload it first. Painted-still shots work as they are.
- Login: 10 wrong passwords per IP per 15 min, then blocked. Cookie is HttpOnly, Secure, SameSite=Strict, 7 days.
