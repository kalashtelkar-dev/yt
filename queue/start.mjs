// Render/Railway start command: workers + publisher in one container; any that exits is restarted.
import { spawn } from 'node:child_process'; import http from 'node:http';
// Render's free tier only has web services, which need an open port; ping it every 5 min (UptimeRobot) so it never sleeps.
http.createServer((q, r) => r.end('ok')).listen(process.env.PORT || 3000);
for (const f of ['dhanu_worker.mjs', 'dhshort_worker.mjs', 'publish.mjs']) { const run = () => spawn('node', [f], { stdio: 'inherit' }).on('exit', c => { console.log(f, 'exited', c); setTimeout(run, 5000); }); run(); }
