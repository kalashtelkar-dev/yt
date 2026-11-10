// Shared by the API routes (underscore = not a route). Env: UI_PASSWORD, COOKIE_SECRET, REDIS_URL, BLOB_READ_WRITE_TOKEN. Never the EngineX key.
import crypto from 'node:crypto'; import Redis from 'ioredis';
const sha = s => crypto.createHash('sha256').update(String(s)).digest();
export const same = (a, b) => crypto.timingSafeEqual(sha(a), sha(b)); // equal length digests, constant time
const sign = exp => crypto.createHmac('sha256', process.env.COOKIE_SECRET).update(String(exp)).digest('base64url');
export const mint = (days = 7) => { const exp = Date.now() + days * 864e5; return `${exp}.${sign(exp)}`; };
export const authed = req => { const m = /(?:^|;\s*)s=(\d+)\.([\w-]+)/.exec(req.headers.cookie || ''); return !!m && +m[1] > Date.now() && same(m[2], sign(m[1])); };
export const guard = (req, res) => authed(req) || (res.status(401).json({ error: 'login' }), false);
let r; export const redis = () => r ??= new Redis(process.env.REDIS_URL, { maxRetriesPerRequest: 2, connectTimeout: 5000 });
