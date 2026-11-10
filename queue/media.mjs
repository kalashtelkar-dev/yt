// node media.mjs push  -> upload local Dhanushkodi stills/clips that Blob does not have yet (run once for the finished film)
// node media.mjs pull  -> download Blob stills/clips that are missing locally (so assemble.py can use what the Railway worker made)
import fs from 'node:fs'; import path from 'node:path'; import { get } from '@vercel/blob'; import { toBlob, blobSet } from './blob.mjs';
const R = new URL('../dhanushkodi_film/', import.meta.url).pathname, DIRS = { dhanu: R, dhshort: R + 'dhanu_short/' }, have = await blobSet('');
for (const [k, base] of Object.entries(DIRS)) for (const d of ['clips', 'stills']) {
  if (process.argv[2] === 'push') for (const f of fs.existsSync(base + d) ? fs.readdirSync(base + d) : []) { const key = `${k}/${d}/${f}`; if (/\.(mp4|png|jpg)$/.test(f) && !have.has(key)) { await toBlob(base + d + '/' + f, key); console.log('up', key); } }
  else if (process.argv[2] === 'pull') for (const key of have) { if (!key.startsWith(`${k}/${d}/`)) continue; const f = base + d + '/' + path.basename(key); if (fs.existsSync(f)) continue;
    fs.mkdirSync(base + d, { recursive: true }); const b = await get(key, { access: 'private' }); fs.writeFileSync(f, Buffer.from(await new Response(b.stream).arrayBuffer())); console.log('down', key); }
}
