// Render/Railway start command: workers + publisher in one container; any that exits is restarted.
import { spawn } from 'node:child_process'; import http from 'node:http';
// Render's free tier only has web services, which need an open port, and they sleep after 15 min without inbound traffic.
// So the service pings its own public URL every 10 min (RENDER_EXTERNAL_URL is set by Render); that counts as inbound traffic.
if (process.env.RENDER_EXTERNAL_URL) setInterval(() => fetch(process.env.RENDER_EXTERNAL_URL).catch(e => console.log('self-ping failed', e.message)), 10 * 60e3);
http.createServer((q, r) => r.end('ok')).listen(process.env.PORT || 3000);
for (const f of ['dhanu_worker.mjs', 'dhshort_worker.mjs', 'publish.mjs']) { const run = () => spawn('node', [f], { stdio: 'inherit' }).on('exit', c => { console.log(f, 'exited', c); setTimeout(run, 5000); }); run(); }
